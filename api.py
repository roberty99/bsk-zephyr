import asyncio
import logging
import re
from html import unescape
from typing import Any, Dict

import aiohttp

_LOGGER = logging.getLogger(__name__)


class BskZephyrApiError(Exception):
    """Raised when the BSK Zephyr API returns an error."""


# Regex to capture: <b>Label:</b> value
_STATUS_LABEL_RE = re.compile(
    r"<b>\s*([^:<]+):\s*</b>\s*([^<]+)", re.IGNORECASE
)


def _coerce_value(key: str, raw: str) -> Any:
    """Convert '19.71 °C' -> 19.71, '-52 dBm' -> -52, etc."""
    text = raw.strip()
    # Extract first number from the string
    num_match = re.search(r"-?\d+(\.\d+)?", text)
    if num_match:
        num_str = num_match.group(0)
        try:
            if "." in num_str:
                val = float(num_str)
            else:
                val = int(num_str)
        except ValueError:
            val = text
    else:
        val = text

    # For some keys we prefer int/float, others we keep as string
    numeric_keys = {
        "temperature",
        "humidity",
        "fan_speed",
        "set_humidity",
        "humidity_boost",
        "buzzer",
        "filter_timer",
        "hygiene_status",
        "rssi",
    }
    if key in numeric_keys and isinstance(val, (int, float)):
        return val

    return text


class BskZephyrClient:
    def __init__(self, ip: str, session: aiohttp.ClientSession) -> None:
        self._ip = ip
        self._session = session
        self._base_url = f"http://{ip}"

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self._base_url}{path}"
        _LOGGER.debug("Requesting %s %s %s", method, url, kwargs.get("data"))

        try:
            async with self._session.request(method, url, **kwargs) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise BskZephyrApiError(
                        f"Error {resp.status} for {url}: {text}"
                    )

                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return await resp.json()

                return await resp.text()
        except asyncio.TimeoutError as exc:
            raise BskZephyrApiError(f"Timeout calling {url}") from exc
        except aiohttp.ClientError as exc:
            raise BskZephyrApiError(f"Client error calling {url}") from exc

    # ---------- NEW: parse the HTML status page ----------

    async def get_device_status(self) -> Dict[str, Any]:
        """
        Fetch "/" and parse all <b>Label:</b> value pairs into a dict.

        Example keys:
          device_id, version, model, ssid, rssi, ip, power, fan_speed,
          temperature, humidity, operation_mode, set_humidity,
          humidity_boost, buzzer, filter_timer, hygiene_status
        """
        html = await self._request("GET", "/")
        data: Dict[str, Any] = {}

        for label, raw_value in _STATUS_LABEL_RE.findall(html):
            label = label.strip()
            value = unescape(raw_value).strip()
            key = label.lower().replace(" ", "_")  # e.g. "Device ID" -> "device_id"
            data[key] = _coerce_value(key, value)

        _LOGGER.debug("Parsed status data: %s", data)
        return data

    # ---------- existing control methods ----------

    async def power_on(self) -> None:
        await self._request("POST", "/on")

    async def power_off(self) -> None:
        await self._request("POST", "/off")

    async def set_fan_speed(self, speed: int) -> None:
        """Speed in the device’s 22–80 range, sent as form data."""
        await self._request("POST", "/fan", data={"speed": str(speed)})

    async def set_mode_cycle(self) -> None:
        await self._request("POST", "/cycle")

    async def set_mode_intake(self) -> None:
        await self._request("POST", "/intake")

    async def set_mode_exhaust(self) -> None:
        await self._request("POST", "/exhaust")

    async def set_humidity_level(self, level: int) -> None:
        """Set target humidity: POST /humid with level=<int>."""
        await self._request("POST", "/humid", data={"level": str(level)})

    async def set_buzzer_state(self, enabled: bool) -> None:
        """Set buzzer state using state=0/1."""
        await self._request("POST", "/buzzer", data={"state": "1" if enabled else "0"})