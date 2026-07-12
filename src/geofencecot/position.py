#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot own-position helpers.

"""Own-position helpers: static config coordinates or gpsd (gpspipe)."""

import json
import os
from configparser import SectionProxy
from typing import Optional, Tuple, Union

import geofencecot


def static_position_configured(config: Union[dict, SectionProxy, None]) -> bool:
    """Return True when STATIC_LAT and STATIC_LON are both set."""
    config = config or {}
    lat = config.get("STATIC_LAT")
    lon = config.get("STATIC_LON")
    return bool(
        lat is not None
        and lon is not None
        and str(lat).strip()
        and str(lon).strip()
    )


def static_position(
    config: Union[dict, SectionProxy, None],
) -> Tuple[float, float, float]:
    """Return (lat, lon, hae) from static config coordinates."""
    config = config or {}
    lat = float(config.get("STATIC_LAT"))
    lon = float(config.get("STATIC_LON"))
    hae = float(config.get("STATIC_HAE") or 0.0)
    return lat, lon, hae


def gpspipe_position(
    config: Union[dict, SectionProxy, None],
) -> Optional[Tuple[float, float, float]]:
    """Poll gpsd once via gpspipe (or GPS_INFO_CMD) for the current fix."""
    config = config or {}
    cmd = str(config.get("GPS_INFO_CMD") or geofencecot.DEFAULT_GPS_INFO_CMD)
    try:
        with os.popen(cmd) as proc:
            output = proc.read()
    except OSError:
        return None

    tpv_line = None
    for line in output.split("\n"):
        if "TPV" in line:
            tpv_line = line

    if not tpv_line:
        return None

    try:
        data = json.loads(tpv_line)
    except json.JSONDecodeError:
        return None

    if data.get("class") != "TPV":
        return None

    lat = data.get("lat")
    lon = data.get("lon")
    if lat is None or lon is None:
        return None

    hae = data.get("altHAE") or data.get("altMSL") or 0.0
    try:
        return float(lat), float(lon), float(hae)
    except (TypeError, ValueError):
        return None


def get_own_position(
    config: Union[dict, SectionProxy, None],
) -> Optional[Tuple[float, float, float]]:
    """Return own (lat, lon, hae): static config takes priority, else gpsd."""
    if static_position_configured(config):
        return static_position(config)
    return gpspipe_position(config)
