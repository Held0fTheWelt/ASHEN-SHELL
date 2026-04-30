/**
 * Governance Health Panels Controller
 * Real-time quality assessment, token budgeting, cost tracking, and evaluation metrics
 */

class GovernanceHealthPanelsController {
    constructor() {
        this.currentSessionId = null;
        this.autoRefreshInterval = null;
        this.costChart = null;
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.initializeCharts();
    }

    attachEventListeners() {
        const loadBtn = document.getElementById('load_session_btn');
        const sessionInput = document.getElementById('session_id_input');
        const panelRefreshBtns = document.querySelectorAll('.panel-refresh');
        const applyOverrideBtn = document.getElementById('apply_budget_override_btn');

        if (loadBtn) loadBtn.addEventListener('click', () => this.loadSession());
        if (sessionInput) sessionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.loadSession();
        });

        panelRefreshBtns.forEach(btn => {
            btn.addEventListener('click', () => this.refreshAllPanels());
        });

        if (applyOverrideBtn) {
            applyOverrideBtn.addEventListener('click', () => this.applyBudgetOverride());
        }
    }

    loadSession() {
        const sessionInput = document.getElementById('session_id_input');
        const sessionId = sessionInput.value.trim();

        if (!sessionId) {
            this.setStatus('Please enter a session ID', 'error');
            return;
        }

        this.currentSessionId = sessionId;
        this.setStatus('Loading session data...', 'info');
        this.fetchSessionData(sessionId);
    }

    async fetchSessionData(sessionId) {
        try {
            // Fetch token budget
            const budgetRes = await fetch(
                `/api/v1/admin/mvp4/game/session/${sessionId}/token-budget`
            );
            const budgetData = await budgetRes.json();

            // Fetch evaluation weights
            const weightsRes = await fetch(
                `/api/v1/admin/mvp4/evaluation/weights/${sessionId}`
            );
            const weightsData = await weightsRes.json();

            // In a real implementation, would also fetch:
            // - diagnostics envelope (quality_class, degradation_timeline, cost_summary)
            // - evaluation metrics (turn scores)
            // - cost dashboard data

            this.updatePanels(budgetData?.data, weightsData?.data);
            this.setStatus('Session loaded successfully', 'success');

        } catch (error) {
            console.error('Failed to load session data:', error);
            this.setStatus(`Error loading session: ${error.message}`, 'error');
        }
    }

    updatePanels(budgetData, weightsData) {
        // Panel 1: Real-Time Health Status
        const qualityClass = document.getElementById('quality_class');
        const degradationLevel = document.getElementById('degradation_level');
        if (qualityClass) qualityClass.textContent = budgetData?.degradation_level || '—';
        if (degradationLevel) degradationLevel.textContent = budgetData?.degradation_level || 'none';

        // Panel 2: Token & Cost Metrics
        const tokensUsed = document.getElementById('tokens_used');
        const costUsed = document.getElementById('cost_used');
        const budgetStatus = document.getElementById('budget_status');
        const budgetProgress = document.getElementById('budget_progress');

        if (budgetData && budgetData.data) {
            const { used_tokens, total_budget, usage_percent } = budgetData.data;
            if (tokensUsed) tokensUsed.textContent = used_tokens || '0';
            if (costUsed) costUsed.textContent = '$0.0000'; // Phase A: no real costs yet
            if (budgetStatus) budgetStatus.textContent = `${used_tokens} / ${total_budget} tokens`;
            if (budgetProgress) budgetProgress.style.width = `${usage_percent || 0}%`;

            // Update budget controls panel
            document.getElementById('total_budget').textContent = `${total_budget} tokens`;
            document.getElementById('budget_used').textContent = `${used_tokens} tokens`;
            document.getElementById('budget_remaining').textContent = `${total_budget - used_tokens} tokens`;
            document.getElementById('degradation_strategy').textContent = budgetData.data.degradation_strategy || 'ldss_shorter';
        }

        // Panel 5: Evaluation Metrics (from rubric weights in Phase A, will be real scores in Phase B)
        if (weightsData && weightsData.data) {
            const weights = weightsData.data.weights;
            this.updateDimensionScore('coherence', 3.5, weights?.weight_coherence);
            this.updateDimensionScore('authenticity', 3.5, weights?.weight_authenticity);
            this.updateDimensionScore('player_agency', 3.5, weights?.weight_player_agency);
            this.updateDimensionScore('immersion', 3.5, weights?.weight_immersion);
        }

        // Panel 6: Cost Dashboard
        this.updateCostDashboard();
    }

    updateDimensionScore(dimension, score, weight) {
        const scoreBar = document.getElementById(`${dimension}_score_bar`);
        const scoreSpan = document.getElementById(`${dimension}_score`);

        if (scoreBar) scoreBar.style.width = `${(score / 5) * 100}%`;
        if (scoreSpan) scoreSpan.textContent = `${score.toFixed(1)}/5`;

        // Weight indicator (Phase A: placeholder; Phase B: real)
        if (weight && weight !== 1.0) {
            console.debug(`${dimension} weight: ${weight}`);
        }
    }

    updateDegradationTimeline(events) {
        const timelineEl = document.getElementById('degradation_timeline');
        if (!timelineEl) return;

        if (!events || events.length === 0) {
            timelineEl.innerHTML = '<p class="empty-state">No degradation events recorded</p>';
            return;
        }

        timelineEl.innerHTML = events.map(event => `
            <div class="timeline-item">
                <div class="timeline-timestamp">${this.formatTime(event.timestamp)}</div>
                <div class="timeline-event">
                    <strong>${event.severity}</strong>: ${event.marker}
                    ${event.recovery_successful ? '✓ Recovered' : '✗ Active'}
                </div>
            </div>
        `).join('');
    }

    updateCostDashboard() {
        // Phase A: Placeholder values
        // Phase B: Will fetch real cost data from cost dashboard endpoints
        document.getElementById('cost_today').textContent = '$0.00';
        document.getElementById('cost_week').textContent = '$0.00';
        document.getElementById('cost_per_turn').textContent = '$0.00';
        document.getElementById('cost_projected').textContent = '$0.00';
    }

    async applyBudgetOverride() {
        if (!this.currentSessionId) {
            this.setStatus('Please load a session first', 'error');
            return;
        }

        const tokensToAdd = parseInt(document.getElementById('tokens_to_add').value, 10);
        const reason = document.getElementById('override_reason').value.trim();

        if (isNaN(tokensToAdd) || tokensToAdd <= 0) {
            this.setStatus('Please enter a valid number of tokens', 'error');
            return;
        }

        if (!reason) {
            this.setStatus('Please provide a reason for the override', 'error');
            return;
        }

        try {
            const response = await fetch(
                `/api/v1/admin/mvp4/game/session/${this.currentSessionId}/token-budget/override`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tokens_to_add: tokensToAdd, reason: reason }),
                }
            );

            const result = await response.json();
            if (response.ok) {
                this.setStatus(`Budget override applied: ${tokensToAdd} tokens added`, 'success');
                document.getElementById('tokens_to_add').value = '';
                document.getElementById('override_reason').value = '';
                this.fetchSessionData(this.currentSessionId);
            } else {
                this.setStatus(`Error: ${result.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            this.setStatus(`Error applying override: ${error.message}`, 'error');
        }
    }

    refreshAllPanels() {
        if (this.currentSessionId) {
            this.fetchSessionData(this.currentSessionId);
        }
    }

    initializeCharts() {
        const ctx = document.getElementById('cost_breakdown_chart');
        if (!ctx) return;

        this.costChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['LDSS', 'Narrator', 'Fallback', 'Other'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#4caf50',
                        '#2196f3',
                        '#ff9800',
                        '#9c27b0',
                    ],
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
            },
        });
    }

    setStatus(message, type) {
        const statusEl = document.getElementById('session_status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = `status-indicator status-${type}`;
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.healthPanelsController = new GovernanceHealthPanelsController();
});
