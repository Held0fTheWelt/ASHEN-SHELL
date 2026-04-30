/**
 * PlayControls — UI event handlers
 *
 * Responsibility: Wire DOM events (Skip, Reveal All, Accessibility mode) to orchestrator methods.
 */

class PlayControls {
  constructor(orchestrator) {
    if (!orchestrator) {
      throw new Error('PlayControls requires an orchestrator');
    }
    this.orchestrator = orchestrator;
  }

  /**
   * Attach event listeners to control buttons
   */
  attachEventListeners() {
    const skipBtn = document.getElementById('play-skip-current-btn');
    const revealBtn = document.getElementById('play-reveal-all-btn');
    const a11yCheckbox = document.getElementById('play-accessibility-mode');

    if (skipBtn) {
      skipBtn.addEventListener('click', () => {
        this.orchestrator.skipCurrentBlock();
      });
    }

    if (revealBtn) {
      revealBtn.addEventListener('click', () => {
        this.orchestrator.revealAll();
      });
    }

    if (a11yCheckbox) {
      a11yCheckbox.addEventListener('change', (e) => {
        this.orchestrator.setAccessibilityMode(e.target.checked);
      });
    }
  }
}

// Export for use
if (typeof window !== 'undefined') {
  window.PlayControls = PlayControls;
}
