/**
 * Canonical Inspector Suite workbench (read-only rendering).
 */
(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function setText(id, text) {
    var el = byId(id);
    if (!el) return;
    el.textContent = text == null ? "" : String(text);
  }

  function setHtml(id, html) {
    var el = byId(id);
    if (!el) return;
    el.innerHTML = html;
  }

  function toPretty(value) {
    return JSON.stringify(value == null ? null : value, null, 2);
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDisplayValue(v) {
    if (v == null) return "null";
    if (typeof v === "object") return JSON.stringify(v);
    return String(v);
  }

  function statusText(section) {
    if (!section || typeof section !== "object") return "unavailable";
    return String(section.status || "unavailable");
  }

  function extractData(section) {
    if (!section || typeof section !== "object") return null;
    return section.data == null ? null : section.data;
  }

  function sectionReason(section) {
    if (!section || typeof section !== "object") return "";
    return String(section.unavailable_reason || section.unsupported_reason || "");
  }

  function envelopeBanner(section) {
    if (!section || typeof section !== "object") {
      return '<p class="inspector-section-status inspector-section-status-unavailable">No projection envelope.</p>';
    }
    var st = statusText(section);
    var reason = sectionReason(section);
    var cls = "inspector-section-status";
    if (st === "unavailable") cls += " inspector-section-status-unavailable";
    else if (st === "unsupported") cls += " inspector-section-status-unsupported";
    else cls += " inspector-section-status-supported";
    var parts = ['<p class="' + cls + '"><strong>Status:</strong> ' + escapeHtml(st) + "</p>"];
    if (reason) {
      parts.push(
        '<p class="inspector-section-reason"><strong>Reason:</strong> ' + escapeHtml(reason) + "</p>"
      );
    }
    return parts.join("");
  }

  function toPairs(data) {
    if (!data || typeof data !== "object") return [];
    return Object.keys(data).map(function (key) {
      return { key: key, value: data[key] };
    });
  }

  function renderKeyValueGrid(containerId, data, fallback) {
    var el = byId(containerId);
    if (!el) return;
    if (!data || typeof data !== "object") {
      el.innerHTML = '<p class="manage-empty">' + (fallback || "No data loaded.") + "</p>";
      return;
    }
    var rows = toPairs(data).map(function (row) {
      return (
        '<div class="inspector-kv-item">' +
        '<span class="inspector-kv-key">' +
        escapeHtml(row.key) +
        "</span>" +
        '<span class="inspector-kv-value">' +
        escapeHtml(formatDisplayValue(row.value)) +
        "</span>" +
        "</div>"
      );
    });
    el.innerHTML = rows.join("");
  }

  function renderMermaid(decisionTrace) {
    var host = byId("inspector-mermaid-host");
    if (!host) return;
    var data = extractData(decisionTrace);
    if (!data || !Array.isArray(data.flow_nodes) || !data.flow_nodes.length) {
      host.innerHTML = '<p class="manage-empty">No flow nodes available.</p>';
      return;
    }
    var nodes = data.flow_nodes.map(function (id) {
      var safeId = String(id).replace(/[^a-zA-Z0-9_]/g, "_");
      return safeId + '["' + String(id).replace(/"/g, '\\"') + '"]';
    });
    var edges = [];
    if (Array.isArray(data.flow_edges)) {
      edges = data.flow_edges
        .map(function (edge) {
          if (!edge || typeof edge !== "object") return "";
          var src = String(edge.from || "").replace(/[^a-zA-Z0-9_]/g, "_");
          var dst = String(edge.to || "").replace(/[^a-zA-Z0-9_]/g, "_");
          if (!src || !dst) return "";
          return src + " --> " + dst;
        })
        .filter(Boolean);
    }
    var graphSrc = ["flowchart LR"].concat(nodes).concat(edges).join("\n");
    if (!window.mermaid || typeof window.mermaid.render !== "function") {
      host.innerHTML = '<pre class="code-block">' + escapeHtml(graphSrc) + "</pre>";
      return;
    }
    window.mermaid
      .render("inspectorWorkbenchMermaidGraph", graphSrc)
      .then(function (result) {
        host.innerHTML = result.svg;
      })
      .catch(function () {
        host.innerHTML = '<pre class="code-block">' + escapeHtml(graphSrc) + "</pre>";
      });
  }

  function mergeSectionSummary(section) {
    var data = extractData(section);
    var base = { envelope_status: statusText(section) };
    if (sectionReason(section)) {
      base.envelope_reason = sectionReason(section);
    }
    if (data && typeof data === "object" && !Array.isArray(data)) {
      Object.keys(data).forEach(function (k) {
        base[k] = data[k];
      });
    } else if (data != null) {
      base.payload = data;
    }
    return base;
  }

  function renderTurnPayload(payload) {
    var turnIdentity = payload.turn_identity || {};
    var decisionTrace = payload.decision_trace_projection || {};
    var authority = payload.authority_projection || {};
    var planner = payload.planner_state_projection || {};
    var gate = payload.gate_projection || {};
    var validation = payload.validation_projection || {};
    var fallback = payload.fallback_projection || {};

    var decisionData = extractData(decisionTrace) || {};
    var identityData = extractData(turnIdentity) || {};
    renderKeyValueGrid(
      "inspector-decision-summary",
      {
        projection_status: payload.projection_status,
        turn_identity_status: statusText(turnIdentity),
        decision_trace_status: statusText(decisionTrace),
        turn_number_world_engine: identityData.turn_number_world_engine,
        execution_health: decisionData.execution_health,
        fallback_path_taken: decisionData.fallback_path_taken,
      },
      "No decision summary loaded."
    );

    renderKeyValueGrid(
      "inspector-authority-boundary",
      extractData(authority),
      "No authority projection loaded."
    );
    setText("inspector-planner-state", toPretty(planner));
    renderKeyValueGrid("inspector-gate-outcome-grid", mergeSectionSummary(gate), "No gate projection loaded.");
    renderKeyValueGrid(
      "inspector-validation-outcome-grid",
      mergeSectionSummary(validation),
      "No validation projection loaded."
    );
    renderKeyValueGrid(
      "inspector-fallback-status-grid",
      mergeSectionSummary(fallback),
      "No fallback projection loaded."
    );
    setText("inspector-raw-json", toPretty(payload));

    var gateData = extractData(gate) || {};
    var rejection = {
      gate_envelope_status: statusText(gate),
      dominant_rejection_category: gateData.dominant_rejection_category,
      rejection_codes: gateData.rejection_codes,
      legacy_fallback_used: gateData.legacy_fallback_used,
      scene_function_mismatch_score: gateData.scene_function_mismatch_score,
      character_implausibility_score: gateData.character_implausibility_score,
      continuity_pressure_score: gateData.continuity_pressure_score,
      fluency_risk_score: gateData.fluency_risk_score,
    };
    renderKeyValueGrid(
      "inspector-rejection-analysis-grid",
      rejection,
      "No rejection analysis loaded."
    );
    renderMermaid(decisionTrace);
  }

  function renderDistributionBlock(title, dist) {
    if (!dist || typeof dist !== "object" || !Object.keys(dist).length) {
      return (
        '<section class="inspector-dist-block"><h4 class="inspector-subheading">' +
        escapeHtml(title) +
        '</h4><p class="manage-empty">No distribution data.</p></section>'
      );
    }
    var rows = Object.keys(dist).map(function (k) {
      return { key: k, value: dist[k] };
    });
    var inner = rows
      .map(function (r) {
        return (
          '<div class="inspector-kv-item"><span class="inspector-kv-key">' +
          escapeHtml(r.key) +
          '</span><span class="inspector-kv-value">' +
          escapeHtml(formatDisplayValue(r.value)) +
          "</span></div>"
        );
      })
      .join("");
    return (
      '<section class="inspector-dist-block"><h4 class="inspector-subheading">' +
      escapeHtml(title) +
      '</h4><div class="inspector-kv-grid">' +
      inner +
      "</div></section>"
    );
  }

  function renderCoverageView(root) {
    var hostId = "inspector-coverage-structured";
    var section = root && root.coverage_health_projection;
    var html = envelopeBanner(section);
    var data = extractData(section) || {};
    var metrics = data.metrics || {};
    var dist = data.distribution || {};
    var fb = metrics.fallback_frequency;
    if (fb && typeof fb === "object") {
      html += '<section class="inspector-dist-block"><h4 class="inspector-subheading">Fallback frequency</h4><div class="inspector-kv-grid">';
      html += toPairs(fb)
        .map(function (r) {
          return (
            '<div class="inspector-kv-item"><span class="inspector-kv-key">' +
            escapeHtml(r.key) +
            '</span><span class="inspector-kv-value">' +
            escapeHtml(formatDisplayValue(r.value)) +
            "</span></div>"
          );
        })
        .join("");
      html += "</div></section>";
    }
    html += renderDistributionBlock("Gate outcome distribution", dist.gate_outcome_distribution);
    html += renderDistributionBlock("Validation outcome distribution", dist.validation_outcome_distribution);
    html += renderDistributionBlock("Rejection / rationale distribution", dist.rejection_rationale_distribution);
    html += renderDistributionBlock(
      "Unsupported / unavailable frequency",
      dist.unsupported_unavailable_frequency
    );
    if (metrics.total_turns != null) {
      html +=
        '<p class="manage-state">Total turns (metrics): ' + escapeHtml(String(metrics.total_turns)) + "</p>";
    }
    setHtml(hostId, html);
  }

  function renderProvenanceView(root) {
    var section = root && root.provenance_raw_projection;
    var parts = [envelopeBanner(section)];
    var data = extractData(section) || {};
    var entries = data.entries;
    var cols = [
      { key: "field", label: "Field" },
      { key: "value", label: "Value" },
      { key: "source_kind", label: "Source kind" },
      { key: "source_ref", label: "Source ref" },
    ];
    if (statusText(section) === "supported" && Array.isArray(entries) && entries.length) {
      var tableHtml =
        '<table class="inspector-data-table"><caption class="visually-hidden">Canonical provenance entries</caption><thead><tr>' +
        cols
          .map(function (c) {
            return "<th>" + escapeHtml(c.label) + "</th>";
          })
          .join("") +
        "</tr></thead><tbody>";
      tableHtml += entries
        .map(function (row) {
          return (
            "<tr>" +
            cols
              .map(function (c) {
                var v = row[c.key];
                return "<td>" + escapeHtml(formatDisplayValue(v)) + "</td>";
              })
              .join("") +
            "</tr>"
          );
        })
        .join("");
      tableHtml += "</tbody></table>";
      parts.push(tableHtml);
      if (data.canonical_vs_raw_boundary) {
        parts.push(
          '<p class="manage-state inspector-boundary-note">' +
            escapeHtml(String(data.canonical_vs_raw_boundary)) +
            "</p>"
        );
      }
    } else {
      parts.push('<p class="manage-empty">No canonical provenance entries to display.</p>');
    }
    setHtml("inspector-provenance-canonical", parts.join(""));

    var rawEl = byId("inspector-provenance-raw-json");
    if (rawEl) {
      if (root && root.raw_mode_loaded && root.raw_evidence) {
        rawEl.textContent = toPretty(root.raw_evidence);
      } else {
        rawEl.textContent =
          "Raw evidence not loaded. Select read mode “raw” and load the workbench to inspect raw bundles (secondary material only).";
      }
    }
  }

  function renderTimelineViewFixed(root) {
    var host = byId("inspector-timeline-structured");
    if (!host) return;
    var section = root && root.timeline_projection;
    var parts = [envelopeBanner(section)];
    var st = statusText(section);
    var data = extractData(section);
    if (st === "supported" && data && Array.isArray(data.turns) && data.turns.length) {
      parts.push(
        '<p class="manage-state">Total turns: ' +
          escapeHtml(String(data.total_turns != null ? data.total_turns : data.turns.length)) +
          "</p>"
      );
      var cols = [
        { key: "turn_index", label: "Turn index" },
        { key: "turn_number", label: "Turn #" },
        { key: "trace_id", label: "Trace id" },
        { key: "gate_result", label: "Gate result" },
        { key: "validation_status", label: "Validation" },
        { key: "validation_reason", label: "Validation reason" },
        { key: "fallback_path_taken", label: "Fallback path" },
        { key: "execution_health", label: "Execution health" },
        { key: "selected_scene_function", label: "Scene function" },
        { key: "route_mode", label: "Route mode" },
        { key: "route_reason_code", label: "Route reason" },
      ];
      var tableHtml =
        '<table class="inspector-data-table"><caption class="visually-hidden">Timeline turns</caption><thead><tr>' +
        cols
          .map(function (c) {
            return "<th>" + escapeHtml(c.label) + "</th>";
          })
          .join("") +
        "</tr></thead><tbody>";
      tableHtml += data.turns
        .map(function (row) {
          return (
            "<tr>" +
            cols
              .map(function (c) {
                var v = row[c.key];
                return "<td>" + escapeHtml(formatDisplayValue(v)) + "</td>";
              })
              .join("") +
            "</tr>"
          );
        })
        .join("");
      tableHtml += "</tbody></table>";
      parts.push(tableHtml);
    } else {
      parts.push('<p class="manage-empty">No structured timeline rows to display.</p>');
    }
    host.innerHTML = parts.join("");
  }

  function renderComparisonViewFixed(root) {
    var host = byId("inspector-comparison-structured");
    if (!host) return;
    var section = root && root.comparison_projection;
    var parts = [envelopeBanner(section)];
    var data = extractData(section) || {};
    if (Array.isArray(data.unsupported_dimensions) && data.unsupported_dimensions.length) {
      parts.push('<h4 class="inspector-subheading">Unsupported dimensions (explicit)</h4><ul class="inspector-dim-list">');
      data.unsupported_dimensions.forEach(function (d) {
        parts.push("<li>" + escapeHtml(String(d)) + "</li>");
      });
      parts.push("</ul>");
    }
    if (Array.isArray(data.supported_dimensions) && data.supported_dimensions.length) {
      parts.push(
        '<h4 class="inspector-subheading">Supported dimensions</h4><p>' +
          escapeHtml(data.supported_dimensions.join(", ")) +
          "</p>"
      );
    }
    var comparisons = data.comparisons;
    if (statusText(section) === "supported" && Array.isArray(comparisons) && comparisons.length) {
      var cols = [
        { key: "from_turn_number", label: "From turn" },
        { key: "to_turn_number", label: "To turn" },
        { key: "gate_result_from", label: "Gate (from)" },
        { key: "gate_result_to", label: "Gate (to)" },
        { key: "validation_status_from", label: "Validation (from)" },
        { key: "validation_status_to", label: "Validation (to)" },
        { key: "fallback_path_taken_from", label: "Fallback (from)" },
        { key: "fallback_path_taken_to", label: "Fallback (to)" },
        { key: "selected_scene_function_from", label: "Scene fn (from)" },
        { key: "selected_scene_function_to", label: "Scene fn (to)" },
      ];
      var tableHtml =
        '<table class="inspector-data-table"><caption class="visually-hidden">Turn comparisons</caption><thead><tr>' +
        cols
          .map(function (c) {
            return "<th>" + escapeHtml(c.label) + "</th>";
          })
          .join("") +
        "</tr></thead><tbody>";
      tableHtml += comparisons
        .map(function (row) {
          return (
            "<tr>" +
            cols
              .map(function (c) {
                var v = row[c.key];
                return "<td>" + escapeHtml(formatDisplayValue(v)) + "</td>";
              })
              .join("") +
            "</tr>"
          );
        })
        .join("");
      tableHtml += "</tbody></table>";
      parts.push(tableHtml);
    } else {
      parts.push(
        '<p class="manage-empty">No turn-to-turn comparison rows (need at least two turns in session evidence).</p>'
      );
    }
    host.innerHTML = parts.join("");
  }

  function switchTab(targetPanelId) {
    var tabs = document.querySelectorAll(".inspector-tab");
    var panels = document.querySelectorAll("[data-inspector-panel]");
    for (var i = 0; i < tabs.length; i++) {
      var tab = tabs[i];
      var active = tab.getAttribute("data-panel") === targetPanelId;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
    }
    for (var j = 0; j < panels.length; j++) {
      var panel = panels[j];
      panel.hidden = panel.id !== targetPanelId;
    }
  }

  function initTabs() {
    var tabs = document.querySelectorAll(".inspector-tab");
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].addEventListener("click", function (event) {
        var panelId = event.currentTarget.getAttribute("data-panel");
        if (panelId) switchTab(panelId);
      });
    }
  }

  function initMermaid() {
    if (!window.mermaid || typeof window.mermaid.initialize !== "function") return;
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "default",
    });
  }

  function buildPath(sessionId, mode, view) {
    var suffix = "/api/v1/admin/ai-stack/inspector/" + view + "/" + encodeURIComponent(sessionId);
    if (view === "turn" || view === "provenance-raw") {
      suffix += "?mode=" + encodeURIComponent(mode === "raw" ? "raw" : "canonical");
    }
    return suffix;
  }

  function loadWorkbench() {
    var sessionField = byId("inspector-session-id");
    var modeField = byId("inspector-mode");
    var sessionId = ((sessionField && sessionField.value) || "").trim();
    var mode = ((modeField && modeField.value) || "canonical").trim();
    if (!sessionId) {
      setText("inspector-load-state", "Bitte zuerst eine Backend-Session-ID eingeben.");
      return;
    }
    setText("inspector-load-state", "Lade Workbench-Projektionen ...");

    var paths = {
      turn: buildPath(sessionId, mode, "turn"),
      timeline: buildPath(sessionId, mode, "timeline"),
      comparison: buildPath(sessionId, mode, "comparison"),
      coverage: buildPath(sessionId, mode, "coverage-health"),
      provenance: buildPath(sessionId, mode, "provenance-raw"),
    };

    Promise.all([
      window.ManageAuth.apiFetchWithAuth(paths.turn),
      window.ManageAuth.apiFetchWithAuth(paths.timeline),
      window.ManageAuth.apiFetchWithAuth(paths.comparison),
      window.ManageAuth.apiFetchWithAuth(paths.coverage),
      window.ManageAuth.apiFetchWithAuth(paths.provenance),
    ])
      .then(function (payloads) {
        var turn = payloads[0] || {};
        var timeline = payloads[1] || {};
        var comparison = payloads[2] || {};
        var coverage = payloads[3] || {};
        var provenance = payloads[4] || {};
        renderTurnPayload(turn);
        renderTimelineViewFixed(timeline);
        renderComparisonViewFixed(comparison);
        renderCoverageView(coverage);
        renderProvenanceView(provenance);
        setText("inspector-timeline-full-json", toPretty(timeline));
        setText("inspector-comparison-full-json", toPretty(comparison));
        setText("inspector-coverage-full-json", toPretty(coverage));
        setText("inspector-provenance-full-json", toPretty(provenance));
        setText("inspector-load-state", "Workbench-Projektionen geladen.");
        switchTab("inspector-panel-turn");
      })
      .catch(function (error) {
        var msg = error && error.message ? error.message : "Request failed";
        setText("inspector-load-state", msg);
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!window.ManageAuth) return;
    initTabs();
    initMermaid();
    var loadBtn = byId("inspector-load-all");
    if (loadBtn) {
      loadBtn.addEventListener("click", loadWorkbench);
    }
    window.ManageAuth.ensureAuth().catch(function () {});
  });
})();
