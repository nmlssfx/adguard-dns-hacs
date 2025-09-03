"""Config flow for AdGuard DNS integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CLIENT_ID, OAUTH_URL, SCOPES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def get_tokens_from_credentials(
    hass: HomeAssistant, username: str, password: str
) -> dict[str, str]:
    """Get access and refresh tokens from username and password."""
    session = async_get_clientsession(hass)
    
    # OAuth2 token request
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": "",  # Public client, no secret required
        "username": username,
        "password": password,
        "scope": " ".join(SCOPES),
    }
    
    try:
        async with session.post(OAUTH_URL, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                return {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data["refresh_token"],
                }
            else:
                error_text = await response.text()
                _LOGGER.error("OAuth2 error: %s - %s", response.status, error_text)
                raise InvalidAuth
    except aiohttp.ClientError as err:
        _LOGGER.error("Network error during authentication: %s", err)
        raise CannotConnect from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AdGuard DNS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                tokens = await get_tokens_from_credentials(
                    self.hass, user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                
                await self.async_set_unique_id(user_input[CONF_USERNAME])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"AdGuard DNS ({user_input[CONF_USERNAME]})",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                    },
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """AdGuard DNS options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "update_interval",
                        default=self.config_entry.options.get("update_interval", 300),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""