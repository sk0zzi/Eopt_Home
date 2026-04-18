# Eopt Home

A [Home Assistant](https://www.home-assistant.io/) custom component for controlling the Sensio / Eopt Home X1 xComfort controller via [sensio_lib](https://pypi.org/project/sensio-lib/).

## Features

- **Lights** — on/off
- **Scenes** — activate scenes configured in your xComfort project
- **Sync button** — re-fetch your project data from Eopt Home at any time

### Limitations

- Commands are sent to the X1 controller but no state is read back. If lights are toggled with physical switches the status in Home Assistant will be out of sync.
- Only lights and scenes are supported.

## Installation

This integration is possible to install through HACS via a manual steps:

1. Go to hack in your home assistant installation.
2. Press the menu button in the right top corner.
3. Select "Custom reposotories".
4. Add this URL to the reposotory field: https://github.com/sk0zzi/Eopt_Home and select integration in type and press add.
5. Search for "eopt home" in hacs and install it from there. 

To install manually:

1. Copy the `custom_components/eopt_home` folder from this repository into the `custom_components` directory of your Home Assistant installation.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **Eopt Home**.

## Configuration

The integration works 100% locally but needs to fetch your project information from Eopt Home on first setup. It logs in, retrieves your project data, and stores it in Home Assistant. A button entity is provided so you can trigger a re-sync whenever needed. Running a re-sync is only needed if your have changed your configuration in the installation itself. 

You will be prompted for:

| Field | Description |
|---|---|
| **Username** | Your Eopt Home username |
| **Password** | Your Eopt Home password |
| **Hub IP** | The local IP address of your X1 controller |

> **Tip:** The hub can be difficult to spot on your local network if you don't already know its IP. In my case the hostname started with something like `X-1...` when I looked for the unit in my routers DHCP leases. 

## Disclaimer

This integration has only been tested on a single device. It is currently unknown if it will work with all kind of installations using the X1 controller. Feedback / reporting issues are welcome!