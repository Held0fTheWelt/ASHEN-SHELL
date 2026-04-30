# MVP5 Implementation Plan

**Status**: DRAFT - For Approval  
**Date**: 2026-04-30  
**Architecture Choices Finalized**:
- ✅ Block-Only (no legacy entry rendering)
- ✅ Modular (Option B: BlockRenderingOrchestrator + BlockRenderer + TypewriterEngine + Controls)
- ✅ HTTP + WebSocket (Initial load + Narrator streaming)
- ✅ Virtual Clock (deterministic test mode)
- ✅ Global Typewriter Config (via SiteSetting)

---

## Module Structure

```
frontend/static/
├── play_block_renderer.js          (NEW) — DOM rendering only
├── play_typewriter_engine.js       (NEW) — Virtual clock + delivery
├── play_controls.js                (NEW) — Skip/Reveal/Accessibility UI
├── play_blocks_orchestrator.js     (NEW) — State + orchestration
├── play_narrative_stream.js        (EXTEND) — Add block payloads to WS
├── play_shell.js                   (REPLACE) — Call orchestrator, NOT old renderer
├── style.css                       (EXTEND) — Block styles + accessibility
└── (remove old play_shell rendering code)
```

---

## Data Flow

### Initial HTTP Load
```
1. Frontend POST /api/v1/sessions/{id}/turns
   ↓
2. Backend returns {visible_scene_output: {blocks: [...]}, diagnostics: {...}}
   ↓
3. BlocksOrchestrator.loadTurn(response)
   - Sets: this.blocks = [block1, block2, block3]
   - Calls: BlockRenderer.render(block1), render(block2), render(block3)
   - Calls: TypewriterEngine.startDelivery(block1)
   ↓
4. DOM: 3 <div data-block-id="turn-X-block-Y"> with typewriter animating block1
```

### WebSocket Narrator Streaming (while block1 typing)
```
1. NarratorStreamListener receives narrator block (via play_narrative_stream.js)
   ↓
2. BlocksOrchestrator.appendNarratorBlock(block4)
   - Appends: this.blocks.push(block4)
   - Calls: BlockRenderer.render(block4)  [appends to DOM]
   - Queues: TypewriterEngine for block4 (after block1 completes)
   ↓
3. DOM: 4 <div>s, block1 typing, block4 queued
```

### Player Action: Skip Current Block
```
1. User clicks "Skip Current"
   ↓
2. SkipControl calls: BlocksOrchestrator.skipCurrentBlock()
   - Reads: this.blocks[this.currentBlockIndex]
   - Calls: TypewriterEngine.skipBlock(current_block_id)
   - Updates: this.currentBlockIndex++
   ↓
3. Block completes, Typewriter moves to next
```

---

## Module Responsibilities

### BlockRenderer
**File**: `frontend/static/play_block_renderer.js`

**Responsibility**: Pure HTML rendering (no state, no orchestration)

```javascript
class BlockRenderer {
  constructor(dom_root) {
    this.dom_root = dom_root;  // <div id="turn-transcript">
  }

  render(block) {
    // block = {id, block_type, text, actor_id, speaker_label, delivery: {...}}
    const div = document.createElement('div');
    div.setAttribute('data-block-id', block.id);
    div.setAttribute('data-block-type', block.block_type);
    if (block.actor_id) div.setAttribute('data-actor-id', block.actor_id);
    if (block.target_actor_id) div.setAttribute('data-target-actor-id', block.target_actor_id);
    
    div.className = `scene-block scene-block--${block.block_type}`;
    div.textContent = block.text;  // Will be animated by Typewriter
    
    this.dom_root.appendChild(div);
    return div;
  }

  getBlockElement(block_id) {
    return this.dom_root.querySelector(`[data-block-id="${block_id}"]`);
  }
}
```

**Tests**: `frontend/tests/test_block_renderer.js`
- `test_render_creates_div_with_data_attributes`
- `test_render_sets_block_type_class`
- `test_render_appends_to_dom_root`

---

### TypewriterEngine
**File**: `frontend/static/play_typewriter_engine.js`

**Responsibility**: Virtual clock + character-by-character delivery + test mode

```javascript
class VirtualClock {
  constructor(test_mode = false) {
    this.test_mode = test_mode;
    this.virtual_time = 0;  // ms
    this.listeners = [];
  }

  advanceBy(ms) {
    // TEST MODE: Advance virtual time
    // PROD MODE: should not be called
    if (!this.test_mode) throw new Error("advanceBy only in test mode");
    this.virtual_time += ms;
    this.listeners.forEach(cb => cb(this.virtual_time));
  }

  onTick(callback) {
    this.listeners.push(callback);
  }

  now() {
    return this.test_mode ? this.virtual_time : performance.now();
  }
}

class TypewriterEngine {
  constructor(test_mode = false) {
    this.clock = new VirtualClock(test_mode);
    this.queue = [];  // [{block_id, start_time, duration, ...}]
    this.current_block = null;
  }

  startDelivery(block) {
    // block.delivery = {mode: "typewriter", characters_per_second: 44, ...}
    const duration = (block.text.length / 44) * 1000;  // ms
    this.queue.push({
      block_id: block.id,
      text: block.text,
      start_time: this.clock.now(),
      duration: duration,
      visible_chars: 0
    });
    this._processQueue();
  }

  _processQueue() {
    if (this.queue.length === 0) return;
    this.current_block = this.queue[0];
    
    this.clock.onTick((time) => {
      const elapsed = time - this.current_block.start_time;
      const visible_chars = Math.min(
        Math.floor((elapsed / this.current_block.duration) * this.current_block.text.length),
        this.current_block.text.length
      );
      this.current_block.visible_chars = visible_chars;
      this._renderBlock();
    });
  }

  skipBlock(block_id) {
    // Complete current block, move to next
    if (this.current_block?.block_id === block_id) {
      this.current_block.visible_chars = this.current_block.text.length;
      this._renderBlock();
      this.queue.shift();
      this._processQueue();
    }
  }

  revealAll() {
    // Complete all queued blocks immediately
    for (let block of this.queue) {
      block.visible_chars = block.text.length;
    }
    this._renderBlock();
  }

  _renderBlock() {
    // Update DOM element with visible_chars
    const el = document.querySelector(`[data-block-id="${this.current_block.block_id}"]`);
    if (el) {
      el.textContent = this.current_block.text.substring(0, this.current_block.visible_chars);
    }
  }
}
```

**Tests**: `frontend/tests/test_typewriter_engine.js`
- `test_virtual_clock_advances_in_test_mode`
- `test_typewriter_renders_chars_progressively`
- `test_skip_current_completes_block`
- `test_reveal_all_shows_all_blocks`

---

### BlocksOrchestrator
**File**: `frontend/static/play_blocks_orchestrator.js`

**Responsibility**: Orchestrate HTTP + WebSocket + Typewriter + Controls

```javascript
class BlocksOrchestrator {
  constructor(renderer, typewriter, controls) {
    this.renderer = renderer;
    this.typewriter = typewriter;
    this.controls = controls;
    
    this.blocks = [];              // All blocks ever rendered
    this.currentBlockIndex = 0;    // Which block is being typed
    this.accessibility_mode = false;
  }

  // HTTP: Initial load
  loadTurn(http_response) {
    this.blocks = http_response.visible_scene_output.blocks;
    
    for (let block of this.blocks) {
      const el = this.renderer.render(block);
      if (!this.accessibility_mode) {
        this.typewriter.startDelivery(block);
      } else {
        el.textContent = block.text;  // Show all immediately
      }
    }
  }

  // WebSocket: Narrator streaming
  appendNarratorBlock(block) {
    this.blocks.push(block);
    const el = this.renderer.render(block);
    if (!this.accessibility_mode) {
      this.typewriter.startDelivery(block);
    } else {
      el.textContent = block.text;
    }
  }

  // Control: Skip current
  skipCurrentBlock() {
    if (this.currentBlockIndex < this.blocks.length) {
      const current = this.blocks[this.currentBlockIndex];
      this.typewriter.skipBlock(current.id);
      this.currentBlockIndex++;
    }
  }

  // Control: Reveal all
  revealAll() {
    this.typewriter.revealAll();
  }

  // Control: Toggle accessibility
  setAccessibilityMode(enabled) {
    this.accessibility_mode = enabled;
    if (enabled) {
      for (let block of this.blocks) {
        const el = this.renderer.getBlockElement(block.id);
        if (el) el.textContent = block.text;  // Show all
      }
    }
  }
}
```

**Tests**: `frontend/tests/test_blocks_orchestrator.js`
- `test_load_turn_initializes_blocks`
- `test_append_narrator_block_adds_to_state`
- `test_skip_current_increments_index`
- `test_accessibility_mode_disables_typewriter`

---

### Controls (Skip/Reveal/Accessibility)
**File**: `frontend/static/play_controls.js`

**Responsibility**: UI event handlers

```javascript
class PlayControls {
  constructor(orchestrator) {
    this.orchestrator = orchestrator;
    this.attachEventListeners();
  }

  attachEventListeners() {
    const skipBtn = document.getElementById('play-skip-current-btn');
    const revealBtn = document.getElementById('play-reveal-all-btn');
    const a11yCheckbox = document.getElementById('play-accessibility-mode');

    if (skipBtn) {
      skipBtn.addEventListener('click', () => this.orchestrator.skipCurrentBlock());
    }
    if (revealBtn) {
      revealBtn.addEventListener('click', () => this.orchestrator.revealAll());
    }
    if (a11yCheckbox) {
      a11yCheckbox.addEventListener('change', (e) => {
        this.orchestrator.setAccessibilityMode(e.target.checked);
      });
    }
  }
}
```

---

## Configuration: Typewriter Delivery (Admin Tool)

**Storage**: `backend/app/models/site_setting.py` — `SiteSetting` with key `frontend_typewriter_config`

**API Endpoint** (create or extend): `backend/app/api/v1/admin_settings_routes.py`

```python
@admin_bp.route('/frontend-config/typewriter', methods=['GET', 'PATCH'])
def typewriter_config():
    if request.method == 'GET':
        setting = SiteSetting.query.get('frontend_typewriter_config')
        if setting:
            return jsonify(json.loads(setting.value))
        return jsonify({
            "characters_per_second": 44,
            "pause_before_ms": 150,
            "pause_after_ms": 650,
            "skippable": True
        })
    
    if request.method == 'PATCH':
        data = request.get_json()
        setting = SiteSetting.query.get('frontend_typewriter_config')
        if not setting:
            setting = SiteSetting(key='frontend_typewriter_config')
            db.session.add(setting)
        setting.value = json.dumps(data)
        db.session.commit()
        return jsonify({"saved": True})
```

**Admin UI** (extend `administration-tool/static/manage_runtime_settings.js`):

```javascript
// Add section for Typewriter Config
async function loadTypewriterConfig() {
  const response = await fetch('/api/v1/admin/frontend-config/typewriter');
  const config = await response.json();
  document.getElementById('tw-chars-per-sec').value = config.characters_per_second;
  document.getElementById('tw-pause-before').value = config.pause_before_ms;
  document.getElementById('tw-pause-after').value = config.pause_after_ms;
  document.getElementById('tw-skippable').checked = config.skippable;
}

async function saveTypewriterConfig() {
  const payload = {
    characters_per_second: parseInt(document.getElementById('tw-chars-per-sec').value),
    pause_before_ms: parseInt(document.getElementById('tw-pause-before').value),
    pause_after_ms: parseInt(document.getElementById('tw-pause-after').value),
    skippable: document.getElementById('tw-skippable').checked
  };
  await fetch('/api/v1/admin/frontend-config/typewriter', {
    method: 'PATCH',
    body: JSON.stringify(payload)
  });
}
```

---

## Frontend Loading (play_shell.js entrypoint)

**File**: `frontend/static/play_shell.js` (rewritten)

```javascript
(function() {
  const shell = document.querySelector('.play-shell');
  if (!shell) return;

  // 1. Initialize modules
  const renderer = new BlockRenderer(document.getElementById('turn-transcript'));
  const typewriter = new TypewriterEngine(window.TEST_MODE || false);
  const orchestrator = new BlocksOrchestrator(renderer, typewriter);
  const controls = new PlayControls(orchestrator);

  // 2. Load initial turn (bootstrap)
  const bootstrapEl = document.getElementById('play-shell-bootstrap');
  if (bootstrapEl) {
    const bootstrap = JSON.parse(bootstrapEl.textContent || '{}');
    if (bootstrap.visible_scene_output?.blocks?.length) {
      orchestrator.loadTurn(bootstrap);
    }
  }

  // 3. Listen for new turns (form submit)
  const form = document.getElementById('play-execute-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('player-input');
      const response = await fetch(form.action, {
        method: 'POST',
        body: JSON.stringify({ player_input: input.value })
      });
      const data = await response.json();
      orchestrator.loadTurn(data);
      input.value = '';
    });
  }

  // 4. Listen for WebSocket narrator blocks
  // (via extended play_narrative_stream.js)
  window.addEventListener('narrator-block-received', (e) => {
    orchestrator.appendNarratorBlock(e.detail.block);
  });

  // Export for testing
  window.BlocksOrchestrator = orchestrator;
})();
```

---

## Tests Structure

```
frontend/tests/
├── test_block_renderer.js           (unit) — Pure DOM rendering
├── test_typewriter_engine.js        (unit) — Virtual clock + delivery
├── test_blocks_orchestrator.js      (unit) — State + orchestration
├── test_play_controls.js            (unit) — Event handlers
└── test_final_goc_e2e.py            (e2e) — Browser tests (Annette/Alain)
```

**JS Unit Tests**: Can run via pytest-node or similar

**Browser E2E Tests**: Playwright/Selenium
- `test_final_annette_e2e` — Create run as Annette, play turns, verify blocks render, trace collected
- `test_final_alain_e2e` — Same but as Alain

---

## Operational Wiring

| Item | File | Change |
|------|------|--------|
| Test runner | `tests/run_tests.py` | Add `--mvp5` flag, include JS + browser suites |
| Workflows | `.github/workflows/tests.yml` | Add JS test job + browser E2E job |
| TOML | `frontend/pyproject.toml` | Add JS test config, browser test config |
| Reports | `tests/reports/GOC_FINAL_E2E_ACCEPTANCE.md` | Create with final evidence |

---

## Stop Condition: MVP5 Complete When

1. ✅ BlockRenderer renders one DOM element per scene block
2. ✅ TypewriterEngine uses virtual clock (deterministic in tests)
3. ✅ BlocksOrchestrator merges HTTP + WebSocket blocks
4. ✅ Skip/Reveal controls work without runtime calls
5. ✅ Accessibility mode disables animation + shows all immediately
6. ✅ Typewriter config editable in Admin Tool (global, persisted in SiteSetting)
7. ✅ All JS unit tests pass
8. ✅ Annette and Alain final E2E runs complete with transcript + trace + Narrative Gov cross-check
9. ✅ Operational gate: docker-up.py, tests/run_tests.py, GitHub workflows all working
10. ✅ No legacy entry rendering; blocks only

---

## Question for You

**Passt dieser Plan so? Sollen wir so implementieren?**

Oder gibt es noch Punkte, die unklar sind oder anders sein sollen?
