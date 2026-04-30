/**
 * State Delta Boundary Overrides Controller (Breakglass)
 * Manage protected state path overrides for narrative governance emergencies
 */

class StateDeltaBoundaryOverridesController {
    constructor() {
        this.currentOverride = null;
        this.overrides = [];
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.loadOverrides();
    }

    attachEventListeners() {
        const confirmBtn = document.getElementById('confirm_btn');
        const revokeBtn = document.getElementById('revoke_override_btn');

        if (confirmBtn) confirmBtn.addEventListener('click', () => this.createOverride());
        if (revokeBtn) revokeBtn.addEventListener('click', () => this.revokeOverride());
    }

    async loadOverrides() {
        try {
            const response = await fetch('/api/v1/admin/mvp4/overrides/state-delta-boundary');
            const result = await response.json();

            if (response.ok && result.data) {
                this.overrides = result.data.overrides || [];
                this.renderOverridesList();
            } else {
                this.showStatus('Failed to load overrides', 'error');
            }
        } catch (error) {
            console.error('Failed to load overrides:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async createOverride() {
        const sessionId = document.getElementById('session_id_input').value.trim();
        const protectedPath = document.getElementById('protected_path_input').value.trim();
        const reason = document.getElementById('reason_input').value.trim();

        if (!sessionId || !protectedPath || !reason) {
            this.showStatus('All fields are required', 'error');
            return;
        }

        closeConfirmModal();
        this.showStatus('Activating breakglass override...', 'info');

        try {
            const response = await fetch('/api/v1/admin/mvp4/overrides/state-delta-boundary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    protected_path: protectedPath,
                    reason: reason,
                }),
            });

            const result = await response.json();

            if (response.ok && result.data) {
                this.showStatus('⚠️ Breakglass override activated and audited', 'success');
                document.getElementById('session_id_input').value = '';
                document.getElementById('protected_path_input').value = '';
                document.getElementById('reason_input').value = '';
                this.loadOverrides();
            } else {
                this.showStatus(`Error: ${result.message || 'Failed to activate override'}`, 'error');
            }
        } catch (error) {
            console.error('Failed to activate override:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async revokeOverride() {
        if (!this.currentOverride) return;

        const reason = window.prompt('Reason for revocation:', 'Emergency resolved');
        if (reason === null) return;

        try {
            const response = await fetch(
                `/api/v1/admin/mvp4/overrides/state-delta-boundary/${this.currentOverride.override_id}`,
                {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reason: reason }),
                }
            );

            const result = await response.json();

            if (response.ok && result.data) {
                this.showStatus('Override revoked successfully', 'success');
                closeOverrideModal();
                this.loadOverrides();
            } else {
                this.showStatus(`Error: ${result.message || 'Failed to revoke override'}`, 'error');
            }
        } catch (error) {
            console.error('Failed to revoke override:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    renderOverridesList() {
        const listEl = document.getElementById('overrides_list');

        if (this.overrides.length === 0) {
            listEl.innerHTML = '<div class="overrides-table empty">No active overrides</div>';
            return;
        }

        let html = '<div class="override-row">' +
            '<div>Override ID</div>' +
            '<div>Protected Path</div>' +
            '<div>Reason</div>' +
            '<div>Activated By</div>' +
            '<div>Activated At</div>' +
            '<div>Status</div>' +
            '<div>Actions</div>' +
            '</div>';

        for (const override of this.overrides) {
            const active = override.active !== false && override.breakglass_activated;
            const statusClass = active ? 'active' : 'revoked';
            const statusText = active ? 'Active' : 'Revoked';
            const activatedTime = override.created?.timestamp ? new Date(override.created.timestamp).toLocaleString() : '—';

            html += `<div class="override-row">
                <div class="override-row-data">${override.override_id || '—'}</div>
                <div class="override-row-data">${override.protected_path || '—'}</div>
                <div class="override-row-data" title="${override.created?.reason || ''}">${this.truncate(override.created?.reason, 30) || '—'}</div>
                <div class="override-row-user">${override.created?.admin_user || '—'}</div>
                <div class="override-row-time">${activatedTime}</div>
                <div><span class="override-row-status ${statusClass}">⚠️ ${statusText}</span></div>
                <div class="override-row-actions">
                    <button onclick="stateDeltaController.showOverrideDetails('${override.override_id}')">Details</button>
                    ${active ? `<button class="danger" onclick="stateDeltaController.revokeOverride()">Revoke</button>` : ''}
                </div>
            </div>`;
        }

        listEl.innerHTML = html;
    }

    showOverrideDetails(overrideId) {
        const override = this.overrides.find(o => o.override_id === overrideId);
        if (!override) return;

        this.currentOverride = override;

        const detailsEl = document.getElementById('override_details_content');
        const activatedTime = override.created?.timestamp ? new Date(override.created.timestamp).toLocaleString() : '—';
        const revokedTime = override.revoked?.timestamp ? new Date(override.revoked.timestamp).toLocaleString() : '—';

        let html = `
            <div class="detail-field">
                <div class="detail-field-label">Override ID</div>
                <div class="detail-field-value">${override.override_id}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Type</div>
                <div class="detail-field-value">${override.type}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Protected Path</div>
                <div class="detail-field-value">${override.protected_path}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Session</div>
                <div class="detail-field-value">${override.scope}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Activated</div>
                <div class="detail-field-value">${activatedTime}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Activated By</div>
                <div class="detail-field-value">${override.created?.admin_user || '—'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Emergency Reason</div>
                <div class="detail-field-value">${override.created?.reason || '—'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Breakglass Status</div>
                <div class="detail-field-value">${override.breakglass_activated ? '⚠️ ACTIVE' : 'INACTIVE'}</div>
            </div>
        `;

        if (override.revoked) {
            html += `
                <div class="detail-field">
                    <div class="detail-field-label">Revoked</div>
                    <div class="detail-field-value">${revokedTime}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Revoked By</div>
                    <div class="detail-field-value">${override.revoked.admin_user || '—'}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Revocation Reason</div>
                    <div class="detail-field-value">${override.revoked.reason || '—'}</div>
                </div>
            `;
        }

        if (override.applied_events && override.applied_events.length > 0) {
            html += `<div class="detail-field">
                <div class="detail-field-label">Applied Events (${override.applied_events.length})</div>
                <div class="detail-field-value">
                    ${override.applied_events.map(e => `Turn ${e.turn_number}: ${e.result} (${new Date(e.applied_timestamp).toLocaleTimeString()})`).join('<br>')}
                </div>
            </div>`;
        }

        detailsEl.innerHTML = html;

        document.getElementById('override_details_modal').style.display = 'flex';
    }

    showStatus(message, type) {
        const statusEl = document.getElementById('creation_status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status-message ${type}`;
        }
    }

    truncate(str, maxLen) {
        if (!str) return '';
        return str.length > maxLen ? str.substring(0, maxLen) + '…' : str;
    }
}

// Global helper functions
function closeOverrideModal() {
    document.getElementById('override_details_modal').style.display = 'none';
}

function closeConfirmModal() {
    document.getElementById('confirm_modal').style.display = 'none';
}

function confirmBreakglassActivation() {
    const sessionId = document.getElementById('session_id_input').value.trim();
    const protectedPath = document.getElementById('protected_path_input').value.trim();
    const reason = document.getElementById('reason_input').value.trim();

    if (!sessionId || !protectedPath || !reason) {
        stateDeltaController.showStatus('All fields are required', 'error');
        return;
    }

    document.getElementById('confirm_modal').style.display = 'flex';
}

// Initialize on page load
let stateDeltaController;
document.addEventListener('DOMContentLoaded', () => {
    stateDeltaController = new StateDeltaBoundaryOverridesController();
});
