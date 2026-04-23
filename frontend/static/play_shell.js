(function () {
  const shell = document.querySelector(".play-shell");
  if (!shell) return;

  function escapeHtml(value) {
    const d = document.createElement("div");
    d.textContent = value == null ? "" : String(value);
    return d.innerHTML;
  }

  function normalizeLine(line) {
    if (line == null) return "";
    if (typeof line === "string") return line.trim();
    if (typeof line === "object") {
      const text = String(line.text || "").trim();
      if (!text) return "";
      const actor = String(line.speaker_id || line.actor_id || "").trim();
      const tone = String(line.tone || "").trim();
      const prefix = actor ? actor + ": " : "";
      const suffix = tone ? " (" + tone + ")" : "";
      return (prefix + text + suffix).trim();
    }
    return String(line).trim();
  }

  function normalizeEntry(entry) {
    const normalized = Object.assign({}, entry || {});
    normalized.role = String(normalized.role || "runtime").trim() || "runtime";
    normalized.speaker = normalized.speaker || (normalized.role === "player" ? "You" : "World of Shadows");
    normalized.text = String(normalized.text || "").trim();

    const spoken = Array.isArray(normalized.spoken_lines) ? normalized.spoken_lines : [];
    normalized.spoken_lines = spoken.map(normalizeLine).filter(Boolean);

    const action = Array.isArray(normalized.action_lines) ? normalized.action_lines : [];
    normalized.action_lines = action.map(normalizeLine).filter(Boolean);

    const consequences = Array.isArray(normalized.committed_consequences) ? normalized.committed_consequences : [];
    normalized.committed_consequences = consequences.map(normalizeLine).filter(Boolean);

    const reasons = Array.isArray(normalized.degraded_reasons) ? normalized.degraded_reasons : [];
    normalized.degraded_reasons = reasons.map(normalizeLine).filter(Boolean);
    normalized.degraded = Boolean(normalized.degraded);
    normalized.responder_id = String(normalized.responder_id || "").trim();
    normalized.validation_status = String(normalized.validation_status || "").trim();
    return normalized;
  }

  function storyPlaceholderHtml() {
    return (
      '<p id="transcript-empty" class="play-story-placeholder">' +
      "No authored opening was returned by the story runtime. The player session is not ready for meaningful play." +
      "</p>"
    );
  }

  function entryHtml(rawEntry) {
    const entry = normalizeEntry(rawEntry);
    const speaker = entry.speaker || "World of Shadows";
    const turn = entry.turn_number != null ? "Turn " + escapeHtml(entry.turn_number) + " · " : "";
    let html = '<article class="play-turn-card play-turn-card--fresh">';
    html += '<header class="play-turn-card__meta">' + turn + escapeHtml(speaker) + "</header>";
    if (entry.role === "player") {
      html += '<p class="runtime-player-line"><strong>You:</strong> ' + escapeHtml(entry.text || "") + "</p>";
    } else if (entry.text) {
      html += '<div class="play-story-output">';
      html +=
        '<div class="play-story-text play-turn-card__narration play-narration--reveal">' +
        escapeHtml(entry.text) +
        "</div>";
      html += "</div>";
    }
    if (entry.spoken_lines.length) {
      html += '<h3 class="play-dialogue-label">Spoken</h3><ul class="runtime-spoken play-dialogue-list">';
      entry.spoken_lines.forEach(function (line) {
        html += "<li>" + escapeHtml(line) + "</li>";
      });
      html += "</ul>";
    }
    if (entry.action_lines.length) {
      html += '<h3 class="play-dialogue-label">Action</h3><ul class="runtime-actions play-dialogue-list">';
      entry.action_lines.forEach(function (line) {
        html += "<li>" + escapeHtml(line) + "</li>";
      });
      html += "</ul>";
    }
    if (entry.committed_consequences.length) {
      html += '<h3 class="play-dialogue-label">Consequences</h3><ul class="runtime-consequences">';
      entry.committed_consequences.forEach(function (line) {
        html += "<li>" + escapeHtml(line) + "</li>";
      });
      html += "</ul>";
    }
    if (entry.role === "runtime" && entry.responder_id) {
      html += '<p class="runtime-meta">Responder <code>' + escapeHtml(entry.responder_id) + "</code></p>";
    }
    if (entry.role === "runtime" && entry.degraded) {
      const reason = entry.degraded_reasons.length ? ": " + escapeHtml(entry.degraded_reasons.join(", ")) : "";
      html += '<p class="play-turn-warning">Degraded runtime path' + reason + "</p>";
    }
    html += "</article>";
    return html;
  }

  function summarizeRuntimeStatus(entries, fallbackStatus) {
    const status = {};
    if (fallbackStatus && typeof fallbackStatus === "object") {
      status.selected_responder_id = String(fallbackStatus.selected_responder_id || "").trim();
      status.validation_status = String(fallbackStatus.validation_status || "").trim();
      status.degraded = Boolean(fallbackStatus.degraded);
      status.degraded_reasons = Array.isArray(fallbackStatus.degraded_reasons)
        ? fallbackStatus.degraded_reasons.map(normalizeLine).filter(Boolean)
        : [];
    } else {
      status.selected_responder_id = "";
      status.validation_status = "";
      status.degraded = false;
      status.degraded_reasons = [];
    }

    const runtimeEntries = (entries || []).filter(function (entry) {
      return normalizeEntry(entry).role === "runtime";
    });
    if (runtimeEntries.length) {
      const latest = normalizeEntry(runtimeEntries[runtimeEntries.length - 1]);
      if (latest.responder_id) status.selected_responder_id = latest.responder_id;
      if (latest.validation_status) status.validation_status = latest.validation_status;
      if (latest.degraded) {
        status.degraded = true;
      }
      if (latest.degraded_reasons.length) {
        status.degraded_reasons = latest.degraded_reasons;
      }
    }
    return status;
  }

  function renderRuntimeStatus(status) {
    const responderEl = document.getElementById("runtime-selected-responder");
    if (responderEl) {
      responderEl.innerHTML =
        "Responder: <code>" + escapeHtml((status && status.selected_responder_id) || "n/a") + "</code>";
    }
    const validationEl = document.getElementById("runtime-validation-status");
    if (validationEl) {
      validationEl.innerHTML =
        "Validation: <code>" + escapeHtml((status && status.validation_status) || "unknown") + "</code>";
    }
    const bannerEl = document.getElementById("runtime-degraded-banner");
    if (bannerEl) {
      const degraded = Boolean(status && status.degraded);
      const reasons = Array.isArray(status && status.degraded_reasons) ? status.degraded_reasons : [];
      const reasonText = reasons.length ? " \u00b7 " + reasons.join(", ") : "";
      bannerEl.textContent = "Degraded runtime path" + reasonText;
      bannerEl.hidden = !degraded;
    }
  }

  function renderEntries(entries, runtimeStatusOverride) {
    const transcriptRoot = document.getElementById("turn-transcript");
    if (!transcriptRoot) return;
    const normalizedEntries = Array.isArray(entries) ? entries.map(normalizeEntry) : [];
    if (!normalizedEntries.length) {
      transcriptRoot.innerHTML = storyPlaceholderHtml();
      renderRuntimeStatus(summarizeRuntimeStatus([], runtimeStatusOverride));
      return;
    }
    transcriptRoot.innerHTML = normalizedEntries.map(entryHtml).join("");
    renderRuntimeStatus(summarizeRuntimeStatus(normalizedEntries, runtimeStatusOverride));
    transcriptRoot.scrollTop = transcriptRoot.scrollHeight;
    const lastCard = transcriptRoot.querySelector(".play-turn-card:last-of-type");
    if (lastCard && typeof lastCard.scrollIntoView === "function") {
      lastCard.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
    window.setTimeout(function () {
      document.querySelectorAll(".play-turn-card--fresh").forEach(function (el) {
        el.classList.remove("play-turn-card--fresh");
      });
    }, 1000);
  }

  function extractEntriesFromPayload(payload) {
    if (Array.isArray(payload)) return payload;
    if (!payload || typeof payload !== "object") return null;
    if (Array.isArray(payload.story_entries)) return payload.story_entries;
    if (payload.story_window && Array.isArray(payload.story_window.entries)) return payload.story_window.entries;
    if (payload.type === "snapshot" && payload.data && payload.data.story_window && Array.isArray(payload.data.story_window.entries)) {
      return payload.data.story_window.entries;
    }
    if (payload.data && Array.isArray(payload.data.story_entries)) return payload.data.story_entries;
    return null;
  }

  function extractRuntimeStatusFromPayload(payload) {
    if (!payload || typeof payload !== "object") return null;
    if (payload.runtime_status_view && typeof payload.runtime_status_view === "object") {
      return payload.runtime_status_view;
    }
    if (payload.data && payload.data.runtime_status_view && typeof payload.data.runtime_status_view === "object") {
      return payload.data.runtime_status_view;
    }
    return null;
  }

  function parsePayload(raw) {
    if (raw == null) return null;
    if (typeof raw === "string") {
      try {
        return JSON.parse(raw);
      } catch (_err) {
        return null;
      }
    }
    if (typeof raw === "object") return raw;
    return null;
  }

  function applyRuntimePayload(rawPayload) {
    const payload = parsePayload(rawPayload);
    if (!payload) return false;
    const entries = extractEntriesFromPayload(payload);
    const runtimeStatus = extractRuntimeStatusFromPayload(payload);
    if (!entries && !runtimeStatus) return false;
    if (entries) {
      renderEntries(entries, runtimeStatus || undefined);
      return true;
    }
    if (runtimeStatus) {
      renderRuntimeStatus(summarizeRuntimeStatus([], runtimeStatus));
      return true;
    }
    return false;
  }

  window.playShellApplyRuntimePayload = applyRuntimePayload;
  window.addEventListener("play-shell-runtime-update", function (event) {
    if (!event) return;
    applyRuntimePayload(event.detail);
  });
  window.addEventListener("message", function (event) {
    if (!event) return;
    applyRuntimePayload(event.data);
  });

  const bootstrapEl = document.getElementById("play-shell-bootstrap");
  if (bootstrapEl) {
    const bootstrapPayload = parsePayload(bootstrapEl.textContent || "{}") || {};
    const initialEntries = extractEntriesFromPayload(bootstrapPayload) || [];
    const initialStatus = extractRuntimeStatusFromPayload(bootstrapPayload);
    renderRuntimeStatus(summarizeRuntimeStatus(initialEntries, initialStatus || undefined));
  }

  const form = document.getElementById("play-execute-form");
  const executeStatus = document.getElementById("execute-status");
  if (!form) return;

  form.addEventListener("submit", function (ev) {
    const ta = document.getElementById("player-input");
    if (!ta || !ta.value.trim()) return;
    ev.preventDefault();
    const btn = document.getElementById("execute-turn-btn");
    if (btn) btn.disabled = true;
    if (executeStatus) executeStatus.textContent = "Submitting turn...";
    fetch(form.action, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      credentials: "same-origin",
      body: JSON.stringify({ player_input: ta.value.trim() }),
    })
      .then(function (r) {
        return r.json().then(function (data) {
          return { ok: r.ok, data: data };
        });
      })
      .then(function (res) {
        if (!res.ok || !res.data.ok) {
          if (executeStatus) executeStatus.textContent = (res.data && res.data.error) || "Turn failed.";
          return;
        }
        renderEntries(res.data.story_entries || [], res.data.runtime_status_view || undefined);
        ta.value = "";
        if (executeStatus) {
          const degraded = Boolean(res.data.runtime_status_view && res.data.runtime_status_view.degraded);
          executeStatus.textContent = degraded
            ? "Story updated (degraded runtime path)."
            : "Story updated.";
        }
      })
      .catch(function () {
        if (executeStatus) executeStatus.textContent = "Network error. Try again.";
      })
      .finally(function () {
        if (btn) btn.disabled = false;
      });
  });
})();
