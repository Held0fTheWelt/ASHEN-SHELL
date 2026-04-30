/**
 * Object Admission Overrides Controller
 * Manage object admission tier overrides for narrative governance
 */

class ObjectAdmissionOverridesController {
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
        const createBtn = document.getElementById('create_override_btn');
        const revokeBtn = document.getElementById('revoke_override_btn');

        if (createBtn) createBtn.addEventListener('click', () => this.createOverride());
        if (revokeBtn) revokeBtn.addEventListener('click', () => this.revokeOverride());
    }

    async loadOverrides() {
        try {
            const response = await fetch('/api/v1/admin/mvp4/overrides/object-admission');
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
        const objectId = document.getElementById('object_id_input').value.trim();
        const tierChange = document.getElementById('tier_change_input').value.trim();
        const reason = document.getElementById('reason_input').value.trim();

        if (!sessionId || !objectId || !tierChange || !reason) {
            this.showStatus('All fields are required', 'error');
            return;
        }

        this.showStatus('Creating override...', 'info');

        try {
            const response = await fetch('/api/v1/admin/mvp4/overrides/object-admission', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    object_id: objectId,
                    tier_change: tierChange,
                    reason: reason,
                }),
            });

            const result = await response.json();

            if (response.ok && result.data) {
                this.showStatus('Override created successfully', 'success');
                document.getElementById('session_id_input').value = '';
                document.getElementById('object_id_input').value = '';
                document.getElementById('tier_change_input').value = '';
                document.getElementById('reason_input').value = '';
                this.loadOverrides();
            } else {
                this.showStatus(`Error: ${result.message || 'Failed to create override'}`, 'error');
            }
        } catch (error) {
            console.error('Failed to create override:', error);
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }

    async revokeOverride() {
        if (!this.currentOverride) return;

        const reason = window.prompt('Reason for revocation:', 'Override revoked');
        if (reason === null) return;

        try {
            const response = await fetch(
                `/api/v1/admin/mvp4/overrides/object-admission/${this.currentOverride.override_id}`,
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
            '<div>Object ID</div>' +
            '<div>Tier Change</div>' +
            '<div>Session</div>' +
            '<div>Created By</div>' +
            '<div>Status</div>' +
            '<div>Actions</div>' +
            '</div>';

        for (const override of this.overrides) {
            const active = override.active !== false;
            const statusClass = active ? 'active' : 'revoked';
            const statusText = active ? 'Active' : 'Revoked';

            html += `<div class="override-row">
                <div class="override-row-data">${override.override_id || '—'}</div>
                <div class="override-row-data">${override.target || '—'}</div>
                <div class="override-row-data">${override.tier_change || '—'}</div>
                <div class="override-row-data" title="${override.scope || ''}">${this.truncate(override.scope, 20) || '—'}</div>
                <div class="override-row-user">${override.created?.admin_user || '—'}</div>
                <div><span class="override-row-status ${statusClass}">${statusText}</span></div>
                <div class="override-row-actions">
                    <button onclick="objectAdmissionController.showOverrideDetails('${override.override_id}')">Details</button>
                    ${active ? `<button class="danger" onclick="objectAdmissionController.revokeOverride()">Revoke</button>` : ''}
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
        const createdTime = override.created?.timestamp ? new Date(override.created.timestamp).toLocaleString() : '—';
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
                <div class="detail-field-label">Object</div>
                <div class="detail-field-value">${override.target}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Tier Change</div>
                <div class="detail-field-value">${override.tier_change}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Session</div>
                <div class="detail-field-value">${override.scope}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Created</div>
                <div class="detail-field-value">${createdTime}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Created By</div>
                <div class="detail-field-value">${override.created?.admin_user || '—'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Reason</div>
                <div class="detail-field-value">${override.created?.reason || '—'}</div>
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

// Global helper function
function closeOverrideModal() {
    document.getElementById('override_details_modal').style.display = 'none';
}

// Initialize on page load
let objectAdmissionController;
document.addEventListener('DOMContentLoaded', () => {
    objectAdmissionController = new ObjectAdmissionOverridesController();
});
