(function () {
  const cfg = window.__FRONTEND_CONFIG__ || {};
  const apiBase = (cfg.apiProxyBase || '') + '/api/v1';
  const evidenceOut = document.getElementById('ai-stack-evidence-out');
  const packagesOut = document.getElementById('ai-stack-packages-out');
  const releaseOut = document.getElementById('ai-stack-release-readiness-out');
  const releaseSummary = document.getElementById('ai-stack-release-summary');
  const sessionInput = document.getElementById('ai-stack-session-id');
  const loadEvidenceBtn = document.getElementById('ai-stack-load-evidence');
  const loadPackagesBtn = document.getElementById('ai-stack-load-packages');
  const loadReleaseBtn = document.getElementById('ai-stack-load-release-readiness');

  if (!evidenceOut || !packagesOut || !sessionInput || !loadEvidenceBtn || !loadPackagesBtn) return;

  function summarizeReleaseReadiness(data) {
    if (!data || typeof data !== 'object') return '';
    var lines = [];
    lines.push('Overall: ' + (data.overall_status || '(missing)'));
    if (data.decision_support && typeof data.decision_support === 'object') {
      var ds = data.decision_support;
      lines.push('Writers-Room retrieval tier (latest artifact): ' + String(ds.latest_writers_room_retrieval_tier));
      lines.push('Improvement retrieval class (latest package): ' + String(ds.latest_improvement_retrieval_context_class));
      lines.push('WR retrieval graded review-ready: ' + String(ds.writers_room_review_ready_for_retrieval_graded_review));
      lines.push('Improvement retrieval graded review-ready: ' + String(ds.improvement_review_ready_for_retrieval_graded_review));
    }
    if (Array.isArray(data.areas)) {
      lines.push('Areas:');
      data.areas.forEach(function (a) {
        var posture = a.evidence_posture ? ' [' + a.evidence_posture + ']' : '';
        lines.push('  - ' + a.area + ': ' + a.status + posture);
      });
    }
    if (Array.isArray(data.known_partiality) && data.known_partiality.length) {
      lines.push('Known partiality: ' + data.known_partiality.join('; '));
    }
    if (Array.isArray(data.known_environment_sensitivities) && data.known_environment_sensitivities.length) {
      lines.push('Environment sensitivities: ' + data.known_environment_sensitivities.join('; '));
    }
    return lines.join('\n');
  }

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

  if (loadReleaseBtn && releaseOut) {
    loadReleaseBtn.addEventListener('click', function () {
      api('/admin/ai-stack/release-readiness', { method: 'GET' })
        .then(function (data) {
          if (releaseSummary) releaseSummary.textContent = summarizeReleaseReadiness(data);
          releaseOut.textContent = JSON.stringify(data, null, 2);
        })
        .catch(function (err) {
          if (releaseSummary) releaseSummary.textContent = '';
          releaseOut.textContent = err.message;
        });
    });
  }
})();
