/**
 * Operational governance admin surface.
 */
(function () {
    function show(kind, msg) {
        var errEl = document.getElementById("manage-og-banner");
        var okEl = document.getElementById("manage-og-success");
        if (errEl) {
            errEl.style.display = "none";
            errEl.textContent = "";
        }
        if (okEl) {
            okEl.style.display = "none";
            okEl.textContent = "";
        }
        if (!msg) return;
        if (kind === "ok" && okEl) {
            okEl.style.display = "";
            okEl.textContent = msg;
        } else if (errEl) {
            errEl.style.display = "";
            errEl.textContent = msg;
        }
    }

    function val(id, fallback) {
        var node = document.getElementById(id);
        if (!node) return fallback || "";
        return node.value || fallback || "";
    }

    function setVal(id, value) {
        var node = document.getElementById(id);
        if (node) node.value = value || "";
    }

    function renderResolvedConfig(payload) {
        var box = document.getElementById("manage-og-runtime-config");
        if (!box) return;
        box.textContent = JSON.stringify(payload || {}, null, 2);
    }

    function loadModes() {
        return window.ManageAuth.apiFetchWithAuth("/api/v1/admin/runtime/modes")
            .then(function (res) {
                var data = res.data || {};
                setVal("manage-og-generation-mode", data.generation_execution_mode);
                setVal("manage-og-retrieval-mode", data.retrieval_execution_mode);
                setVal("manage-og-validation-mode", data.validation_execution_mode);
                setVal("manage-og-provider-selection", data.provider_selection_mode);
                setVal("manage-og-runtime-profile", data.runtime_profile);
            });
    }

    function loadResolved() {
        return window.ManageAuth.apiFetchWithAuth("/api/v1/admin/runtime/resolved-config")
            .then(function (res) {
                renderResolvedConfig(res.data || {});
            });
    }

    function refreshAll() {
        show(null, "");
        return Promise.all([loadModes(), loadResolved()]);
    }

    function parseError(err) {
        if (!err) return "Request failed";
        return err.message || "Request failed";
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (!window.ManageAuth) return;
        window.ManageAuth.ensureAuth()
            .then(function () { return refreshAll(); })
            .catch(function (err) { show("err", parseError(err)); });

        var refreshBtn = document.getElementById("manage-og-refresh");
        if (refreshBtn) {
            refreshBtn.addEventListener("click", function () {
                refreshAll().catch(function (err) { show("err", parseError(err)); });
            });
        }

        var initBtn = document.getElementById("manage-og-bootstrap-init");
        if (initBtn) {
            initBtn.addEventListener("click", function () {
                var body = {
                    selected_preset: val("manage-og-preset", "safe_local"),
                    admin_email: val("manage-og-admin-email", "operator@example.com"),
                    secret_storage_mode: "same_db_encrypted",
                    generation_execution_mode: val("manage-og-generation-mode", "mock_only"),
                    retrieval_execution_mode: val("manage-og-retrieval-mode", "disabled"),
                    validation_execution_mode: val("manage-og-validation-mode", "schema_only"),
                    provider_selection_mode: val("manage-og-provider-selection", "local_only"),
                    trust_anchor: {
                        kek_source: "deployment_secret",
                        allow_reopen_with_recovery_token: true
                    }
                };
                window.ManageAuth.apiFetchWithAuth("/api/v1/admin/bootstrap/initialize", {
                    method: "POST",
                    body: JSON.stringify(body)
                }).then(function () {
                    show("ok", "Bootstrap initialized.");
                    return refreshAll();
                }).catch(function (err) {
                    show("err", parseError(err));
                });
            });
        }

        var saveModesBtn = document.getElementById("manage-og-save-modes");
        if (saveModesBtn) {
            saveModesBtn.addEventListener("click", function () {
                var body = {
                    generation_execution_mode: val("manage-og-generation-mode", "mock_only"),
                    retrieval_execution_mode: val("manage-og-retrieval-mode", "disabled"),
                    validation_execution_mode: val("manage-og-validation-mode", "schema_only"),
                    provider_selection_mode: val("manage-og-provider-selection", "local_only"),
                    runtime_profile: val("manage-og-runtime-profile", "safe_local")
                };
                window.ManageAuth.apiFetchWithAuth("/api/v1/admin/runtime/modes", {
                    method: "PATCH",
                    body: JSON.stringify(body)
                }).then(function () {
                    show("ok", "Runtime modes updated.");
                    return refreshAll();
                }).catch(function (err) {
                    show("err", parseError(err));
                });
            });
        }

        var providerCreateBtn = document.getElementById("manage-og-provider-create");
        if (providerCreateBtn) {
            providerCreateBtn.addEventListener("click", function () {
                var providerBody = {
                    provider_type: val("manage-og-provider-type", "mock"),
                    display_name: val("manage-og-provider-display", "Mock Provider"),
                    base_url: val("manage-og-provider-base-url", ""),
                    is_enabled: true
                };
                window.ManageAuth.apiFetchWithAuth("/api/v1/admin/ai/providers", {
                    method: "POST",
                    body: JSON.stringify(providerBody)
                }).then(function (res) {
                    var providerId = (res.data || {}).provider_id;
                    var key = val("manage-og-provider-api-key", "");
                    if (!providerId || !key) return res;
                    return window.ManageAuth.apiFetchWithAuth("/api/v1/admin/ai/providers/" + providerId + "/credential", {
                        method: "POST",
                        body: JSON.stringify({ api_key: key, label: "ui_submit" })
                    });
                }).then(function () {
                    show("ok", "Provider created (credential written when provided).");
                    return refreshAll();
                }).catch(function (err) {
                    show("err", parseError(err));
                });
            });
        }

        var providerTestBtn = document.getElementById("manage-og-provider-test");
        if (providerTestBtn) {
            providerTestBtn.addEventListener("click", function () {
                window.ManageAuth.apiFetchWithAuth("/api/v1/admin/ai/providers")
                    .then(function (res) {
                        var providers = (res.data || {}).providers || [];
                        if (!providers.length) throw new Error("No providers available for testing.");
                        return providers[0].provider_id;
                    })
                    .then(function (providerId) {
                        return window.ManageAuth.apiFetchWithAuth("/api/v1/admin/ai/providers/" + providerId + "/test-connection", {
                            method: "POST",
                            body: "{}"
                        });
                    })
                    .then(function () {
                        show("ok", "Provider health test completed.");
                        return refreshAll();
                    })
                    .catch(function (err) {
                        show("err", parseError(err));
                    });
            });
        }

        var reloadBtn = document.getElementById("manage-og-bootstrap-reload");
        if (reloadBtn) {
            reloadBtn.addEventListener("click", function () {
                window.ManageAuth.apiFetchWithAuth("/api/v1/admin/runtime/reload-resolved-config", {
                    method: "POST",
                    body: "{}"
                }).then(function () {
                    show("ok", "Resolved config regenerated.");
                    return refreshAll();
                }).catch(function (err) {
                    show("err", parseError(err));
                });
            });
        }
    });
})();
