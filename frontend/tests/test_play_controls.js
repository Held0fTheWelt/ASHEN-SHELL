/**
 * Unit tests for PlayControls
 * Tests UI event handler wiring
 */

describe('PlayControls', () => {
  let mockOrchestrator;
  let controls;

  beforeEach(() => {
    mockOrchestrator = {
      skipCurrentBlock: jest.fn(),
      revealAll: jest.fn(),
      setAccessibilityMode: jest.fn(),
    };

    controls = new PlayControls(mockOrchestrator);
  });

  describe('initialization', () => {
    test('should require an orchestrator', () => {
      expect(() => new PlayControls(null)).toThrow();
    });

    test('should store orchestrator reference', () => {
      expect(controls.orchestrator).toBe(mockOrchestrator);
    });
  });

  describe('attachEventListeners()', () => {
    test('should attach click handler to skip button', () => {
      const skipBtn = document.createElement('button');
      skipBtn.id = 'play-skip-current-btn';
      document.body.appendChild(skipBtn);

      controls.attachEventListeners();
      skipBtn.click();

      expect(mockOrchestrator.skipCurrentBlock).toHaveBeenCalled();

      document.body.removeChild(skipBtn);
    });

    test('should attach click handler to reveal button', () => {
      const revealBtn = document.createElement('button');
      revealBtn.id = 'play-reveal-all-btn';
      document.body.appendChild(revealBtn);

      controls.attachEventListeners();
      revealBtn.click();

      expect(mockOrchestrator.revealAll).toHaveBeenCalled();

      document.body.removeChild(revealBtn);
    });

    test('should attach change handler to accessibility checkbox', () => {
      const a11yCheckbox = document.createElement('input');
      a11yCheckbox.id = 'play-accessibility-mode';
      a11yCheckbox.type = 'checkbox';
      document.body.appendChild(a11yCheckbox);

      controls.attachEventListeners();

      a11yCheckbox.checked = true;
      a11yCheckbox.dispatchEvent(new Event('change'));

      expect(mockOrchestrator.setAccessibilityMode).toHaveBeenCalledWith(true);

      a11yCheckbox.checked = false;
      a11yCheckbox.dispatchEvent(new Event('change'));

      expect(mockOrchestrator.setAccessibilityMode).toHaveBeenCalledWith(false);

      document.body.removeChild(a11yCheckbox);
    });

    test('should handle missing buttons gracefully', () => {
      // No buttons in DOM
      expect(() => controls.attachEventListeners()).not.toThrow();
    });

    test('should handle multiple attach calls', () => {
      const skipBtn = document.createElement('button');
      skipBtn.id = 'play-skip-current-btn';
      document.body.appendChild(skipBtn);

      controls.attachEventListeners();
      controls.attachEventListeners();

      skipBtn.click();

      // Event should be called (might be called twice due to multiple attachments)
      expect(mockOrchestrator.skipCurrentBlock).toHaveBeenCalled();

      document.body.removeChild(skipBtn);
    });
  });

  describe('button interaction flow', () => {
    test('should skip multiple blocks in sequence', () => {
      const skipBtn = document.createElement('button');
      skipBtn.id = 'play-skip-current-btn';
      document.body.appendChild(skipBtn);

      controls.attachEventListeners();

      skipBtn.click();
      skipBtn.click();
      skipBtn.click();

      expect(mockOrchestrator.skipCurrentBlock).toHaveBeenCalledTimes(3);

      document.body.removeChild(skipBtn);
    });

    test('should handle reveal and skip together', () => {
      const skipBtn = document.createElement('button');
      skipBtn.id = 'play-skip-current-btn';
      const revealBtn = document.createElement('button');
      revealBtn.id = 'play-reveal-all-btn';
      document.body.appendChild(skipBtn);
      document.body.appendChild(revealBtn);

      controls.attachEventListeners();

      skipBtn.click();
      revealBtn.click();
      skipBtn.click();

      expect(mockOrchestrator.skipCurrentBlock).toHaveBeenCalledTimes(2);
      expect(mockOrchestrator.revealAll).toHaveBeenCalledTimes(1);

      document.body.removeChild(skipBtn);
      document.body.removeChild(revealBtn);
    });

    test('should toggle accessibility mode', () => {
      const checkbox = document.createElement('input');
      checkbox.id = 'play-accessibility-mode';
      checkbox.type = 'checkbox';
      document.body.appendChild(checkbox);

      controls.attachEventListeners();

      // Toggle on
      checkbox.checked = true;
      checkbox.dispatchEvent(new Event('change'));

      expect(mockOrchestrator.setAccessibilityMode).toHaveBeenCalledWith(true);

      // Toggle off
      checkbox.checked = false;
      checkbox.dispatchEvent(new Event('change'));

      expect(mockOrchestrator.setAccessibilityMode).toHaveBeenCalledWith(false);

      // Toggle on again
      checkbox.checked = true;
      checkbox.dispatchEvent(new Event('change'));

      expect(mockOrchestrator.setAccessibilityMode).toHaveBeenCalledTimes(3);

      document.body.removeChild(checkbox);
    });
  });
});
