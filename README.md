# KM-F Energy Monitor

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for the **Junctek KM-F series** battery monitor/coulometer.

Connects directly to the device over TCP (via its built-in WiFi adapter) and parses the real-time data stream — no cloud, no polling delay.

![Junctek Logo](logo.png)

## Features

- Real-time push updates from the KM-F data stream
- Battery voltage, current, power, and state of charge
- Remaining capacity (Ah) and nominal capacity
- Cumulative charge and discharge energy (kWh)
- Charge status (charging / discharging) and estimated time to full/empty
- Device date and time
- Load switch control
- Automatic reconnection on connection loss

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → three-dot menu → **Custom repositories**
2. Add `https://github.com/ogremustcrush/kmf_energy_monitor` as an **Integration**
3. Install "KM-F Energy Monitor" from HACS
4. Restart Home Assistant

### Manual

Copy the `custom_components/kmf_energy_monitor/` directory into your HA `custom_components/` folder and restart.

## Configuration

After installation, go to **Settings → Devices & Services → Add Integration** and search for **KM-F Energy Monitor**.

You will be prompted for:

| Field | Default | Description |
|---|---|---|
| Host | — | IP address of your KM-F WiFi adapter |
| Port | 8899 | TCP port (default for KM-F) |
| Reconnect delay | 3s | Seconds to wait before reconnecting on disconnect |

## Supported Devices

Tested with the **Junctek KM-F** series. Other Junctek models using the same TCP protocol may also work.
