"""Device tracker platform for AdGuard DNS."""
from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AdGuardDNSConfigEntry
from .const import DOMAIN
from .coordinator import AdGuardDNSDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AdGuardDNSConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AdGuard DNS device tracker based on a config entry."""
    coordinator = entry.runtime_data

    # Wait for initial data
    if not coordinator.data:
        return

    entities = []
    devices_data = coordinator.data.get("devices", {})
    devices_list = devices_data.get("devices", [])
    
    for device in devices_list:
        device_id = device.get("id")
        if device_id:
            entities.append(AdGuardDNSDeviceTracker(coordinator, device_id))

    async_add_entities(entities)


class AdGuardDNSDeviceTracker(CoordinatorEntity[AdGuardDNSDataUpdateCoordinator], TrackerEntity):
    """Representation of an AdGuard DNS device tracker."""

    def __init__(
        self,
        coordinator: AdGuardDNSDataUpdateCoordinator,
        device_id: str,
    ) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{DOMAIN}_device_{device_id}"
        
        # Get device info for name
        device_info = self._get_device_info()
        device_name = device_info.get("name", f"Device {device_id}")
        self._attr_name = f"AdGuard DNS {device_name}"

    def _get_device_info(self) -> dict[str, Any]:
        """Get device information from coordinator data."""
        if not self.coordinator.data:
            return {}
        
        devices_data = self.coordinator.data.get("devices", {})
        devices_list = devices_data.get("devices", [])
        
        for device in devices_list:
            if device.get("id") == self._device_id:
                return device
        
        return {}

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        device_data = self._get_device_info()
        device_name = device_data.get("name", f"Device {self._device_id}")
        
        return {
            "identifiers": {(DOMAIN, f"device_{self._device_id}")},
            "name": device_name,
            "manufacturer": "AdGuard DNS",
            "model": "Tracked Device",
            "via_device": (DOMAIN, "adguard_dns"),
        }

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device."""
        return SourceType.ROUTER

    @property
    def is_connected(self) -> bool:
        """Return true if the device is connected."""
        device_info = self._get_device_info()
        # Consider device connected if it has recent activity
        # This is a simplified check - you might want to implement more sophisticated logic
        return device_info.get("status", "active") == "active"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes."""
        device_info = self._get_device_info()
        if not device_info:
            return None

        attributes = {
            "device_id": self._device_id,
            "device_name": device_info.get("name", "Unknown"),
        }
        
        # Add optional attributes if available
        if "linked_ip" in device_info:
            attributes["linked_ip"] = device_info["linked_ip"]
        
        if "dns_servers" in device_info:
            attributes["dns_servers"] = device_info["dns_servers"]
        
        if "filtering_enabled" in device_info:
            attributes["filtering_enabled"] = device_info["filtering_enabled"]
        
        # Add statistics if available from device info
        if "statistics" in device_info:
            device_stats = device_info["statistics"]
            attributes["queries_count"] = device_stats.get("queries_count", 0)
            attributes["blocked_count"] = device_stats.get("blocked_count", 0)
            
            queries = device_stats.get("queries_count", 0)
            blocked = device_stats.get("blocked_count", 0)
            if queries > 0:
                attributes["blocked_percentage"] = round((blocked / queries) * 100, 2)
            else:
                attributes["blocked_percentage"] = 0
        
        # Add settings if available
        if "settings" in device_info:
            device_settings = device_info["settings"]
            attributes["protection_enabled"] = device_settings.get("protection_enabled", True)
            attributes["safe_browsing_enabled"] = device_settings.get("safe_browsing_enabled", True)
            attributes["adult_content_enabled"] = device_settings.get("adult_content_enabled", False)
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon for the device tracker."""
        if self.is_connected:
            return "mdi:router-wireless"
        return "mdi:router-wireless-off"