"""The Duplicate Video Finder integration."""
import logging
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    SERVICE_START_SCAN,
    EVENT_SCAN_STARTED,
    EVENT_SCAN_COMPLETED,
    EVENT_SCAN_ERROR,
    STATE_IDLE,
    STATE_SCANNING,
)
from .scanner import DuplicateVideoScanner
from .frontend import async_setup_frontend

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Duplicate Video Finder component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Duplicate Video Finder from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create scanner instance
    scanner = DuplicateVideoScanner(hass)
    hass.data[DOMAIN][entry.entry_id] = {
        "scanner": scanner,
        "state": STATE_IDLE,
        "duplicates": [],
    }
    
    # Register services
    async def start_scan_service(call: ServiceCall) -> None:
        """Start scanning for duplicate videos."""
        await _start_scan(hass, entry.entry_id)
    
    hass.services.async_register(
        DOMAIN, SERVICE_START_SCAN, start_scan_service
    )
    
    # Set up frontend
    await async_setup_frontend(hass)
    
    # Set up sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove services
    hass.services.async_remove(DOMAIN, SERVICE_START_SCAN)
    
    # Unload sensor platform
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    
    # Cleanup
    hass.data[DOMAIN].pop(entry.entry_id)
    
    return True


async def _start_scan(hass: HomeAssistant, entry_id: str) -> None:
    """Start scanning process."""
    data = hass.data[DOMAIN][entry_id]
    scanner = data["scanner"]
    
    # Avoid starting a new scan if one is already in progress
    if data["state"] == STATE_SCANNING:
        _LOGGER.warning("A scan is already in progress")
        return
    
    # Update state
    data["state"] = STATE_SCANNING
    data["duplicates"] = []
    
    # Fire event
    hass.bus.async_fire(EVENT_SCAN_STARTED)
    
    try:
        # Start the scan
        _LOGGER.info("Starting scan for duplicate videos")
        result = await scanner.scan()
        
        # Store results
        data["duplicates"] = result
        data["state"] = STATE_IDLE
        
        # Fire completion event
        hass.bus.async_fire(
            EVENT_SCAN_COMPLETED,
            {"duplicates_count": len(result)}
        )
        _LOGGER.info(f"Scan completed, found {len(result)} duplicate sets")
        
    except Exception as exc:
        data["state"] = STATE_IDLE
        _LOGGER.error(f"Error during scan: {exc}")
        hass.bus.async_fire(EVENT_SCAN_ERROR, {"error": str(exc)})
