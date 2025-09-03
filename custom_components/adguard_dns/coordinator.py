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
    CLIENT_ID,
    DOMAIN,
    OAUTH_URL,
    SCOPES,
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
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": "",
            "refresh_token": self.refresh_token,
            "scope": " ".join(SCOPES),
        }

        try:
            async with self.session.post(OAUTH_URL, data=data) as response:
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

    async def _fetch_stats_time(self) -> dict[str, Any]:
        """Fetch time-based statistics."""
        return await self._api_request(API_ENDPOINTS["stats_time"])

    async def _fetch_stats_domains(self) -> dict[str, Any]:
        """Fetch domain statistics."""
        return await self._api_request(API_ENDPOINTS["stats_domains"])

    async def _fetch_devices_list(self) -> dict[str, Any]:
        """Fetch devices list."""
        return await self._api_request(API_ENDPOINTS["devices"])

    async def _fetch_query_log_summary(self) -> dict[str, Any]:
        """Fetch query log summary for protection status."""
        params = {"limit": 1000}  # Limit for performance
        return await self._api_request(API_ENDPOINTS["query_log"], params)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            # Fetch all data concurrently
            stats_tasks = [
                self._fetch_stats_time(),
                self._fetch_stats_domains(),
                self._fetch_devices_list(),
                self._fetch_query_log_summary(),
            ]
            
            results = await asyncio.gather(*stats_tasks, return_exceptions=True)
            
            data = {}
            
            # Process stats_time
            if isinstance(results[0], dict):
                data["stats_time"] = results[0]
            else:
                _LOGGER.warning("Failed to fetch time stats: %s", results[0])
                data["stats_time"] = {}
            
            # Process stats_domains
            if isinstance(results[1], dict):
                data["stats_domains"] = results[1]
            else:
                _LOGGER.warning("Failed to fetch domain stats: %s", results[1])
                data["stats_domains"] = {}
            
            # Process devices
            if isinstance(results[2], dict):
                data["devices"] = results[2]
            else:
                _LOGGER.warning("Failed to fetch devices: %s", results[2])
                data["devices"] = {}
            
            # Process query log
            if isinstance(results[3], dict):
                data["query_log"] = results[3]
                # Determine protection status from query log
                query_log_data = results[3].get("query_log", [])
                blocked_count = sum(1 for entry in query_log_data if entry.get("status") == "blocked")
                total_count = len(query_log_data)
                data["protection_enabled"] = blocked_count > 0 if total_count > 0 else True
            else:
                _LOGGER.warning("Failed to fetch query log: %s", results[3])
                data["query_log"] = {}
                data["protection_enabled"] = True  # Default to enabled
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def clear_query_log(self) -> bool:
        """Clear the query log."""
        try:
            await self._ensure_valid_token()
            
            url = f"{API_BASE_URL}/v1/query_log/clear"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            
            async with self.session.delete(url, headers=headers) as response:
                if response.status in (200, 204):
                    _LOGGER.info("Query log cleared successfully")
                    # Trigger a data refresh
                    await self.async_request_refresh()
                    return True
                else:
                    error_text = await response.text()
                    _LOGGER.error(
                        "Failed to clear query log: %s - %s", response.status, error_text
                    )
                    return False
        except Exception as err:
            _LOGGER.error("Error clearing query log: %s", err)
            return False