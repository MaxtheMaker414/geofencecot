#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot marker parsing.

"""Parse incoming CoT marker XML into a simple dict."""

import xml.etree.ElementTree as ET
from typing import Optional, Union


def parse_marker(raw: Union[bytes, str]) -> Optional[dict]:
    """Parse a raw CoT XML event into a marker dict, or None if invalid."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None

    if root.tag != "event":
        return None

    point = root.find("point")
    if point is None:
        return None

    try:
        lat = float(point.get("lat"))
        lon = float(point.get("lon"))
    except (TypeError, ValueError):
        return None

    if lat == 0.0 and lon == 0.0:
        # Null-island / no-fix placeholder, not a real position.
        return None

    detail = root.find("detail")
    callsign = None
    if detail is not None:
        contact = detail.find("contact")
        if contact is not None:
            callsign = contact.get("callsign")

    try:
        hae = float(point.get("hae") or 0.0)
    except (TypeError, ValueError):
        hae = 0.0

    return {
        "uid": root.get("uid"),
        "type": root.get("type"),
        "lat": lat,
        "lon": lon,
        "hae": hae,
        "callsign": callsign or root.get("uid") or "UNKNOWN",
        "time": root.get("time"),
    }
