""""Starting setup task: Verify API"."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from ..base import HacsBase
from ..enums import HacsStage
from .base import HacsTask


async def async_setup_task(hacs: HacsBase, hass: HomeAssistant) -> Task:
    """Set up this task."""
    return Task(hacs=hacs, hass=hass)


class Task(HacsTask):
    """Verify the connection to the GitHub API."""

    stages = [HacsStage.SETUP]

    async def async_execute(self) -> None:
        can_update = await self.hacs.async_can_update()
        self.log.debug("Can update %s repositories", can_update)
