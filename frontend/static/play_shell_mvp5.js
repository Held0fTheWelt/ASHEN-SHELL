/**
 * play_shell.js (MVP5 — Rewritten)
 *
 * Responsibility: Initialize modular frontend (BlockRenderer, TypewriterEngine,
 * BlocksOrchestrator, PlayControls) and coordinate HTTP + WebSocket flows.
 */

(function () {
  const shell = document.querySelector('.play-shell');
  if (!shell) return;

  // Initialize modules
  const transcriptEl = document.getElementById('turn-transcript');
  if (!transcriptEl) {
    console.error('play_shell.js: #turn-transcript not found');
    return;
  }

  const renderer = new BlockRenderer(transcriptEl);
  const typewriter = new TypewriterEngine(window.TEST_MODE || false);
  const orchestrator = new BlocksOrchestrator(renderer, typewriter);
  const controls = new PlayControls(orchestrator);

  // Load typewriter config (default if not provided)
  const config = window.TYPEWRITER_CONFIG || {
    characters_per_second: 44,
    pause_before_ms: 150,
    pause_after_ms: 650,
    skippable: true,
  };
  typewriter.setConfig(config);

  // Attach control event listeners
  controls.attachEventListeners();

  // 1. Bootstrap: Load initial turn from script element
  function loadBootstrap() {
    const bootstrapEl = document.getElementById('play-shell-bootstrap');
    if (!bootstrapEl) {
      return;
    }

    try {
      const bootstrap = JSON.parse(bootstrapEl.textContent || '{}');
      if (bootstrap.visible_scene_output && bootstrap.visible_scene_output.blocks) {
        orchestrator.loadTurn(bootstrap);
      }
    } catch (err) {
      console.error('Failed to parse bootstrap data:', err);
    }
  }

  // 2. Form submission: Execute turn
  function handleFormSubmit(e) {
    e.preventDefault();

    const form = document.getElementById('play-execute-form');
    const input = document.getElementById('player-input');

    if (!form || !input) {
      return;
    }

    const playerInput = input.value.trim();
    if (!playerInput) {
      return;
    }

    const sessionId = shell.getAttribute('data-session-id');
    if (!sessionId) {
      console.error('Session ID not found');
      return;
    }

    // Disable form during submission
    const submitBtn = document.getElementById('execute-turn-btn');
    if (submitBtn) submitBtn.disabled = true;
    if (input) input.disabled = true;

    // Submit turn
    fetch(form.action || `/play/session/${sessionId}/turn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ player_input: playerInput }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        // Load new turn blocks
        orchestrator.loadTurn(data);

        // Clear input
        input.value = '';

        // Re-enable form
        if (submitBtn) submitBtn.disabled = false;
        if (input) input.disabled = false;
      })
      .catch((err) => {
        console.error('Turn execution failed:', err);

        // Re-enable form on error
        if (submitBtn) submitBtn.disabled = false;
        if (input) input.disabled = false;
      });
  }

  // 3. WebSocket: Listen for narrator blocks from play_narrative_stream.js
  function handleNarratorBlock(e) {
    if (e.detail && e.detail.block) {
      orchestrator.appendNarratorBlock(e.detail.block);
    }
  }

  // Wire event listeners
  const form = document.getElementById('play-execute-form');
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }

  window.addEventListener('narrator-block-received', handleNarratorBlock);

  // Initialize
  loadBootstrap();

  // Export orchestrator for testing and diagnostics
  window.BlocksOrchestrator_instance = orchestrator;
})();
