(function () {
  var api = null;
  var currentRunId = null;
  function $(id) { return document.getElementById(id); }
  function showError(message) { var el = $('game-ops-error'); if (!el) return; if (!message) { el.hidden = true; el.textContent = ''; return; } el.hidden = false; el.textContent = message; }
  function escapeHtml(value) { return String(value || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;'); }
  function renderRuns(items) {
    var wrap = $('game-ops-runs'); if (!wrap) return; wrap.innerHTML = '';
    if (!items.length) { wrap.innerHTML = '<p class="muted">No active runs reported.</p>'; return; }
    items.forEach(function (item) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'list-card-button' + (currentRunId === item.id ? ' is-active' : '');
      button.innerHTML = '<strong>' + escapeHtml(item.template_title || item.template_id) + '</strong><br><small>' + escapeHtml(item.id) + ' · ' + escapeHtml(item.status) + ' · humans ' + escapeHtml(item.connected_humans + '/' + item.total_humans) + '</small>';
      button.addEventListener('click', function () { loadRun(item.id); });
      wrap.appendChild(button);
    });
  }
  function refreshRuns() { showError(''); api('/api/v1/game-admin/runtime/runs').then(function (data) { renderRuns(data.items || []); }).catch(function (err) { showError(err.message || 'Failed to load runtime runs.'); }); }
  function loadRun(runId) {
    currentRunId = runId; $('game-ops-load-transcript').disabled = false; $('game-ops-terminate').disabled = false; $('game-ops-transcript').textContent = 'Transcript not loaded.';
    api('/api/v1/game-admin/runtime/runs/' + encodeURIComponent(runId)).then(function (data) { $('game-ops-detail').textContent = JSON.stringify(data, null, 2); refreshRuns(); }).catch(function (err) { showError(err.message || 'Failed to load runtime detail.'); });
  }
  function loadTranscript() { if (!currentRunId) return; api('/api/v1/game-admin/runtime/runs/' + encodeURIComponent(currentRunId) + '/transcript').then(function (data) { $('game-ops-transcript').textContent = JSON.stringify(data, null, 2); }).catch(function (err) { showError(err.message || 'Failed to load transcript.'); }); }
  function terminateRun() { if (!currentRunId) return; var reason = $('game-ops-terminate-reason').value.trim(); api('/api/v1/game-admin/runtime/runs/' + encodeURIComponent(currentRunId) + '/terminate', { method: 'POST', body: JSON.stringify({ reason: reason || null }) }).then(function (data) { $('game-ops-detail').textContent = JSON.stringify(data, null, 2); loadTranscript(); refreshRuns(); }).catch(function (err) { showError(err.message || 'Failed to terminate run.'); }); }
  function init() {
    if (!window.ManageAuth || !window.ManageAuth.apiFetchWithAuth) return;
    api = window.ManageAuth.apiFetchWithAuth;
    $('game-ops-refresh').addEventListener('click', refreshRuns);
    $('game-ops-load-transcript').addEventListener('click', loadTranscript);
    $('game-ops-terminate').addEventListener('click', terminateRun);
    refreshRuns();
  }
  document.addEventListener('DOMContentLoaded', init);
})();
