# Eopt Home

![AI: Assisted](https://img.shields.io/badge/AI-Assisted-blue)

A [Home Assistant](https://www.home-assistant.io/) custom component for controlling the Sensio / Eopt Home X1 xComfort controller via [sensio_lib](https://pypi.org/project/sensio-lib/).

## Features

- **Lights & Dimmers** — On/off control for relay lights and `0–100%` brightness control for dimmers (automatically restoring the previous brightness level when turned back on)
- **Live state feedback** — Listens to the X1 controller's real-time event stream, so lights or dimmers changed via physical wall switches update in Home Assistant immediately
- **Zone (Room) grouping** — Creates a Home Assistant device for each Sensio zone so you can assign a whole room of lights to your chosen Home Assistant Area in one place
- **Automatic reconnect** — Automatically reconnects with exponential backoff if the network connection to the X1 controller drops
- **Scenes** — Activate house-level scenes configured in your xComfort project
- **Sync button** — Re-fetch your project data from the Eopt Home cloud at any time

### Limitations

- Only lights, dimmers and scenes are supported.

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
| **HA-Pilot** | If you use HA-Pilot, enable this. Otherwise, Unity is used by default. |

> **Tip:** The hub can be difficult to spot on your local network if you don't already know its IP. In my case the hostname started with something like `X-1...` when I looked for the unit in my routers DHCP leases. 

## Disclaimer

This integration has only been tested on a single device. It is currently unknown if it will work with all kind of installations using the X1 controller. Feedback / reporting issues are welcome!
