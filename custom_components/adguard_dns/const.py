"""Constants for the AdGuard DNS integration."""

DOMAIN = "adguard_dns"

# API URLs
API_BASE_URL = "https://api.adguard-dns.io"
OAUTH_URL = "https://api.adguard-dns.io/oapi/v1/oauth_token"

# Authentication Configuration
# AdGuard DNS API uses simple username/password authentication

# API Endpoints
API_ENDPOINTS = {
    "account_limits": "/oapi/v1/account/limits",
    "devices": "/oapi/v1/devices",
    "dns_servers": "/oapi/v1/dns_servers",
    "dedicated_addresses": "/oapi/v1/dedicated_addresses/ipv4",
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
# Note: Clear Query Log functionality is not available in current AdGuard DNS API
BUTTON_TYPES = {}

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
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]