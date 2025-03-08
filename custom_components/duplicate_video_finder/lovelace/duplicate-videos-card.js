class DuplicateVideosCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  set hass(hass) {
    this._hass = hass;
    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.showError(`Entity not found: ${entityId}`);
      return;
    }

    this.render(state);
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  render(state) {
    const root = this.shadowRoot;
    const duplicates = state.attributes.duplicates || [];
    const scanState = state.attributes.scan_state || 'idle';
    const lastScan = state.attributes.last_scan || 'Never';
    const isScanning = scanState === 'scanning';

    root.innerHTML = `
      <ha-card>
        <div class="card-header">
          <div class="name">
            Duplicate Videos (${duplicates.length} sets found)
          </div>
        </div>
        <div class="card-content">
          <div class="status-bar">
            <div>Status: ${isScanning ? 'Scanning...' : 'Ready'}</div>
            <div>Last scan: ${lastScan}</div>
          </div>
          ${isScanning ? this.renderProgress() : ''}
          <div class="actions">
            <mwc-button @click="${this.startScan.bind(this)}" ?disabled="${isScanning}">
              Start Scan
            </mwc-button>
          </div>
          ${duplicates.length > 0 ? this.renderDuplicates(duplicates) : `<p>No duplicates found.</p>`}
        </div>
      </ha-card>
    `;
  }

  renderProgress() {
    return `
      <div class="progress">
        <p>Scanning file system for duplicate videos. This may take a while...</p>
        <ha-circular-progress active></ha-circular-progress>
      </div>
    `;
  }

  renderDuplicates(duplicates) {
    return `
      <div class="duplicate-list">
        ${duplicates.map((dup, index) => `
          <div class="duplicate-item">
            <div class="duplicate-header" @click="this.toggleDetails(${index})">
              <div class="duplicate-name">${dup.name}</div>
              <div class="duplicate-count">${dup.count} copies</div>
            </div>
            <div class="duplicate-details duplicate-details-${index}" style="display: none;">
              <ul>
                ${dup.paths.map(path => `<li>${path}</li>`).join('')}
              </ul>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  toggleDetails(index) {
    const details = this.shadowRoot.querySelector(`.duplicate-details-${index}`);
    if (details) {
      details.style.display = details.style.display === 'none' ? 'block' : 'none';
    }
  }

  startScan() {
    if (!this._hass) return;
    this._hass.callService('duplicate_video_finder', 'start_scan');
  }

  showError(error) {
    const root = this.shadowRoot;
    root.innerHTML = `
      <ha-card>
        <div class="card-content">
          <div class="error">${error}</div>
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return `
      ha-card {
        padding: 16px;
      }
      .card-header {
        display: flex;
        justify-content: space-between;
        padding-bottom: 12px;
      }
      .status-bar {
        display: flex;
        justify-content: space-between;
        margin-bottom: 16px;
      }
      .progress {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 16px 0;
      }
      .actions {
        margin: 16px 0;
      }
      .duplicate-list {
        margin-top: 16px;
      }
      .duplicate-item {
        margin-bottom: 8px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        overflow: hidden;
      }
      .duplicate-header {
        display: flex;
        justify-content: space-between;
        padding: 8px 16px;
        background: var(--secondary-background-color);
        cursor: pointer;
      }
      .duplicate-details {
        padding: 8px 16px;
      }
      .duplicate-details ul {
        margin: 0;
        padding-left: 16px;
      }
      .error {
        color: var(--error-color);
      }
    `;
  }
}

customElements.define('duplicate-videos-card', DuplicateVideosCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "duplicate-videos-card",
  name: "Duplicate Videos Card",
  description: "Card showing duplicate video files"
});
