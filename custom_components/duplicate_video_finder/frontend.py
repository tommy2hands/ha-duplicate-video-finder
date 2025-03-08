"""Frontend for Duplicate Video Finder."""
import os
import logging

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_frontend(hass: HomeAssistant) -> bool:
    """Set up the frontend for the integration."""
    # Register the panel
    register_panel(hass)
    
    # Register custom card for use in dashboards
    register_card(hass)
    
    return True


def register_panel(hass: HomeAssistant) -> None:
    """Register a panel in Home Assistant for the integration."""
    # Register the panel
    hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Duplicate Videos",
        sidebar_icon="mdi:video-multiple",
        frontend_url_path="duplicate-video-finder",
        config={
            "url": "/api/duplicate_video_finder/dashboard",
            "title": "Duplicate Video Finder"
        },
        require_admin=False,
    )
    
    # Register a view for the panel
    hass.http.register_view(DuplicateVideoFinderPanelView(hass))
    

def register_card(hass: HomeAssistant) -> None:
    """Register the custom card for use in dashboards."""
    root_path = os.path.dirname(__file__)
    card_path = os.path.join(root_path, "lovelace", "duplicate-videos-card.js")
    
    if not os.path.exists(card_path):
        _LOGGER.error(f"Could not find card at {card_path}")
        return
        
    # Serve the card file
    hass.http.register_static_path(
        f"/duplicate_video_finder/duplicate-videos-card.js",
        card_path,
        True
    )
    
    # Add to resources to make it available
    add_extra_js_url(
        hass,
        f"/duplicate_video_finder/duplicate-videos-card.js",
        es5=False
    )


class DuplicateVideoFinderPanelView(HomeAssistantView):
    """View for the Duplicate Video Finder panel."""
    
    requires_auth = True
    url = "/api/duplicate_video_finder/dashboard"
    name = "api:duplicate_video_finder:dashboard"
    
    def __init__(self, hass: HomeAssistant):
        """Initialize the view."""
        self.hass = hass
        
    async def get(self, request):
        """Handle GET request."""
        html = self._generate_html()
        return self.json({"html_response": html})
    
    def _generate_html(self):
        """Generate the HTML for the panel."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Duplicate Video Finder</title>
            <style>
                body {{  
                    font-family: var(--paper-font-body1_-_font-family);
                    -webkit-font-smoothing: var(--paper-font-body1_-_-webkit-font-smoothing);
                    font-size: var(--paper-font-body1_-_font-size);
                    font-weight: var(--paper-font-body1_-_font-weight);
                    line-height: var(--paper-font-body1_-_line-height);
                    background-color: var(--primary-background-color);
                    color: var(--primary-text-color);
                    margin: 0;
                    padding: 16px;
                }}
                .card {{  
                    background-color: var(--card-background-color);
                    border-radius: 8px;
                    box-shadow: 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12), 0 3px 1px -2px rgba(0, 0, 0, 0.2);
                    padding: 16px;
                    margin-bottom: 16px;
                }}
                h1 {{  
                    font-family: var(--paper-font-headline_-_font-family);
                    -webkit-font-smoothing: var(--paper-font-headline_-_-webkit-font-smoothing);
                    font-size: var(--paper-font-headline_-_font-size);
                    font-weight: var(--paper-font-headline_-_font-weight);
                    letter-spacing: var(--paper-font-headline_-_letter-spacing);
                    line-height: var(--paper-font-headline_-_line-height);
                    margin: 0 0 16px;
                }}
                button {{  
                    background-color: var(--primary-color);
                    border: none;
                    border-radius: 4px;
                    color: white;
                    padding: 8px 16px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 14px;
                    margin: 4px 2px;
                    cursor: pointer;
                }}
                .loading {{  
                    display: none;
                    margin: 20px 0;
                    text-align: center;
                }}
                .duplicate-item {{  
                    border: 1px solid var(--divider-color);
                    border-radius: 4px;
                    margin-bottom: 8px;
                    overflow: hidden;
                }}
                .duplicate-header {{  
                    background-color: var(--secondary-background-color);
                    padding: 10px 16px;
                    display: flex;
                    justify-content: space-between;
                    cursor: pointer;
                }}
                .duplicate-details {{  
                    padding: 0 16px;
                    display: none;
                }}
                .duplicate-details.visible {{  
                    display: block;
                    padding: 10px 16px;
                }}
                .status-bar {{  
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 16px;
                }}
                #results {{  
                    margin-top: 20px;
                }}
                .path-list {{  
                    margin: 0;
                    padding-left: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Duplicate Video Finder</h1>
                <div class="status-bar">
                    <div id="status">Status: Ready</div>
                    <div id="lastScan">Last scan: Never</div>
                </div>
                <button id="startScan">Start Scan</button>
                <div id="loading" class="loading">
                    <p>Scanning for duplicate videos. This may take a while depending on your file system size...</p>
                    <p id="progressText"></p>
                </div>
                <div id="results"></div>
            </div>
            
            <script>
                // Helper function to communicate with Home Assistant
                function callService(domain, service, data) {{
                    return fetch('/api/services/' + domain + '/' + service, {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(data || {{}}),
                    }});
                }}
                
                // Get state of entity
                function getState(entityId) {{
                    return fetch('/api/states/' + entityId)
                        .then(response => response.json());
                }}
                
                document.addEventListener('DOMContentLoaded', function() {{
                    const startButton = document.getElementById('startScan');
                    const loadingDiv = document.getElementById('loading');
                    const resultsDiv = document.getElementById('results');
                    const statusDiv = document.getElementById('status');
                    const lastScanDiv = document.getElementById('lastScan');
                    const progressText = document.getElementById('progressText');
                    const entityId = 'sensor.duplicate_video_finder';
                    
                    // Check initial state
                    getState(entityId).then(state => {{
                        updateUIFromState(state);
                    }});
                    
                    // Set up event source for real-time updates
                    const eventSource = new EventSource('/api/stream');
                    eventSource.addEventListener('state_changed', function(e) {{
                        const data = JSON.parse(e.data);
                        if (data.entity_id === entityId) {{
                            updateUIFromState(data.new_state);
                        }}
                    }});
                    
                    // Handle start scan button
                    startButton.addEventListener('click', function() {{
                        startButton.disabled = true;
                        loadingDiv.style.display = 'block';
                        statusDiv.innerText = 'Status: Scanning...';
                        resultsDiv.innerHTML = '';
                        
                        callService('duplicate_video_finder', 'start_scan', {{}})
                            .catch(error => {{
                                console.error('Error starting scan:', error);
                                statusDiv.innerText = 'Status: Error starting scan';
                                startButton.disabled = false;
                                loadingDiv.style.display = 'none';
                            }});
                    }});
                    
                    function updateUIFromState(state) {{
                        if (!state) return;
                        
                        const attributes = state.attributes || {{}};
                        const scanState = attributes.scan_state || 'idle';
                        const lastScan = attributes.last_scan || 'Never';
                        const duplicates = attributes.duplicates || [];
                        
                        // Update status
                        statusDiv.innerText = 'Status: ' + (scanState === 'scanning' ? 'Scanning...' : 'Ready');
                        lastScanDiv.innerText = 'Last scan: ' + lastScan;
                        
                        // Update button and loading state
                        startButton.disabled = scanState === 'scanning';
                        loadingDiv.style.display = scanState === 'scanning' ? 'block' : 'none';
                        
                        // Only update results if we're not scanning
                        if (scanState !== 'scanning') {{
                            displayResults(duplicates);
                        }}
                    }}
                    
                    function displayResults(duplicates) {{
                        resultsDiv.innerHTML = '';
                        
                        if (duplicates.length === 0) {{
                            resultsDiv.innerHTML = '<p>No duplicate videos found.</p>';
                            return;
                        }}
                        
                        const countText = document.createElement('p');
                        countText.innerText = `Found ${duplicates.length} sets of duplicate videos.`;
                        resultsDiv.appendChild(countText);
                        
                        duplicates.forEach((dup, index) => {{
                            const dupItem = document.createElement('div');
                            dupItem.className = 'duplicate-item';
                            
                            const dupHeader = document.createElement('div');
                            dupHeader.className = 'duplicate-header';
                            dupHeader.innerHTML = `
                                <div>${dup.name || 'Unnamed Video'}</div>
                                <div>${dup.count || dup.paths.length} copies</div>
                            `;
                            
                            const dupDetails = document.createElement('div');
                            dupDetails.className = 'duplicate-details';
                            dupDetails.id = `duplicate-${index}`;
                            
                            // Add the paths
                            const pathList = document.createElement('ul');
                            pathList.className = 'path-list';
                            dup.paths.forEach(path => {{
                                const li = document.createElement('li');
                                li.innerText = path;
                                pathList.appendChild(li);
                            }});
                            
                            dupDetails.appendChild(pathList);
                            
                            // Toggle visibility on click
                            dupHeader.addEventListener('click', function() {{
                                dupDetails.classList.toggle('visible');
                            }});
                            
                            dupItem.appendChild(dupHeader);
                            dupItem.appendChild(dupDetails);
                            resultsDiv.appendChild(dupItem);
                        }});
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return html
