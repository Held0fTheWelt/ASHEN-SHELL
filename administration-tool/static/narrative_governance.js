/* global ManageAuth */
(function () {
    "use strict";

    function renderJson(targetId, title, data) {
        var el = document.getElementById(targetId);
        if (!el) return;
        el.innerHTML = "";
        var card = document.createElement("div");
        card.className = "narrative-card";
        var h = document.createElement("h2");
        h.textContent = title;
        var pre = document.createElement("pre");
        pre.textContent = JSON.stringify(data, null, 2);
        card.appendChild(h);
        card.appendChild(pre);
        el.appendChild(card);
    }

    function loadOverview() {
        Promise.all([
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/packages"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/health?module_id=god_of_carnage"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/revision-conflicts"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/notifications/feed")
        ]).then(function (results) {
            renderJson("narrative-overview-grid", "Overview", {
                packages: results[0].data,
                runtime_health: results[1].data,
                conflicts: results[2].data,
                notifications: results[3].data
            });
        }).catch(function (err) {
            renderJson("narrative-overview-grid", "Overview Error", err);
        });
    }

    function loadRuntime() {
        ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/config")
            .then(function (result) { renderJson("narrative-runtime-panel", "Runtime Config", result.data); })
            .catch(function (err) { renderJson("narrative-runtime-panel", "Runtime Config Error", err); });
    }

    function loadRuntimeHealth() {
        Promise.all([
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/health?module_id=god_of_carnage"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/health/fallbacks?module_id=god_of_carnage")
        ]).then(function (results) {
            renderJson("narrative-runtime-health-panel", "Runtime Health", {
                summary: results[0].data,
                fallbacks: results[1].data
            });
        }).catch(function (err) {
            renderJson("narrative-runtime-health-panel", "Runtime Health Error", err);
        });
    }

    function loadPackages() {
        ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/packages")
            .then(function (result) { renderJson("narrative-packages-panel", "Packages", result.data); })
            .catch(function (err) { renderJson("narrative-packages-panel", "Packages Error", err); });
    }

    function loadPolicies() {
        ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/config")
            .then(function (result) { renderJson("narrative-policies-panel", "Policy View", result.data); })
            .catch(function (err) { renderJson("narrative-policies-panel", "Policy Error", err); });
    }

    function loadFindings() {
        Promise.all([
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/runtime/health/events?module_id=god_of_carnage"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/revisions")
        ]).then(function (results) {
            renderJson("narrative-findings-panel", "Findings and Linked Revisions", {
                runtime_events: results[0].data,
                revisions: results[1].data
            });
        }).catch(function (err) {
            renderJson("narrative-findings-panel", "Findings Error", err);
        });
    }

    function loadRevisions() {
        Promise.all([
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/revisions"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/revision-conflicts")
        ]).then(function (results) {
            renderJson("narrative-revisions-panel", "Revisions with Inline Conflicts", {
                revisions: results[0].data,
                conflicts: results[1].data
            });
        }).catch(function (err) {
            renderJson("narrative-revisions-panel", "Revisions Error", err);
        });
    }

    function loadEvaluations() {
        ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/evaluations?module_id=god_of_carnage")
            .then(function (result) { renderJson("narrative-evaluations-panel", "Evaluations", result.data); })
            .catch(function (err) { renderJson("narrative-evaluations-panel", "Evaluations Error", err); });
    }

    function loadNotifications() {
        Promise.all([
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/notifications/rules"),
            ManageAuth.apiFetchWithAuth("/api/v1/admin/narrative/notifications/feed")
        ]).then(function (results) {
            renderJson("narrative-notifications-panel", "Notifications", {
                rules: results[0].data,
                feed: results[1].data
            });
        }).catch(function (err) {
            renderJson("narrative-notifications-panel", "Notifications Error", err);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        var pageEl = document.querySelector(".narrative-governance-page");
        if (!pageEl) return;
        var page = pageEl.getAttribute("data-narrative-page");
        var loaders = {
            overview: loadOverview,
            runtime: loadRuntime,
            runtime_health: loadRuntimeHealth,
            packages: loadPackages,
            policies: loadPolicies,
            findings: loadFindings,
            revisions: loadRevisions,
            evaluations: loadEvaluations,
            notifications: loadNotifications
        };
        if (loaders[page]) loaders[page]();
    });
})();
