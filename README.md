# Eopt Home

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=sk0zzi&repository=https%3A%2F%2Fgithub.com%2Fsk0zzi%2FEopt_Home&category=Integration)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
![AI: Assisted](https://img.shields.io/badge/AI-Assisted-blue)

A powerful but lightweight [Home Assistant](https://www.home-assistant.io/) custom component for controlling the Sensio / Eopt Home X1 xComfort controller from your local network!

The integration pulls your existing room and device setup from your Eopt Home (or HA-Pilot) account on first run, caches it locally, and handles all control and state updates directly on your LAN. This project uses the [sensio_lib](https://pypi.org/project/sensio-lib/) for handling X1 controller communication. 

## Features

- **Lights & Dimmers** - On/off control for relay lights and `0–100%` brightness control for dimmers (automatically restoring the previous brightness level when turned back on)
- **Thermostats** - Set and read temperatures
- **Live state feedback** - Listens to the X1 controller's real-time event stream, so lights, dimmers or thermostats changed via physical wall switches update in Home Assistant immediately
- **Zone (Room) grouping** - Creates a Home Assistant device for each Sensio zone so you can assign a whole room of lights to your chosen Home Assistant Area in one place
- **Automatic reconnect** - Automatically reconnects with exponential backoff if the network connection to the X1 controller drops
- **Scenes** - Activate house-level scenes configured in your xComfort project
- **Sync button** - Re-fetch your project data from the Eopt Home cloud at any time (only automatically done at first run)
- **Error reporting** - Integration will report issues back to home assistant if the controller reports issues
- **Thermostat power & energy reporting** - Optional Power (`W`) and cumulative Energy (`kWh`) sensors per thermostat for the Home Assistant Energy Dashboard (can be toggled on or off in integration settings).

## Installation

Use the button at the top of the readme or follow these manual steps:

1. Go to marketplace in your home assistant installation.
2. Press the menu button in the right top corner.
3. Select "Custom repositories".
4. Add this URL to the repository field: https://github.com/sk0zzi/Eopt_Home and select integration in type and press add.
5. Search for "eopt home" in marketplace and install it. 

To install manually:

1. Copy the `custom_components/eopt_home` folder from this repository into the `custom_components` directory of your Home Assistant installation.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **Eopt Home**.

## Configuration

The integration works 100% locally but needs to fetch your project information from Eopt Home on first setup. It logs in, retrieves your project data, and stores it in Home Assistant. A button entity is provided so you can trigger a re-sync whenever needed. Running a re-sync is only needed if you have changed your configuration in the Eopt home installation itself. 

You will be prompted for:

| Field | Description |
|---|---|
| **Username** | Your Eopt Home username |
| **Password** | Your Eopt Home password |
| **Hub IP** | The local IP address of your X1 controller |
| **HA-Pilot** | If you use HA-Pilot, enable this. Otherwise, Unity is used by default. |
| **Enable power reporting** | Choose if you want entities created for reporting power usage that is received from the controller |

> **Tip:** The hub can be difficult to spot on your local network if you don't already know its IP. In my case the hostname started with something like `X-1...`. 


Feedback / reporting issues are welcome!
