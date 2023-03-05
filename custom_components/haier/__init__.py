import logging

import voluptuous as vol
from pyhon import HonConnection

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import config_validation as cv, aiohttp_client
from homeassistant.helpers.typing import HomeAssistantType

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


HON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [HON_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry):
    session = aiohttp_client.async_get_clientsession(hass)
    hon = HonConnection(entry.data["email"], entry.data["password"], session)
    await hon.setup()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.unique_id] = hon
    hass.data[DOMAIN]["coordinators"] = {}

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    return True


async def async_unload_entry(hass, entry: ConfigEntry) -> bool:
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
    return unload
