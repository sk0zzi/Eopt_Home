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

This integration is not yet available through HACS.

To install manually:

1. Copy the `custom_components/eopt_home` folder from this repository into the `custom_components` directory of your Home Assistant installation.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **Eopt Home**.

## Configuration

The integration works 100% locally but needs to fetch your project information from Eopt Home on first setup. It logs in, retrieves your project data, and stores it in Home Assistant. A button entity is provided so you can trigger a re-sync whenever needed.

You will be prompted for:

| Field | Description |
|---|---|
| **Username** | Your Eopt Home username |
| **Password** | Your Eopt Home password |
| **Hub IP** | The local IP address of your X1 controller |

> **Tip:** The hub can be difficult to spot on your local network if you don't already know its IP. In my case the hostname started with something like `X-1...`.

## Disclaimer

This integration has only been tested on a single device. It was built to switch a few lights and control scenes — your mileage may vary.