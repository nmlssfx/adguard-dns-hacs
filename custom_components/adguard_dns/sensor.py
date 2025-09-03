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
            return self.coordinator.data.get("total_queries", 0)
        
        elif self._sensor_type == "blocked_queries":
            return self.coordinator.data.get("blocked_queries", 0)
        
        elif self._sensor_type == "blocked_percentage":
            return self.coordinator.data.get("blocked_percentage", 0)
        
        elif self._sensor_type == "top_blocked_domain":
            # Get top blocked domain from devices data
            devices_data = self.coordinator.data.get("devices", {})
            devices_list = devices_data.get("devices", [])
            
            # Collect all blocked domains from all devices
            blocked_domains = {}
            for device in devices_list:
                device_stats = device.get("statistics", {})
                top_blocked = device_stats.get("top_blocked_domains", [])
                for domain_info in top_blocked:
                    domain = domain_info.get("domain", "")
                    count = domain_info.get("count", 0)
                    blocked_domains[domain] = blocked_domains.get(domain, 0) + count
            
            if blocked_domains:
                top_domain = max(blocked_domains.items(), key=lambda x: x[1])
                return top_domain[0]
            return "N/A"
        
        elif self._sensor_type == "top_queried_domain":
            # Get top queried domain from devices data
            devices_data = self.coordinator.data.get("devices", {})
            devices_list = devices_data.get("devices", [])
            
            # Collect all queried domains from all devices
            queried_domains = {}
            for device in devices_list:
                device_stats = device.get("statistics", {})
                top_queried = device_stats.get("top_queried_domains", [])
                for domain_info in top_queried:
                    domain = domain_info.get("domain", "")
                    count = domain_info.get("count", 0)
                    queried_domains[domain] = queried_domains.get(domain, 0) + count
            
            if queried_domains:
                top_domain = max(queried_domains.items(), key=lambda x: x[1])
                return top_domain[0]
            return "N/A"
        
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return None

        attributes = {}
        
        if self._sensor_type in ["total_queries", "blocked_queries", "blocked_percentage"]:
            # Add device count and account limits info
            devices_data = self.coordinator.data.get("devices", {})
            devices_list = devices_data.get("devices", [])
            attributes["active_devices"] = len(devices_list)
            
            account_limits = self.coordinator.data.get("account_limits", {})
            attributes["account_limits"] = account_limits
        
        elif self._sensor_type == "top_blocked_domain":
            devices_data = self.coordinator.data.get("devices", {})
            devices_list = devices_data.get("devices", [])
            
            # Collect all blocked domains from all devices
            blocked_domains = {}
            for device in devices_list:
                device_stats = device.get("statistics", {})
                top_blocked = device_stats.get("top_blocked_domains", [])
                for domain_info in top_blocked:
                    domain = domain_info.get("domain", "")
                    count = domain_info.get("count", 0)
                    blocked_domains[domain] = blocked_domains.get(domain, 0) + count
            
            if blocked_domains:
                # Sort by count and get top 10
                sorted_domains = sorted(blocked_domains.items(), key=lambda x: x[1], reverse=True)
                top_domain = sorted_domains[0]
                attributes["query_count"] = top_domain[1]
                attributes["top_10_blocked"] = [domain for domain, _ in sorted_domains[:10]]
        
        elif self._sensor_type == "top_queried_domain":
            devices_data = self.coordinator.data.get("devices", {})
            devices_list = devices_data.get("devices", [])
            
            # Collect all queried domains from all devices
            queried_domains = {}
            for device in devices_list:
                device_stats = device.get("statistics", {})
                top_queried = device_stats.get("top_queried_domains", [])
                for domain_info in top_queried:
                    domain = domain_info.get("domain", "")
                    count = domain_info.get("count", 0)
                    queried_domains[domain] = queried_domains.get(domain, 0) + count
            
            if queried_domains:
                # Sort by count and get top 10
                sorted_domains = sorted(queried_domains.items(), key=lambda x: x[1], reverse=True)
                top_domain = sorted_domains[0]
                attributes["query_count"] = top_domain[1]
                attributes["top_10_queried"] = [domain for domain, _ in sorted_domains[:10]]
        
        return attributes if attributes else None