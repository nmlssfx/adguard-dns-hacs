"""Binary sensor platform for AdGuard DNS."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdGuardDNSConfigEntry
from .const import BINARY_SENSOR_TYPES, DOMAIN
from .coordinator import AdGuardDNSDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdGuardDNSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AdGuard DNS binary sensor based on a config entry."""
    coordinator = entry.runtime_data

    entities = []
    for sensor_type in BINARY_SENSOR_TYPES:
        entities.append(AdGuardDNSBinarySensor(coordinator, sensor_type))

    async_add_entities(entities)


class AdGuardDNSBinarySensor(CoordinatorEntity[AdGuardDNSDataUpdateCoordinator], BinarySensorEntity):
    """Representation of an AdGuard DNS binary sensor."""

    def __init__(
        self,
        coordinator: AdGuardDNSDataUpdateCoordinator,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = BINARY_SENSOR_TYPES[sensor_type]["name"]
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_icon = BINARY_SENSOR_TYPES[sensor_type]["icon"]
        
        if BINARY_SENSOR_TYPES[sensor_type]["device_class"]:
            self._attr_device_class = BinarySensorDeviceClass(
                BINARY_SENSOR_TYPES[sensor_type]["device_class"]
            )

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

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return None

        if self._sensor_type == "protection_enabled":
            return self.coordinator.data.get("protection_enabled", True)
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attributes = {}
        
        if self._sensor_type == "protection_enabled":
            query_log = self.coordinator.data.get("query_log", {})
            query_log_data = query_log.get("query_log", [])
            
            if query_log_data:
                total_queries = len(query_log_data)
                blocked_queries = sum(1 for entry in query_log_data if entry.get("status") == "blocked")
                
                attributes["total_recent_queries"] = total_queries
                attributes["blocked_recent_queries"] = blocked_queries
                attributes["recent_block_rate"] = (
                    round((blocked_queries / total_queries) * 100, 2) if total_queries > 0 else 0
                )
        
        return attributes if attributes else None