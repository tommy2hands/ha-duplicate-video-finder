"""Navigation configuration for Duplicate Video Finder."""

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_component import EntityComponent

from .const import DOMAIN


@callback
async def async_register_panel(hass: HomeAssistant) -> None:
    """Register a panel in the frontend for Duplicate Video Finder."""
    # Add Duplicate Video Finder to the sidebar
    hass.components.frontend.async_register_built_in_panel(
        "custom",
        "Duplicate Videos",
        "mdi:video-multiple",
        "duplicate-video-finder",
        require_admin=False,
    )
    
    # Register a custom frontend panel card resource
    resource_url = "/dvf-panel/duplicate-video-finder-panel.js"
    hass.http.register_static_path(
        resource_url,
        hass.config.path("custom_components", DOMAIN, "frontend", "duplicate-video-finder-panel.js"),
        True
    )
    
    add_extra_js_url(hass, resource_url)
