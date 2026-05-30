const fs = require('fs');
const path = require('path');
const vm = require('vm');

const repoRoot = path.resolve(__dirname, '..', '..');

function runStaticScript(relativePath) {
  const warnings = [];
  const element = () => ({
    addEventListener: jest.fn(),
    checked: false,
    disabled: false,
    hidden: false,
    innerHTML: '',
    onclick: null,
    scrollHeight: 0,
    scrollTop: 0,
    textContent: '',
    value: '',
  });
  const context = {
    console: {
      error: jest.fn(),
      warn: jest.fn((message) => warnings.push(String(message))),
    },
    document: {
      createElement: () => ({ textContent: '', innerHTML: '' }),
      getElementById: () => element(),
      querySelectorAll: () => [],
    },
    fetch: jest.fn(async () => ({ ok: true, json: async () => [] })),
    location: { protocol: 'http:', host: 'localhost' },
    setInterval: jest.fn(),
    WebSocket: jest.fn(),
    alert: jest.fn(),
    URL,
    window: null,
  };
  context.window = context;
  context.window.W5_AST_FRONTEND_PLAYER_VIEW_ENABLED = true;
  vm.createContext(context);
  const source = fs.readFileSync(path.join(repoRoot, relativePath), 'utf8');
  vm.runInContext(source, context, { filename: relativePath });
  return { context, warnings };
}

function snapshotWithW5() {
  return {
    feature_flags: { W5_AST_FRONTEND_PLAYER_VIEW_ENABLED: true },
    current_room: { id: 'legacy_salon', name: 'Legacy Salon', description: 'legacy' },
    rooms: [{ id: 'salon_w5', name: 'Salon W5', description: 'w5' }],
    w5_player_view: {
      target_consumer: 'player_shell',
      where_summary: {
        current_visible_location: 'salon_w5',
        scene_location: { value: 'salon_w5' },
      },
    },
  };
}

function snapshotWithMalformedW5() {
  return {
    feature_flags: { W5_AST_FRONTEND_PLAYER_VIEW_ENABLED: true },
    current_room: { id: 'legacy_salon', name: 'Legacy Salon', description: 'legacy' },
    w5_player_view: { target_consumer: 'player_shell', where_summary: {} },
  };
}

test('backend currentRoomFromSnapshot prefers w5_player_view and does not warn', () => {
  const { context, warnings } = runStaticScript('backend/app/web/static/app.js');

  const room = context.window.__wosPlayerShellCurrentRoomFromSnapshot(snapshotWithW5());

  expect(room.id).toBe('salon_w5');
  expect(room.name).toBe('Salon W5');
  expect(warnings).toEqual([]);
  expect(context.console.warn).not.toHaveBeenCalled();
});

test('backend currentRoomFromSnapshot falls back to current_room with one warning', () => {
  const { context, warnings } = runStaticScript('backend/app/web/static/app.js');

  const first = context.window.__wosPlayerShellCurrentRoomFromSnapshot(snapshotWithMalformedW5());
  const second = context.window.__wosPlayerShellCurrentRoomFromSnapshot(snapshotWithMalformedW5());

  expect(first.id).toBe('legacy_salon');
  expect(second.id).toBe('legacy_salon');
  expect(warnings).toHaveLength(1);
  expect(warnings[0]).toContain('Deprecated room alias fallback');
});

test('live ws roomFromSnapshot prefers w5_player_view and does not warn', () => {
  const { context, warnings } = runStaticScript('frontend/static/play_live_ws.js');

  const room = context.window.__wosLiveWsRoomFromSnapshot(snapshotWithW5());

  expect(room.id).toBe('salon_w5');
  expect(room.name).toBe('salon_w5');
  expect(warnings).toEqual([]);
});

test('live ws roomFromSnapshot falls back to current_room with one warning', () => {
  const { context, warnings } = runStaticScript('frontend/static/play_live_ws.js');

  const first = context.window.__wosLiveWsRoomFromSnapshot(snapshotWithMalformedW5());
  const second = context.window.__wosLiveWsRoomFromSnapshot(snapshotWithMalformedW5());

  expect(first.id).toBe('legacy_salon');
  expect(second.id).toBe('legacy_salon');
  expect(warnings).toHaveLength(1);
  expect(warnings[0]).toContain('Deprecated room alias fallback');
});

test('world-engine currentRoomFromSnapshot prefers w5_player_view and does not warn', () => {
  const { context, warnings } = runStaticScript('world-engine/app/web/static/app.js');

  const room = context.window.__wosWorldEngineCurrentRoomFromSnapshot(snapshotWithW5());

  expect(room.id).toBe('salon_w5');
  expect(room.name).toBe('Salon W5');
  expect(warnings).toEqual([]);
});
