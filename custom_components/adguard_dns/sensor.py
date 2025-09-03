"""Sensor platform for AdGuard DNS."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdGuardDNSConfigEntry
from .const import DOMAIN, SENSOR_TYPES
from .coordinator import AdGuardDNSDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdGuardDNSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AdGuard DNS sensor based on a config entry."""
    coordinator = entry.runtime_data

    entities = []
    for sensor_type in SENSOR_TYPES:
        entities.append(AdGuardDNSSensor(coordinator, sensor_type))

    async_add_entities(entities)


class AdGuardDNSSensor(CoordinatorEntity[AdGuardDNSDataUpdateCoordinator], SensorEntity):
    """Representation of an AdGuard DNS sensor."""

    def __init__(
        self,
        coordinator: AdGuardDNSDataUpdateCoordinator,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = SENSOR_TYPES[sensor_type]["name"]
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_icon = SENSOR_TYPES[sensor_type]["icon"]
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type]["unit"]
        
        if SENSOR_TYPES[sensor_type]["device_class"]:
            self._attr_device_class = SensorDeviceClass(SENSOR_TYPES[sensor_type]["device_class"])
        
        if SENSOR_TYPES[sensor_type]["state_class"]:
            self._attr_state_class = SensorStateClass(SENSOR_TYPES[sensor_type]["state_class"])

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
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        if self._sensor_type == "total_queries":
            stats_time = self.coordinator.data.get("stats_time", {})
            return sum(stats_time.get("time_units", {}).values())
        
        elif self._sensor_type == "blocked_queries":
            stats_time = self.coordinator.data.get("stats_time", {})
            time_units = stats_time.get("time_units", {})
            blocked_units = stats_time.get("blocked_time_units", {})
            return sum(blocked_units.values())
        
        elif self._sensor_type == "blocked_percentage":
            stats_time = self.coordinator.data.get("stats_time", {})
            time_units = stats_time.get("time_units", {})
            blocked_units = stats_time.get("blocked_time_units", {})
            
            total = sum(time_units.values())
            blocked = sum(blocked_units.values())
            
            if total > 0:
                return round((blocked / total) * 100, 2)
            return 0
        
        elif self._sensor_type == "top_blocked_domain":
            stats_domains = self.coordinator.data.get("stats_domains", {})
            blocked_domains = stats_domains.get("blocked_domains", [])
            if blocked_domains:
                return blocked_domains[0].get("domain", "N/A")
            return "N/A"
        
        elif self._sensor_type == "top_queried_domain":
            stats_domains = self.coordinator.data.get("stats_domains", {})
            queried_domains = stats_domains.get("queried_domains", [])
            if queried_domains:
                return queried_domains[0].get("domain", "N/A")
            return "N/A"
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attributes = {}
        
        if self._sensor_type in ["total_queries", "blocked_queries", "blocked_percentage"]:
            stats_time = self.coordinator.data.get("stats_time", {})
            attributes["time_units"] = stats_time.get("time_units", {})
            attributes["blocked_time_units"] = stats_time.get("blocked_time_units", {})
        
        elif self._sensor_type == "top_blocked_domain":
            stats_domains = self.coordinator.data.get("stats_domains", {})
            blocked_domains = stats_domains.get("blocked_domains", [])
            if blocked_domains:
                top_domain = blocked_domains[0]
                attributes["query_count"] = top_domain.get("query_count", 0)
                attributes["top_10_blocked"] = [d.get("domain") for d in blocked_domains[:10]]
        
        elif self._sensor_type == "top_queried_domain":
            stats_domains = self.coordinator.data.get("stats_domains", {})
            queried_domains = stats_domains.get("queried_domains", [])
            if queried_domains:
                top_domain = queried_domains[0]
                attributes["query_count"] = top_domain.get("query_count", 0)
                attributes["top_10_queried"] = [d.get("domain") for d in queried_domains[:10]]
        
        return attributes if attributes else None