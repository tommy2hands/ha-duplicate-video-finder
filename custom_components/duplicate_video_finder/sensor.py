"""Sensor platform for duplicate video finder."""
import logging
import os
from typing import Any, Callable, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import UpdateCoordinator

from .const import DOMAIN, EVENT_SCAN_COMPLETED, EVENT_SCAN_ERROR, STATE_IDLE, STATE_SCANNING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the duplicate video finder sensor."""
    sensor = DuplicateVideoFinderSensor(hass, entry.entry_id)
    async_add_entities([sensor], True)


class DuplicateVideoFinderSensor(SensorEntity):
    """Sensor that displays information about duplicate videos."""

    def __init__(self, hass: HomeAssistant, entry_id: str):
        """Initialize the sensor."""
        self.hass = hass
        self.entry_id = entry_id
        self._attr_name = "Duplicate Video Finder"
        self._attr_unique_id = f"{entry_id}_duplicate_videos"
        self._attr_icon = "mdi:movie-duplicate"
        self._attr_extra_state_attributes = {
            "duplicates": [],
            "last_scan": None,
            "scan_state": STATE_IDLE
        }
        
    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        # Listen for scan events
        @callback
        def handle_scan_event(event):
            """Handle scan events."""
            self._handle_scan_update()
            self.async_write_ha_state()
            
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_SCAN_COMPLETED, handle_scan_event)
        )
        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_SCAN_ERROR, handle_scan_event)
        )

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        domain_data = self.hass.data[DOMAIN].get(self.entry_id, {})
        scan_state = domain_data.get("state", STATE_IDLE)
        
        if scan_state == STATE_SCANNING:
            return "scanning"
        
        duplicates = domain_data.get("duplicates", [])
        return str(len(duplicates))
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.entry_id in self.hass.data.get(DOMAIN, {})
    
    def _handle_scan_update(self) -> None:
        """Update sensor attributes when scan completes."""
        domain_data = self.hass.data[DOMAIN].get(self.entry_id, {})
        
        # Retrieve duplicates from domain data
        duplicates = domain_data.get("duplicates", [])
        
        # Format the duplicates for better display
        formatted_duplicates = []
        for i, duplicate_set in enumerate(duplicates):
            formatted_duplicates.append({
                "id": i,
                "name": os.path.basename(duplicate_set[0]),
                "count": len(duplicate_set),
                "paths": duplicate_set
            })
        
        # Update attributes
        self._attr_extra_state_attributes.update({
            "duplicates": formatted_duplicates,
            "last_scan": self.hass.states.get("sensor.date_time").state,
            "scan_state": domain_data.get("state", STATE_IDLE)
        })
