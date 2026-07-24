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


@dataclass
class KmfData:
    voltage: float | None = None
    current: float | None = None
    power: float | None = None
    charge_status: str | None = None
    soc: float | None = None
    remaining_ah: float | None = None
    full_capacity_ah: float | None = None
    est_time: str | None = None
    charge_energy_kwh: float | None = None
    discharge_energy_kwh: float | None = None
    date: str | None = None
    time: str | None = None
    field6: int | None = None
    field7: int | None = None
    field8: int | None = None


class KmfCoordinator(DataUpdateCoordinator[KmfData]):
    """Coordinator for KM-F streaming + startup poll."""

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
            reader = None
            writer = None
            try:
                reader, writer = await asyncio.open_connection(self._host, self._port)

                while True:
                    line = await reader.readline()
                    if not line:
                        break
                    self._handle_frame(line.decode().strip())

            except Exception as err:
                _LOGGER.error("KM-F: stream error: %s", err)

            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception:
                    pass

            await asyncio.sleep(self._reconnect_delay)

    def _handle_frame(self, line: str):
        if not line:
            return

        if line.startswith(":A="):
            self._parse_A(line)
        elif line.startswith(":B="):
            self._parse_B(line)
        elif line.startswith(":C="):
            self._parse_C(line)

        self.async_set_updated_data(self.data)

    def _parse_A(self, line: str):
        parts = line.replace(":A=", "").split(",")
        if len(parts) < 9:
            return

        try:
            v_raw = float(parts[0])
            i_raw = float(parts[1])
            mode = parts[2]
            minutes = int(parts[3])
            remaining_raw = float(parts[4])  # mAh
            full_raw = float(parts[5])       # Ah * 10

            # Voltage with 2 decimals
            self.data.voltage = round(v_raw / 100.0, 2)

            sign = -1.0 if mode == "0" else 1.0
            self.data.current = sign * (i_raw / 1000.0)
            self.data.power = sign * (v_raw * i_raw / 100000.0)

            # Convert both to Ah
            remaining_ah = remaining_raw / 1000.0
            full_ah = full_raw / 10.0

            self.data.remaining_ah = remaining_ah
            self.data.full_capacity_ah = full_ah

            if full_ah > 0:
                self.data.soc = round((remaining_ah / full_ah) * 100.0, 1)
            else:
                self.data.soc = None

            h = minutes // 60
            m = minutes % 60
            self.data.est_time = f"{'+' if mode == '1' else '-'}{h:02d}:{m:02d}"

            self.data.charge_status = "CHARGING" if mode == "1" else "DISCHARGING"

            # Raw diagnostic fields
            self.data.field6 = int(parts[6])
            self.data.field7 = int(parts[7])
            self.data.field8 = int(parts[8])

        except Exception as err:
            _LOGGER.warning("KM-F: error parsing :A frame '%s': %s", line, err)

    def _parse_B(self, line: str):
        parts = line.replace(":B=", "").split(",")
        try:
            d = str(parts[6]).zfill(6)
            t = str(parts[7]).zfill(6)
            self.data.date = f"20{d[0:2]}-{d[2:4]}-{d[4:6]}"
            self.data.time = f"{t[0:2]}:{t[2:4]}:{t[4:6]}"
        except Exception:
            pass

    def _parse_C(self, line: str):
        parts = line.replace(":C=", "").split(",")
        try:
            self.data.charge_energy_kwh = float(parts[0]) / 1000.0
            self.data.discharge_energy_kwh = float(parts[1]) / 1000.0
        except Exception:
            pass
