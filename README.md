# AdGuard DNS Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/nmlssfx/adguard-dns-hacs.svg)](https://github.com/nmlssfx/adguard-dns-hacs/releases)
[![GitHub license](https://img.shields.io/github/license/nmlssfx/adguard-dns-hacs.svg)](https://github.com/nmlssfx/adguard-dns-hacs/blob/main/LICENSE)

A comprehensive Home Assistant integration for monitoring and controlling AdGuard DNS services.

## 🚀 Features

- **📊 Real-time Statistics**: Monitor total queries, blocked queries, and blocking percentage
- **🔍 Domain Analytics**: View top queried and blocked domains
- **📱 Device Tracking**: Track devices connected to your AdGuard DNS
- **🛡️ Protection Status**: Monitor DNS protection status
- **🧹 Log Management**: Clear query logs with a simple button press
- **🔄 Auto Updates**: Automatic data refresh every 30 seconds
- **🌐 OAuth2 Authentication**: Secure authentication with AdGuard DNS API

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/nmlssfx/adguard-dns-hacs`
6. Select "Integration" as the category
7. Click "Add"
8. Find "AdGuard DNS" in the integration list and install it
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/nmlssfx/adguard-dns-hacs/releases)
2. Extract the `custom_components/adguard_dns` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Configuration** → **Integrations**
2. Click **"Add Integration"**
3. Search for **"AdGuard DNS"**
4. Follow the OAuth2 authentication flow:
   - You'll be redirected to AdGuard DNS to authorize the integration
   - Select the server profile you want to monitor
   - Complete the authentication process
5. The integration will automatically discover and set up all available entities

## 📋 Available Entities

### Sensors
- **Total Queries**: Number of DNS queries processed
- **Blocked Queries**: Number of blocked DNS queries
- **Blocked Percentage**: Percentage of queries that were blocked
- **Top Blocked Domains**: List of most frequently blocked domains
- **Top Queried Domains**: List of most frequently queried domains

### Binary Sensors
- **Protection Enabled**: Shows whether DNS protection is active

### Buttons
- **Clear Query Log**: Clears the DNS query log

### Device Trackers
- **Connected Devices**: Tracks devices using your AdGuard DNS

## 🔧 Requirements

- Home Assistant 2023.1.0 or newer
- AdGuard DNS account
- Internet connection for API access

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**: Ensure you have a valid AdGuard DNS account and internet connection
2. **No Data**: Check that your AdGuard DNS service is active and processing queries
3. **Entities Not Appearing**: Restart Home Assistant after installation

### Debug Logging

To enable debug logging, add this to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.adguard_dns: debug
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This integration was developed in collaboration with **TraeAI Claude 4 Sonnet**, leveraging advanced AI assistance to create a robust and feature-rich Home Assistant integration.

## 📞 Support

For issues, feature requests, or questions:
- Open an issue on [GitHub](https://github.com/nmlssfx/adguard-dns-hacs/issues)
- Check the [Home Assistant Community Forum](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant community**
