"""The AdGuard DNS integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS
from .coordinator import AdGuardDNSDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

type AdGuardDNSConfigEntry = ConfigEntry[AdGuardDNSDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AdGuardDNSConfigEntry) -> bool:
    """Set up AdGuard DNS from a config entry."""
    session = async_get_clientsession(hass)
    
    coordinator = AdGuardDNSDataUpdateCoordinator(
        hass=hass,
        session=session,
        access_token=entry.data["access_token"],
        refresh_token=entry.data["refresh_token"],
        update_interval=timedelta(seconds=entry.options.get("update_interval", 300)),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: AdGuardDNSConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_listener(hass: HomeAssistant, entry: AdGuardDNSConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)