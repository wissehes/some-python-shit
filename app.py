from flask import Flask, render_template, redirect, request
from kasa import SmartPlug, Discover
import asyncio

app = Flask(__name__)

devices = asyncio.run(Discover.discover())


def rediscover():
    devices = asyncio.run(Discover.discover())

    formattedDevices = {
        'devices': []
    }

    for addr, dev in devices.items():
        asyncio.run(dev.update())

        formattedDevices['devices'].append({
            'name': dev.alias,
            # 'host': dev.host,
            'address': addr,
            'state': dev.is_on,
            'sysinfo': dev.sys_info
        })


def get_device_by_name(deviceName):
    for addr, dev in devices.items():
        if dev.alias.lower() == deviceName.lower():
            asyncio.run(dev.update())
            return dev


def formatDevice(device): return {
    'name': device.alias,
    'address': device.host,
    'state': device.is_on,
    'sysinfo': device.sys_info
}


@app.route("/")
def index():
    formattedDevices = []

    for addr, device in devices.items():
        asyncio.run(device.update())
        formatted = formatDevice(device=device)
        formattedDevices.append(formatted)

    return render_template("index.html", devices=formattedDevices)


@app.route("/device/<deviceName>")
def get_device(deviceName):
    device = get_device_by_name(deviceName=deviceName)

    if not device:
        return 'nope'

    return formatDevice(device)


@app.route("/device/<deviceName>/<option>")
def do_device(deviceName, option):
    device = get_device_by_name(deviceName=deviceName)
    if device == None:
        return '404 not found!'

    redirectTo = request.args.get('redirect')

    if option == "off":
        asyncio.run(device.turn_off())

    if option == "on":
        asyncio.run(device.turn_on())

    if redirectTo:
        return redirect(redirectTo)
    else:
        return formatDevice(device=device)


@app.route("/status")
def status():
    plug = SmartPlug("192.168.178.23")
    asyncio.run(plug.update())
    return {
        'host': plug.host,
        'state': plug.is_on
    }


@app.route("/off")
def off():
    plug = SmartPlug("192.168.178.23")
    asyncio.run(plug.update())
    asyncio.run(plug.turn_off())
    return redirect("/")


@app.route("/on")
def on():
    plug = SmartPlug("192.168.178.23")
    asyncio.run(plug.update())
    asyncio.run(plug.turn_on())
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
