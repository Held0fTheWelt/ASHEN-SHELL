(function () {
  const cfg = window.__FRONTEND_CONFIG__ || {};
  const apiBase = (cfg.apiProxyBase || '') + '/api/v1';
  const evidenceOut = document.getElementById('ai-stack-evidence-out');
  const packagesOut = document.getElementById('ai-stack-packages-out');
  const sessionInput = document.getElementById('ai-stack-session-id');
  const loadEvidenceBtn = document.getElementById('ai-stack-load-evidence');
  const loadPackagesBtn = document.getElementById('ai-stack-load-packages');

  if (!evidenceOut || !packagesOut || !sessionInput || !loadEvidenceBtn || !loadPackagesBtn) return;

  function token() { return localStorage.getItem('access_token') || ''; }
  async function api(path, opts) {
    const headers = Object.assign({ 'Accept': 'application/json' }, (opts && opts.headers) || {});
    if (token()) headers['Authorization'] = 'Bearer ' + token();
    const res = await fetch(apiBase + path, Object.assign({}, opts, { headers }));
    const data = await res.json().catch(function () { return {}; });
    if (!res.ok) throw new Error(data.error || data.message || ('Request failed: ' + res.status));
    return data;
  }

  loadEvidenceBtn.addEventListener('click', function () {
    const sid = (sessionInput.value || '').trim();
    if (!sid) {
      evidenceOut.textContent = 'Enter a backend session id.';
      return;
    }
    api('/admin/ai-stack/session-evidence/' + encodeURIComponent(sid), { method: 'GET' })
      .then(function (data) { evidenceOut.textContent = JSON.stringify(data, null, 2); })
      .catch(function (err) { evidenceOut.textContent = err.message; });
  });

  loadPackagesBtn.addEventListener('click', function () {
    api('/admin/ai-stack/improvement-packages', { method: 'GET' })
      .then(function (data) { packagesOut.textContent = JSON.stringify(data, null, 2); })
      .catch(function (err) { packagesOut.textContent = err.message; });
  });
})();
