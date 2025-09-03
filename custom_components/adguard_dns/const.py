"""Constants for the AdGuard DNS integration."""

DOMAIN = "adguard_dns"

# API URLs
API_BASE_URL = "https://api.adguard-dns.io"
OAUTH_URL = "https://auth.adguard.com/oauth/token"

# OAuth2 Configuration
CLIENT_ID = "adguard-dns-client"
SCOPES = ["profile", "adguard-dns"]

# API Endpoints
API_ENDPOINTS = {
    "query_log": "/v1/query_log",
    "stats_time": "/v1/stats/time",
    "stats_companies": "/v1/stats/companies",
    "stats_countries": "/v1/stats/countries",
    "stats_devices": "/v1/stats/devices",
    "stats_domains": "/v1/stats/domains",
    "devices": "/v1/devices",
    "profile": "/v1/profile",
}

# Sensor Types
SENSOR_TYPES = {
    "total_queries": {
        "name": "Total Queries",
        "icon": "mdi:dns",
        "unit": "queries",
        "device_class": None,
        "state_class": "total_increasing",
    },
    "blocked_queries": {
        "name": "Blocked Queries",
        "icon": "mdi:shield-check",
        "unit": "queries",
        "device_class": None,
        "state_class": "total_increasing",
    },
    "blocked_percentage": {
        "name": "Blocked Percentage",
        "icon": "mdi:percent",
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
    },
    "top_blocked_domain": {
        "name": "Top Blocked Domain",
        "icon": "mdi:web-cancel",
        "unit": None,
        "device_class": None,
        "state_class": None,
    },
    "top_queried_domain": {
        "name": "Top Queried Domain",
        "icon": "mdi:web",
        "unit": None,
        "device_class": None,
        "state_class": None,
    },
}

# Binary Sensor Types
BINARY_SENSOR_TYPES = {
    "protection_enabled": {
        "name": "Protection Enabled",
        "icon": "mdi:shield",
        "device_class": None,
    },
}

# Button Types
BUTTON_TYPES = {
    "clear_query_log": {
        "name": "Clear Query Log",
        "icon": "mdi:delete-sweep",
    },
}

# Device Tracker Types
DEVICE_TRACKER_TYPES = {
    "adguard_device": {
        "name": "AdGuard Device",
        "icon": "mdi:router-wireless",
    },
}

# Update intervals
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutes
MIN_UPDATE_INTERVAL = 60  # 1 minute
MAX_UPDATE_INTERVAL = 3600  # 1 hour

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "button", "device_tracker"]