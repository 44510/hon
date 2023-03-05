import logging
from datetime import timedelta

from pyhon.device import HonDevice

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HonEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, hass, entry, coordinator, device: HonDevice) -> None:
        super().__init__(coordinator)

        self._hon = hass.data[DOMAIN][entry.unique_id]
        self._hass = hass
        self._device = device

        self._attr_unique_id = self._device.mac_address

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.mac_address)},
            manufacturer=self._device.brand,
            name=self._device.nick_name if self._device.nick_name else self._device.model_name,
            model=self._device.model_name,
            sw_version=self._device.fw_version,
        )


class HonCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, device: HonDevice):
        """Initialize my coordinator."""
        super().__init__(hass, _LOGGER, name=device.mac_address, update_interval=timedelta(seconds=30))
        self._device = device

    async def _async_update_data(self):
        await self._device.update()
