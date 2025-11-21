import asyncio
import logging
import re
from html import unescape
from typing import Any, Dict

import aiohttp

_LOGGER = logging.getLogger(__name__)


class BskZephyrApiError(Exception):
    pass


_STATUS_LABEL_RE = re.compile(
    r"<b>\s*([^:<]+):\s*</b>\s*([^<]+)", re.IGNORECASE
)


def _coerce_value(key: str, raw: str) -> Any:
    text = raw.strip()
    num_match = re.search(r"-?\d+(\.\d+)?", text)
    if num_match:
        num = num_match.group(0)
        try:
            return float(num) if "." in num else int(num)
        except ValueError:
            pass
    return text


class BskZephyrClient:
    def __init__(self, ip: str, session: aiohttp.ClientSession):
        self._base_url = f"http://{ip}"
        self._session = session

    async def _request(self, method: str, path: str, **kwargs):
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(method, url, **kwargs) as resp:
                if resp.status != 200:
                    raise BskZephyrApiError(await resp.text())
                text = await resp.text()
                return text
        except Exception as exc:
            raise BskZephyrApiError(str(exc))

    async def get_device_status(self) -> Dict[str, Any]:
        html = await self._request("GET", "/")
        data = {}
        for label, val in _STATUS_LABEL_RE.findall(html):
            key = label.lower().replace(" ", "_")
            data[key] = _coerce_value(key, unescape(val))
        return data

    async def power_on(self):
        await self._request("POST", "/on")

    async def power_off(self):
        await self._request("POST", "/off")

    async def set_fan_speed(self, speed: int):
        await self._request("POST", "/fan", data={"speed": str(speed)})

    async def set_mode_cycle(self):
        await self._request("POST", "/cycle")

    async def set_mode_intake(self):
        await self._request("POST", "/intake")

    async def set_mode_exhaust(self):
        await self._request("POST", "/exhaust")

    async def set_humidity_level(self, level: int):
        await self._request("POST", "/humid", data={"level": str(level)})

    async def set_buzzer_state(self, enable: bool):
        await self._request("POST", "/buzzer", data={"state": "1" if enable else "0"})