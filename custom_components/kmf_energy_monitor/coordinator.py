from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_RECONNECT_DELAY,
)

_LOGGER = logging.getLogger(__name__)

_C_POLL_INTERVAL = 30  # seconds between :C= requests


@dataclass
class KmfData:
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    charge_status: str | None = None
    charging: bool | None = None
    soc: float | None = None
    remaining_ah: float | None = None
    full_capacity_ah: float | None = None
    time_remaining_minutes: int | None = None
    est_time: str | None = None
    charge_energy_kwh: float | None = None
    discharge_energy_kwh: float | None = None
    date: str | None = None
    time: str | None = None
    field6: int | None = None
    field7: int | None = None
    field8: int | None = None


class KmfCoordinator(DataUpdateCoordinator[KmfData]):

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        self.hass = hass
        self._host = config[CONF_HOST]
        self._port = config[CONF_PORT]
        self._reconnect_delay = config[CONF_RECONNECT_DELAY]

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self._host}",
            update_interval=None,
        )

        self.data = KmfData()

    def start_background_tasks(self, entry) -> None:
        entry.async_create_background_task(
            self.hass, self._stream_reader(), "kmf_stream"
        )

    async def _stream_reader(self):
        while True:
            writer = None
            try:
                reader, writer = await asyncio.open_connection(self._host, self._port)
                _LOGGER.info("KM-F: connected to %s:%d", self._host, self._port)

                poll_task = asyncio.ensure_future(self._poll_c(writer))
                try:
                    while True:
                        line = await reader.readline()
                        if not line:
                            raise ConnectionResetError("Connection closed by device")
                        self._handle_frame(line.decode("ascii", errors="ignore").strip())
                finally:
                    poll_task.cancel()
                    try:
                        await poll_task
                    except asyncio.CancelledError:
                        pass

            except Exception as err:
                _LOGGER.error("KM-F: connection error: %s — reconnecting in %ds",
                              err, self._reconnect_delay)

            # Mark entities unavailable while disconnected
            self.last_update_success = False
            self.async_update_listeners()

            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass

            await asyncio.sleep(self._reconnect_delay)

    async def _poll_c(self, writer):
        """Periodically request :C= energy totals from the device."""
        while True:
            await asyncio.sleep(_C_POLL_INTERVAL)
            try:
                writer.write(b":C\n")
                await writer.drain()
                _LOGGER.debug("KM-F: sent :C request")
            except Exception as err:
                _LOGGER.debug("KM-F: error sending :C request: %s", err)
                break

    def _handle_frame(self, line: str):
        if not line:
            return
        if line.startswith(":A="):
            self._parse_A(line)
        elif line.startswith(":B="):
            self._parse_B(line)
        elif line.startswith(":C="):
            self._parse_C(line)
        else:
            return
        self.async_set_updated_data(self.data)

    def _parse_A(self, line: str):
        parts = line.replace(":A=", "").rstrip(",").split(",")
        if len(parts) < 6:
            return
        try:
            v_raw = int(parts[0])
            i_raw = int(parts[1])
            charging = (parts[2].strip() == "1")
            minutes = int(parts[3])
            remaining_raw = int(parts[4])
            full_raw = int(parts[5])

            sign = 1.0 if charging else -1.0

            self.data.voltage = round(v_raw / 100.0, 2)
            self.data.current = round(sign * i_raw / 1000.0, 3)
            self.data.power = round(sign * v_raw * i_raw / 100000.0, 2)
            self.data.charging = charging
            self.data.charge_status = "CHARGING" if charging else "DISCHARGING"

            remaining_ah = remaining_raw / 1000.0
            full_ah = full_raw / 10.0
            self.data.remaining_ah = round(remaining_ah, 3)
            self.data.full_capacity_ah = round(full_ah, 1)

            if full_ah > 0:
                self.data.soc = round(
                    max(0.0, min(100.0, (remaining_ah / full_ah) * 100.0)), 1
                )
            else:
                self.data.soc = None

            self.data.time_remaining_minutes = minutes
            h, m = divmod(minutes, 60)
            self.data.est_time = f"{'+' if charging else '-'}{h:02d}:{m:02d}"

            if len(parts) >= 9:
                self.data.field6 = int(parts[6])
                self.data.field7 = int(parts[7])
                self.data.field8 = int(parts[8])

        except Exception as err:
            _LOGGER.warning("KM-F: error parsing :A frame '%s': %s", line, err)

    def _parse_B(self, line: str):
        parts = line.replace(":B=", "").rstrip(",").split(",")
        try:
            d = str(parts[6]).zfill(6)
            t = str(parts[7]).zfill(6)
            self.data.date = f"20{d[0:2]}-{d[2:4]}-{d[4:6]}"
            self.data.time = f"{t[0:2]}:{t[2:4]}:{t[4:6]}"
        except Exception:
            pass

    def _parse_C(self, line: str):
        parts = line.replace(":C=", "").rstrip(",").split(",")
        try:
            self.data.charge_energy_kwh = round(int(parts[0]) / 1000.0, 3)
            self.data.discharge_energy_kwh = round(int(parts[1]) / 1000.0, 3)
        except Exception as err:
            _LOGGER.warning("KM-F: error parsing :C frame '%s': %s", line, err)
