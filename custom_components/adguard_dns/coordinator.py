"""Data update coordinator for AdGuard DNS."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_BASE_URL,
    API_ENDPOINTS,
    DOMAIN,
    OAUTH_URL,
)

_LOGGER = logging.getLogger(__name__)


class AdGuardDNSDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the AdGuard DNS API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        access_token: str,
        refresh_token: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.session = session
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._token_expires_at: datetime | None = None

    async def _refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token."""
        data = {
            "refresh_token": self.refresh_token,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            async with self.session.post(OAUTH_URL, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    if "refresh_token" in token_data:
                        self.refresh_token = token_data["refresh_token"]
                    # Set token expiration (typically 1 hour)
                    self._token_expires_at = datetime.now() + timedelta(
                        seconds=token_data.get("expires_in", 3600)
                    )
                    _LOGGER.debug("Access token refreshed successfully")
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "Failed to refresh token: %s - %s", response.status, error_text
                    )
                    raise UpdateFailed(f"Failed to refresh token: {response.status}")
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error during token refresh: %s", err)
            raise UpdateFailed(f"Network error during token refresh: {err}") from err

    async def _ensure_valid_token(self) -> None:
        """Ensure we have a valid access token."""
        if (
            self._token_expires_at is None
            or datetime.now() >= self._token_expires_at - timedelta(minutes=5)
        ):
            await self._refresh_access_token()

    async def _api_request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an API request to AdGuard DNS."""
        await self._ensure_valid_token()
        
        url = f"{API_BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Token might be invalid, try refreshing once
                    await self._refresh_access_token()
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    async with self.session.get(url, headers=headers, params=params) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            error_text = await retry_response.text()
                            _LOGGER.error(
                                "API request failed after token refresh: %s - %s",
                                retry_response.status,
                                error_text,
                            )
                            raise UpdateFailed(f"API request failed: {retry_response.status}")
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "API request failed: %s - %s", response.status, error_text
                    )
                    raise UpdateFailed(f"API request failed: {response.status}")
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error during API request: %s", err)
            raise UpdateFailed(f"Network error: {err}") from err

    async def _fetch_account_limits(self) -> dict[str, Any]:
        """Fetch account limits."""
        return await self._api_request(API_ENDPOINTS["account_limits"])

    async def _fetch_devices_list(self) -> dict[str, Any]:
        """Fetch devices list."""
        return await self._api_request(API_ENDPOINTS["devices"])

    async def _fetch_dns_servers(self) -> dict[str, Any]:
        """Fetch DNS servers list."""
        return await self._api_request(API_ENDPOINTS["dns_servers"])

    async def _fetch_dedicated_addresses(self) -> dict[str, Any]:
        """Fetch dedicated IPv4 addresses."""
        return await self._api_request(API_ENDPOINTS["dedicated_addresses"])

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            # Fetch all data concurrently
            api_tasks = [
                self._fetch_account_limits(),
                self._fetch_devices_list(),
                self._fetch_dns_servers(),
                self._fetch_dedicated_addresses(),
            ]
            
            results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            data = {}
            
            # Process account limits
            if isinstance(results[0], dict):
                data["account_limits"] = results[0]
            else:
                _LOGGER.warning("Failed to fetch account limits: %s", results[0])
                data["account_limits"] = {}
            
            # Process devices
            if isinstance(results[1], dict):
                data["devices"] = results[1]
                # Calculate basic stats from devices
                devices_list = results[1].get("devices", [])
                data["total_queries"] = sum(device.get("queries_count", 0) for device in devices_list)
                data["blocked_queries"] = sum(device.get("blocked_count", 0) for device in devices_list)
                if data["total_queries"] > 0:
                    data["blocked_percentage"] = round((data["blocked_queries"] / data["total_queries"]) * 100, 2)
                else:
                    data["blocked_percentage"] = 0
            else:
                _LOGGER.warning("Failed to fetch devices: %s", results[1])
                data["devices"] = {}
                data["total_queries"] = 0
                data["blocked_queries"] = 0
                data["blocked_percentage"] = 0
            
            # Process DNS servers
            if isinstance(results[2], dict):
                data["dns_servers"] = results[2]
                # Determine protection status from DNS servers
                dns_servers = results[2].get("dns_servers", [])
                data["protection_enabled"] = any(server.get("settings", {}).get("protection_enabled", False) for server in dns_servers)
            else:
                _LOGGER.warning("Failed to fetch DNS servers: %s", results[2])
                data["dns_servers"] = {}
                data["protection_enabled"] = True  # Default to enabled
            
            # Process dedicated addresses
            if isinstance(results[3], dict):
                data["dedicated_addresses"] = results[3]
            else:
                _LOGGER.warning("Failed to fetch dedicated addresses: %s", results[3])
                data["dedicated_addresses"] = {}
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err