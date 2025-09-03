# AdGuard DNS Integration for Home Assistant

This integration allows you to monitor and control your AdGuard DNS service directly from Home Assistant.

## Features

- **Statistics Monitoring**: Track total queries, blocked queries, and blocking percentage
- **Top Domains**: View most queried and most blocked domains
- **Device Tracking**: Monitor devices connected to your AdGuard DNS
- **Protection Status**: Check if DNS protection is enabled
- **Query Log Management**: Clear query logs with a button press
- **Real-time Updates**: Automatic data refresh every 30 seconds

## Installation

1. Install via HACS (recommended)
2. Restart Home Assistant
3. Go to Configuration → Integrations
4. Click "Add Integration" and search for "AdGuard DNS"
5. Follow the OAuth2 authentication flow

## Configuration

The integration uses OAuth2 authentication with AdGuard DNS API. You'll need to:

1. Authorize the integration with your AdGuard DNS account
2. Select which server profile to monitor
3. The integration will automatically discover and set up all available entities

## Entities

### Sensors
- Total Queries
- Blocked Queries  
- Blocked Percentage
- Top Blocked Domains
- Top Queried Domains

### Binary Sensors
- Protection Enabled

### Buttons
- Clear Query Log

### Device Trackers
- Connected Devices

## Requirements

- Home Assistant 2023.1.0 or newer
- AdGuard DNS account
- Internet connection for API access

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/nmlssfx/adguard-dns-hacs).