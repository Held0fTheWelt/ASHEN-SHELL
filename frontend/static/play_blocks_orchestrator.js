/**
 * BlocksOrchestrator — State management + event coordination
 *
 * Responsibility: Coordinate BlockRenderer, TypewriterEngine, and PlayControls.
 * Manages blocks array, handles HTTP loads, WebSocket narrator streaming, and user controls.
 */

class BlocksOrchestrator {
  constructor(renderer, typewriter, controls = null) {
    if (!renderer || !typewriter) {
      throw new Error('BlocksOrchestrator requires renderer and typewriter');
    }

    this.renderer = renderer;
    this.typewriter = typewriter;
    this.controls = controls;

    this.blocks = []; // All blocks ever rendered
    this.currentBlockIndex = 0; // Which block is being typed
    this.accessibility_mode = false;
  }

  /**
   * Load initial turn from HTTP response
   *
   * @param {Object} response - HTTP response with visible_scene_output.blocks
   */
  loadTurn(response) {
    if (!response || !response.visible_scene_output) {
      return;
    }

    const blocks = response.visible_scene_output.blocks || [];

    // Clear previous blocks
    this.renderer.clear();
    this.typewriter.reset();
    this.blocks = [];
    this.currentBlockIndex = 0;

    // Render all blocks
    for (let block of blocks) {
      this.blocks.push(block);
      this.renderer.render(block);

      // Start typewriter delivery (unless accessibility mode)
      if (!this.accessibility_mode) {
        this.typewriter.startDelivery(block);
      } else {
        // Accessibility mode: show all text immediately
        const el = this.renderer.getBlockElement(block.id);
        if (el) {
          el.textContent = block.text || '';
        }
      }
    }
  }

  /**
   * Append narrator block from WebSocket streaming
   *
   * @param {Object} block - Scene block from narrator stream
   */
  appendNarratorBlock(block) {
    if (!block || !block.id || !block.text) {
      return;
    }

    // Add to blocks array
    this.blocks.push(block);

    // Render to DOM
    this.renderer.render(block);

    // Start typewriter delivery (unless accessibility mode)
    if (!this.accessibility_mode) {
      this.typewriter.startDelivery(block);
    } else {
      const el = this.renderer.getBlockElement(block.id);
      if (el) {
        el.textContent = block.text;
      }
    }
  }

  /**
   * Skip current block (user clicked "Skip")
   */
  skipCurrentBlock() {
    if (this.currentBlockIndex >= this.blocks.length) {
      return;
    }

    const current = this.blocks[this.currentBlockIndex];
    this.typewriter.skipBlock(current.id);
    this.currentBlockIndex++;
  }

  /**
   * Reveal all blocks immediately (user clicked "Reveal All")
   */
  revealAll() {
    this.typewriter.revealAll();
  }

  /**
   * Toggle accessibility mode
   *
   * @param {boolean} enabled - Enable or disable accessibility mode
   */
  setAccessibilityMode(enabled) {
    this.accessibility_mode = !!enabled;

    if (enabled) {
      // Show all blocks immediately
      for (let block of this.blocks) {
        const el = this.renderer.getBlockElement(block.id);
        if (el) {
          el.textContent = block.text || '';
        }
      }
    }
  }

  /**
   * Get current state (for diagnostics)
   */
  getState() {
    return {
      blocks_count: this.blocks.length,
      current_block_index: this.currentBlockIndex,
      accessibility_mode: this.accessibility_mode,
      typewriter_state: this.typewriter.getQueueState(),
    };
  }
}

// Export for use
if (typeof window !== 'undefined') {
  window.BlocksOrchestrator = BlocksOrchestrator;
}
