"""Button platform for AdGuard DNS."""
from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdGuardDNSConfigEntry
from .const import BUTTON_TYPES, DOMAIN
from .coordinator import AdGuardDNSDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdGuardDNSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AdGuard DNS button based on a config entry."""
    coordinator = entry.runtime_data

    entities = []
    for button_type in BUTTON_TYPES:
        entities.append(AdGuardDNSButton(coordinator, button_type))

    async_add_entities(entities)


class AdGuardDNSButton(CoordinatorEntity[AdGuardDNSDataUpdateCoordinator], ButtonEntity):
    """Representation of an AdGuard DNS button."""

    def __init__(
        self,
        coordinator: AdGuardDNSDataUpdateCoordinator,
        button_type: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._button_type = button_type
        self._attr_name = BUTTON_TYPES[button_type]["name"]
        self._attr_unique_id = f"{DOMAIN}_{button_type}"
        self._attr_icon = BUTTON_TYPES[button_type]["icon"]

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "adguard_dns")},
            "name": "AdGuard DNS",
            "manufacturer": "AdGuard",
            "model": "DNS Service",
            "sw_version": "1.0",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        if self._button_type == "clear_query_log":
            success = await self.coordinator.clear_query_log()
            if success:
                self.hass.components.persistent_notification.async_create(
                    "Query log has been cleared successfully.",
                    title="AdGuard DNS",
                    notification_id="adguard_dns_clear_log",
                )
            else:
                self.hass.components.persistent_notification.async_create(
                    "Failed to clear query log. Please check your connection and try again.",
                    title="AdGuard DNS Error",
                    notification_id="adguard_dns_clear_log_error",
                )