"""Create a sidebar menu item for the Duplicate Video Finder."""

import logging
import os
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


def setup_sidebar(hass: HomeAssistant) -> None:
    """Set up a sidebar menu item for Duplicate Video Finder."""
    # This method is more reliable than using panel_iframe for registration
    # It directly adds the sidebar menu item
    
    # First make sure we have a path for our custom panel
    root_path = os.path.dirname(__file__)
    panel_path = os.path.join(root_path, "panels", "panel.html")
    
    # Ensure the panels directory exists
    os.makedirs(os.path.join(root_path, "panels"), exist_ok=True)
    
    # Create a static panel HTML file if it doesn't exist
    if not os.path.exists(panel_path):
        with open(panel_path, "w") as f:
            f.write(_generate_panel_html())
    
    # Register the static path for the panel
    hass.http.register_static_path(
        "/duplicate_video_finder_static",
        os.path.join(root_path, "panels"),
        True
    )
    
    # Register the sidebar panel
    hass.components.frontend.async_register_built_in_panel(
        "iframe",
        "Duplicate Videos",
        "mdi:video-multiple",
        "duplicate_video_finder",
        {"url": "/duplicate_video_finder_static/panel.html"},
        require_admin=False,
    )
    
    _LOGGER.info("Duplicate Video Finder sidebar menu has been registered")


def _generate_panel_html() -> str:
    """Generate the HTML for the panel."""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Duplicate Video Finder</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 16px;
            color: #212121;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 24px;
            margin-bottom: 24px;
        }
        h1 {
            margin-top: 0;
            margin-bottom: 16px;
            font-size: 24px;
            font-weight: 500;
        }
        button {
            background-color: #03a9f4;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #0288d1;
        }
        button:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
            cursor: not-allowed;
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            margin-bottom: 16px;
            font-size: 14px;
            color: #616161;
        }
        .loading {
            display: none;
            margin: 20px 0;
            text-align: center;
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 4px solid #03a9f4;
            width: 30px;
            height: 30px;
            animation: spin 2s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .duplicate-list {
            margin-top: 24px;
        }
        .duplicate-item {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-bottom: 8px;
            overflow: hidden;
        }
        .duplicate-header {
            background-color: #f5f5f5;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            cursor: pointer;
        }
        .duplicate-details {
            padding: 0 16px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }
        .duplicate-details.visible {
            max-height: 500px;
            padding: 12px 16px;
        }
        .path-list {
            margin: 0;
            padding-left: 20px;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>Duplicate Video Finder</h1>
            <div class="status-bar">
                <div id="status">Status: Ready</div>
                <div id="lastScan">Last scan: Never</div>
            </div>
            <button id="startScan">Start Scan</button>
            <div id="loading" class="loading">
                <p>Scanning for duplicate videos. This may take a while depending on your file system size...</p>
                <div class="spinner"></div>
                <p id="progressText"></p>
            </div>
            <div id="results"></div>
        </div>
    </div>
    
    <script>
        // Helper function to communicate with Home Assistant
        function callService(domain, service, data) {
            return fetch('/api/services/' + domain + '/' + service, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + getToken()
                },
                body: JSON.stringify(data || {}),
            });
        }
        
        // Get authentication token from localStorage
        function getToken() {
            return localStorage.getItem('hassTokens') ? 
                JSON.parse(localStorage.getItem('hassTokens')).access_token : '';
        }
        
        // Get state of entity
        function getState(entityId) {
            return fetch('/api/states/' + entityId, {
                headers: {
                    'Authorization': 'Bearer ' + getToken()
                }
            }).then(response => response.json());
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            const startButton = document.getElementById('startScan');
            const loadingDiv = document.getElementById('loading');
            const resultsDiv = document.getElementById('results');
            const statusDiv = document.getElementById('status');
            const lastScanDiv = document.getElementById('lastScan');
            const progressText = document.getElementById('progressText');
            const entityId = 'sensor.duplicate_video_finder';
            let pollInterval;
            
            // Check initial state
            getState(entityId).then(state => {
                if (state) {
                    updateUIFromState(state);
                } else {
                    statusDiv.innerText = 'Status: Integration not found';
                    startButton.disabled = true;
                }
            }).catch(error => {
                console.error('Error getting state:', error);
                statusDiv.innerText = 'Status: Error connecting to Home Assistant';
                startButton.disabled = true;
            });
            
            // Set up polling for updates (since EventSource may not work in iframes)
            function startPolling() {
                if (pollInterval) clearInterval(pollInterval);
                
                pollInterval = setInterval(() => {
                    getState(entityId).then(state => {
                        if (state) updateUIFromState(state);
                    }).catch(error => {
                        console.error('Error polling state:', error);
                    });
                }, 2000); // Poll every 2 seconds
            }
            
            startPolling();
            
            // Handle start scan button
            startButton.addEventListener('click', function() {
                startButton.disabled = true;
                loadingDiv.style.display = 'block';
                statusDiv.innerText = 'Status: Scanning...';
                resultsDiv.innerHTML = '';
                
                callService('duplicate_video_finder', 'start_scan', {})
                    .then(() => {
                        console.log('Scan started successfully');
                        // Make sure polling is active
                        startPolling();
                    })
                    .catch(error => {
                        console.error('Error starting scan:', error);
                        statusDiv.innerText = 'Status: Error starting scan';
                        startButton.disabled = false;
                        loadingDiv.style.display = 'none';
                    });
            });
            
            function updateUIFromState(state) {
                if (!state) return;
                
                const attributes = state.attributes || {};
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
                if (scanState !== 'scanning') {
                    displayResults(duplicates);
                    
                    // If polling interval is less frequent, increase it when idle
                    if (pollInterval) clearInterval(pollInterval);
                    pollInterval = setInterval(() => {
                        getState(entityId).then(state => {
                            if (state) updateUIFromState(state);
                        }).catch(error => {
                            console.error('Error polling state:', error);
                        });
                    }, 5000); // Poll less frequently when idle
                } else {
                    // Poll more frequently during scanning
                    startPolling();
                }
            }
            
            function displayResults(duplicates) {
                resultsDiv.innerHTML = '';
                
                if (!duplicates || duplicates.length === 0) {
                    resultsDiv.innerHTML = '<p>No duplicate videos found.</p>';
                    return;
                }
                
                const countText = document.createElement('p');
                countText.innerText = `Found ${duplicates.length} sets of duplicate videos.`;
                resultsDiv.appendChild(countText);
                
                const duplicateList = document.createElement('div');
                duplicateList.className = 'duplicate-list';
                
                duplicates.forEach((dup, index) => {
                    const dupItem = document.createElement('div');
                    dupItem.className = 'duplicate-item';
                    
                    const dupHeader = document.createElement('div');
                    dupHeader.className = 'duplicate-header';
                    dupHeader.innerHTML = `
                        <div>${dup.name || 'Unnamed Video'}</div>
                        <div>${dup.count || (dup.paths ? dup.paths.length : 0)} copies</div>
                    `;
                    
                    const dupDetails = document.createElement('div');
                    dupDetails.className = 'duplicate-details';
                    dupDetails.id = `duplicate-${index}`;
                    
                    // Add the paths
                    if (dup.paths && dup.paths.length > 0) {
                        const pathList = document.createElement('ul');
                        pathList.className = 'path-list';
                        dup.paths.forEach(path => {
                            const li = document.createElement('li');
                            li.innerText = path;
                            pathList.appendChild(li);
                        });
                        dupDetails.appendChild(pathList);
                    } else {
                        const noPath = document.createElement('p');
                        noPath.innerText = 'No path information available.';
                        dupDetails.appendChild(noPath);
                    }
                    
                    // Toggle visibility on click
                    dupHeader.addEventListener('click', function() {
                        dupDetails.classList.toggle('visible');
                    });
                    
                    dupItem.appendChild(dupHeader);
                    dupItem.appendChild(dupDetails);
                    duplicateList.appendChild(dupItem);
                });
                
                resultsDiv.appendChild(duplicateList);
            }
        });
    </script>
</body>
</html>
    """
