[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=jilaqi-le-gao_PyIndi_Tornado_Websocket_Interface)

# PyIndi_client Websocket Interface

This is a project operating indi drivers through pyindi_client through websocket interface, based on tornado websocket server.

This project will provide:

1. two http api, which is used to initial after indi is booted, getting infomartion which driver will be used.
2. one websocekt api, to directly know all properties of indi devices.
3. one high-level websocket api, which can be called as part of sequence.
4. one low-level websocket api, which can be called to directly change properties of indi.

## supported devices type

At first stage, this project will support telescope and camera.

At second stage, this project will support focuser, filter_wheel to support basic DSO astrophotography.

Future, may support all necessary devices if necessary.

## project usage

This project is intended to be used as part of  	[ligthAPT](https://github.com/AstroAir-Develop-Team/lightapt), as the backend support for indi drivers.

## class architecture

PyIndiWebSocketWorker (in py_indi_websocket.py) contains:

    IndiClient              (in indiClientDef.py)
    IndiTelescopeDevice     (in indi_telescope.py)
    IndiCameraDevice        (in indi_camera.py)
    IndiDeviceActiveInfo    (in indi_incoming_device_info.py)

IndiTelescopeDevice, IndiCameraDevice are inherited from IndiBaseDevice (in indi_base_device.py)
