# TempStick — Home Assistant Custom Component

Integrates [TempStick](https://www.tempstickapi.com) wireless temperature/humidity sensors into Home Assistant via the TempStick cloud API. Supports standard sensors as well as devices with external thermocouple probes (tcTemp).

---

## Features

- **Automatic discovery** — all sensors on your TempStick account are found at setup
- **Thermocouple (tcTemp) support** — devices with `TC_M = 1` automatically get a Probe Temperature entity named after the probe type (T, K, J, etc.)
- **Per-device entities** for each physical sensor:
  - 🌡 Onboard Temperature
  - 💧 Humidity
  - 🔋 Battery level
  - 📶 RSSI / signal strength (disabled by default)
  - 🔬 Probe Temperature — thermocouple devices only
  - ⚠️ Alert binary sensor
- **Config UI** — set up entirely from the HA integrations page, no YAML required
- **Options flow** — change poll interval or temperature unit without removing the integration
- **Device grouping** — all entities for each physical sensor are grouped under one HA device, with the thermocouple type shown in the device model string

---

## Installation

### HACS (recommended)

1. In HACS → Integrations → Custom Repositories, add this repo URL with category **Integration**
2. Install "TempStick"
3. Restart Home Assistant

### Manual

1. Copy the `tempstick/` folder into `<config>/custom_components/`
2. Restart Home Assistant

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **TempStick**
3. Enter your **API Key** (see below)
4. Set your preferred poll interval (default: 5 minutes) and temperature unit
5. Click **Submit** — all sensors are discovered and entities created automatically

### Getting Your API Key

1. Log in at [app.tempstickapi.com](https://app.tempstickapi.com)
2. Navigate to **Account → API Settings**
3. Copy your API key (format: `ts_live_xxxxxxxxxxxxxxxxxxxx`)

---

## Entities Created Per Device

| Entity | Device Class | Unit | Enabled by Default |
|---|---|---|---|
| Temperature | `temperature` | °F or °C | Yes |
| Humidity | `humidity` | % | Yes |
| Battery | `battery` | % | Yes |
| Signal Strength | `signal_strength` | dBm | No |
| Probe Temperature | `temperature` | °F or °C | Yes — thermocouple devices only |
| Alert | `problem` | on/off | Yes |

### Thermocouple (tcTemp) Devices

Devices with an attached thermocouple probe report `TC_M = 1` in the API response. For these devices the integration automatically creates an additional **Probe Temperature** entity. The entity name includes the probe type — for example, `Probe Temperature (Type T)`.

The probe temperature is reported by TempStick in Celsius internally. The integration converts it to your selected unit (°F or °C). The sentinel value `-9999` (no probe connected or bad reading) is returned as `unavailable` rather than a number.

The HA device model string reflects the probe type, e.g. `TempStick (Thermocouple Type T)`.

---

## Options

After setup, click **Configure** on the integration card to adjust:

| Option | Default | Description |
|---|---|---|
| Poll interval | 5 min | How often to fetch readings from TempStick cloud (1–60 min) |
| Temperature unit | °F | Fahrenheit or Celsius — applies to both onboard and probe sensors |

---

## API Reference

The integration uses the TempStick REST API at `https://www.tempstickapi.com/api/v1`.

### Endpoints Used

| Endpoint | Purpose |
|---|---|
| `GET /sensors/all` | Discover all sensors and fetch latest readings |
| `GET /sensor/{sensor_id}` | Fetch data for a single sensor |

### Sample API Response

```json
{
  "type": "success",
  "message": "get sensors",
  "data": {
    "groups": [],
    "items": [
      {
        "id": "289748",
        "version": "2013",
        "sensor_id": "EX00FWNWR3",
        "sensor_name": "-80C PEKC",
        "sensor_mac_addr": "24:D7:EB:F3:70:37",
        "owner_id": "190144",
        "type": "EX",
        "alert_interval": "1800",
        "send_interval": "3600",
        "last_temp": 20.05,
        "last_humidity": 54.1,
        "last_voltage": "3.46",
        "rssi": "-128",
        "last_checkin": "2026-04-01 00:12:40",
        "next_checkin": "2026-04-01 01:12:40",
        "ssid": "Stanford",
        "offline": "0",
        "battery_pct": 100,
        "TC_M": 1,
        "TC_R": 1,
        "TC_TYPE": "T",
        "last_tcTemp": "-70",
        "minTcTemp": "-9999",
        "maxTcTemp": "-50",
        "TCUS": 20,
        "TCLS": 20,
        "probe_temp_offset": 0,
        "alert_temp_below": "-99",
        "alert_temp_above": "200",
        "alert_humidity_below": "-99",
        "alert_humidity_above": "100"
      }
    ]
  }
}
```

### Key Fields

| Field | Description |
|---|---|
| `sensor_id` | Unique device identifier used as the HA device key (e.g. `EX00FWNWR3`) |
| `sensor_mac_addr` | MAC address of the device |
| `version` | Firmware version string |
| `last_temp` | Onboard temperature in °F |
| `last_humidity` | Relative humidity in % |
| `battery_pct` | Battery level 0–100 |
| `rssi` | WiFi signal strength in dBm |
| `offline` | `"0"` = online, `"1"` = offline |
| `TC_M` | Thermocouple mode: `1` = enabled, `0` = disabled |
| `TC_TYPE` | Thermocouple type: `T`, `K`, `J`, `E`, `N`, `S`, `R`, or `B` |
| `last_tcTemp` | Latest probe temperature in °C; `-9999` = no valid reading |
| `minTcTemp` | Probe alert lower threshold |
| `maxTcTemp` | Probe alert upper threshold |

---

## Troubleshooting

- **"Cannot connect"** — verify internet access from HA and that `tempstickapi.com` is reachable
- **"Invalid auth"** — regenerate your API key in the TempStick portal
- **Probe Temperature entity missing** — check that the physical device reports `TC_M = 1`; devices without a thermocouple attached will not have this entity
- **Probe Temperature shows unavailable** — the probe is returning the `-9999` sentinel (disconnected or bad contact); check the probe wiring
- **Stale readings** — lower the poll interval; note that TempStick free accounts may enforce a minimum check-in interval on the device side regardless of HA polling frequency
- **Missing sensors** — sensors must have checked in recently to appear in the API `/sensors/all` response
