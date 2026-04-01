"""Constants for the TempStick integration."""

DOMAIN = "tempstick"
PLATFORMS = ["sensor", "binary_sensor"]

# API
TEMPSTICK_API_KEY_DEFAULT = ""
TEMPSTICK_API_BASE = "https://www.tempstickapi.com/api/v1"
TEMPSTICK_API_SENSORS = f"{TEMPSTICK_API_BASE}/sensors/all"
TEMPSTICK_API_SENSOR = f"{TEMPSTICK_API_BASE}/sensor"

# Config entry keys
CONF_API_KEY = "api_key"
CONF_POLL_INTERVAL = "poll_interval"
CONF_TEMPERATURE_UNIT = "temperature_unit"

# Defaults
DEFAULT_POLL_INTERVAL = 5  # minutes
DEFAULT_NAME = "TempStick"

# Sensor types
SENSOR_TEMPERATURE = "temperature"
SENSOR_HUMIDITY = "humidity"
SENSOR_BATTERY = "battery"
SENSOR_RSSI = "rssi"
SENSOR_TC_TEMP = "tc_temperature"
BINARY_SENSOR_ALERT = "alert"
BINARY_SENSOR_OFFLINE = "offline"

# Device info keys from API response
API_KEY_SENSOR_ID = "sensor_id"
API_KEY_SENSOR_NAME = "sensor_name"
API_KEY_LAST_TEMP = "last_temp"
API_KEY_LAST_HUMIDITY = "last_humidity"
API_KEY_BATTERY_PCT = "battery_pct"
API_KEY_RSSI = "rssi"
API_KEY_ALERT_ACTIVE = "alert_active"
API_KEY_MAC = "sensor_mac_addr"
API_KEY_LAST_CHECKIN = "last_checkin"
API_KEY_FIRMWARE = "version"
API_KEY_OFFLINE = "offline"

# Thermocouple probe (tcTemp) — present when TC_M == 1
API_KEY_TC_MODE = "TC_M"
API_KEY_TC_TEMP = "last_tcTemp"
API_KEY_TC_TYPE = "TC_TYPE"       # T, K, J, E, N, S, R, B
API_KEY_TC_TEMP_MIN = "minTcTemp"
API_KEY_TC_TEMP_MAX = "maxTcTemp"
