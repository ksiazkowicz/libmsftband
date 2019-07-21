# libmsftband
This project aims to completely reverse engineer Microsoft Band protocol, giving new life to these cool devices. This repo contains a simple Python library, basic interface for it and docs describing the protocol.

## Installation
You need to install some dependencies first:
`pip install -r requirements.txt`

## Usage
You can use provided example client to connect to your Band. Set `DEVICE_MAC_ADDRESS` environment variable to MAC address of your Band and run `cli.py`:

```
export DEVICE_MAC_ADDRESS=00:00:00:00:00:00
python cli.py
```

You can also create `.env` file to save this and other settings for later.

```
DEVICE_MAC_ADDRESS=00:00:00:00:00:00
```

Don't forget to replace `00:00:00:00:00:00` with your Band's MAC address.
