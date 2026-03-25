(function () {
  var api = null;
  var state = { selectedId: null, items: [] };
  function $(id) { return document.getElementById(id); }
  function showError(message) {
    var el = $('game-content-error');
    if (!el) return;
    if (!message) { el.hidden = true; el.textContent = ''; return; }
    el.hidden = false;
    el.textContent = message;
  }
  function defaultPayload(key, title, type, summary, tags, styleProfile) {
    return {
      id: key || 'new_experience',
      title: title || 'New Experience',
      kind: type || 'solo_story',
      join_policy: type === 'open_world' ? 'public' : (type === 'group_story' ? 'invited_party' : 'owner_only'),
      summary: summary || '',
      max_humans: type === 'group_story' ? 4 : 1,
      persistent: type === 'open_world',
      initial_beat_id: 'intro',
      roles: [{ id: 'player', display_name: 'Player', description: 'Primary human viewpoint role.', mode: 'human', initial_room_id: 'start', can_join: true }],
      rooms: [{ id: 'start', name: 'Start', description: 'Author-defined starting room.', exits: [], prop_ids: [], action_ids: [] }],
      props: [],
      actions: [],
      beats: [{ id: 'intro', name: 'Intro', description: 'Initial authored beat.', summary: 'Initial authored beat.' }],
      tags: tags || [],
      style_profile: styleProfile || 'retro_pulp'
    };
  }
  function escapeHtml(value) {
    return String(value || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
  }
  function renderList() {
    var list = $('game-content-list'); if (!list) return; list.innerHTML = '';
    if (!state.items.length) { list.innerHTML = '<p class="muted">No experiences found.</p>'; return; }
    state.items.forEach(function (item) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'list-card-button' + (state.selectedId === item.id ? ' is-active' : '');
      button.innerHTML = '<strong>' + escapeHtml(item.title) + '</strong><br><small>' + escapeHtml(item.key) + ' · ' + escapeHtml(item.experience_type) + ' · ' + escapeHtml(item.status) + '</small>';
      button.addEventListener('click', function () { loadItem(item.id); });
      list.appendChild(button);
    });
  }
  function syncPayloadDefaults() {
    var payloadEl = $('game-content-payload'); if (!payloadEl || payloadEl.value.trim()) return;
    var tags = (($('game-content-tags').value || '').split(',').map(function (v) { return v.trim(); }).filter(Boolean));
    payloadEl.value = JSON.stringify(defaultPayload($('game-content-key').value.trim(), $('game-content-title').value.trim(), $('game-content-type').value, $('game-content-summary').value.trim(), tags, $('game-content-style').value.trim()), null, 2);
  }
  function fillForm(item) {
    $('game-content-id').value = item.id || '';
    $('game-content-key').value = item.key || '';
    $('game-content-key').disabled = !!item.id;
    $('game-content-title').value = item.title || '';
    $('game-content-type').value = item.experience_type || 'solo_story';
    $('game-content-style').value = item.style_profile || 'retro_pulp';
    $('game-content-tags').value = (item.tags || []).join(', ');
    $('game-content-summary').value = item.summary || '';
    $('game-content-status').value = item.status || 'draft';
    $('game-content-payload').value = JSON.stringify(item.draft_payload || defaultPayload(item.key, item.title, item.experience_type, item.summary, item.tags, item.style_profile), null, 2);
    $('game-content-meta').textContent = JSON.stringify({ id: item.id, current_version: item.current_version, published_version: item.published_version, published_at: item.published_at, updated_at: item.updated_at }, null, 2);
    $('game-content-publish').disabled = !item.id;
  }
  function collectPayload() {
    return {
      key: $('game-content-key').value.trim(),
      title: $('game-content-title').value.trim(),
      experience_type: $('game-content-type').value,
      style_profile: $('game-content-style').value.trim() || 'retro_pulp',
      tags: ($('game-content-tags').value || '').split(',').map(function (v) { return v.trim(); }).filter(Boolean),
      summary: $('game-content-summary').value.trim(),
      status: $('game-content-status').value,
      draft_payload: JSON.parse($('game-content-payload').value || '{}')
    };
  }
  function refreshList() {
    showError('');
    var params = [];
    var search = $('game-content-search').value.trim();
    var status = $('game-content-status-filter').value;
    if (search) params.push('q=' + encodeURIComponent(search));
    if (status) params.push('status=' + encodeURIComponent(status));
    api('/api/v1/game-admin/experiences?include_payload=0' + (params.length ? '&' + params.join('&') : ''))
      .then(function (data) { state.items = data.items || []; renderList(); })
      .catch(function (err) { showError(err.message || 'Failed to load game content.'); });
  }
  function loadItem(id) {
    showError('');
    api('/api/v1/game-admin/experiences/' + encodeURIComponent(id))
      .then(function (data) { state.selectedId = data.id; renderList(); fillForm(data); })
      .catch(function (err) { showError(err.message || 'Failed to load experience.'); });
  }
  function newItem() {
    state.selectedId = null; renderList(); $('game-content-id').value = ''; $('game-content-key').disabled = false; $('game-content-form').reset(); $('game-content-type').value = 'solo_story'; $('game-content-style').value = 'retro_pulp'; $('game-content-status').value = 'draft'; $('game-content-meta').textContent = ''; $('game-content-publish').disabled = true; syncPayloadDefaults();
  }
  function saveItem(event) {
    event.preventDefault(); showError('');
    var payload; try { payload = collectPayload(); } catch (e) { showError('Invalid JSON payload: ' + e.message); return; }
    var id = $('game-content-id').value;
    api(id ? '/api/v1/game-admin/experiences/' + encodeURIComponent(id) : '/api/v1/game-admin/experiences', { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) })
      .then(function (data) { state.selectedId = data.id; fillForm(data); refreshList(); })
      .catch(function (err) { showError(err.message || 'Failed to save experience.'); });
  }
  function publishSelected() {
    var id = $('game-content-id').value; if (!id) return; showError('');
    api('/api/v1/game-admin/experiences/' + encodeURIComponent(id) + '/publish', { method: 'POST', body: JSON.stringify({}) })
      .then(function (data) { fillForm(data); refreshList(); })
      .catch(function (err) { showError(err.message || 'Failed to publish experience.'); });
  }
  function init() {
    if (!window.ManageAuth || !window.ManageAuth.apiFetchWithAuth) return;
    api = window.ManageAuth.apiFetchWithAuth;
    $('game-content-form').addEventListener('submit', saveItem);
    $('game-content-refresh').addEventListener('click', refreshList);
    $('game-content-new').addEventListener('click', newItem);
    $('game-content-publish').addEventListener('click', publishSelected);
    ['game-content-key','game-content-title','game-content-type','game-content-summary','game-content-tags','game-content-style'].forEach(function (id) { var el = $(id); if (el) el.addEventListener('change', syncPayloadDefaults); });
    newItem(); refreshList();
  }
  document.addEventListener('DOMContentLoaded', init);
})();
