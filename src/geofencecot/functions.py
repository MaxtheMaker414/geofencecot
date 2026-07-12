#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot functions for building alert Cursor on Target events.

"""Build CoT emergency-alert events when a marker breaches the geofence."""

import uuid
from configparser import SectionProxy
from typing import Union
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import pytak

import geofencecot
from geofencecot.identity import get_callsign, get_uid


def _resolve_alert_type(config: Union[dict, SectionProxy, None]) -> str:
    """Validate ALERT_TYPE against the known ATAK emergency types."""
    config = config or {}
    alert_type = str(config.get("ALERT_TYPE") or geofencecot.DEFAULT_ALERT_TYPE).strip()
    if alert_type not in geofencecot.VALID_ALERT_TYPES:
        return geofencecot.DEFAULT_ALERT_TYPE
    return alert_type


def create_tasks(config: Union[dict, SectionProxy], clitool: pytak.CLITool) -> set:
    """Bootstrap coroutine tasks for this PyTAK application."""
    return {geofencecot.GeofenceWorker(clitool.tx_queue, config)}


def build_alert_cot_xml(
    config: Union[dict, SectionProxy, None],
    marker: dict,
    own_lat: float,
    own_lon: float,
    own_hae: float,
    distance_m: float,
) -> Element:
    """Build a CoT emergency-alert event, reported at the operator's position."""
    config = config or {}

    alert_type = _resolve_alert_type(config)
    cot_type = str(config.get("ALERT_COT_TYPE") or geofencecot.DEFAULT_ALERT_COT_TYPE)
    stale = int(config.get("ALERT_STALE") or geofencecot.DEFAULT_ALERT_STALE)
    callsign = get_callsign(config)
    uid = f"{get_uid(config)}-ALERT-{uuid.uuid4().hex[:8]}"

    threshold = float(
        config.get("DISTANCE_THRESHOLD_M") or geofencecot.DEFAULT_DISTANCE_THRESHOLD_M
    )

    point = pytak.cot_point(lat=own_lat, lon=own_lon, hae=own_hae, ce="10.0", le="10.0")

    contact = Element("contact")
    contact.set("callsign", callsign)

    emergency = Element("emergency")
    emergency.set("type", alert_type)
    emergency.set("cancel", "false")

    link = Element("link")
    link.set("uid", str(marker.get("uid") or ""))
    link.set("type", str(marker.get("type") or ""))
    link.set("relation", "p-p")

    remarks_text = (
        f"Geofence alert ({alert_type}): marker "
        f"{marker.get('callsign')} (uid={marker.get('uid')}) is "
        f"{distance_m:.1f}m away, threshold is {threshold:.1f}m."
    )

    detail = pytak.cot_detail(contact, emergency, link)
    pytak.add_remarks(detail, [remarks_text])

    return pytak.cot_event(
        uid=uid,
        cot_type=cot_type,
        stale=stale,
        point=point,
        detail=detail,
        access=config.get("COT_ACCESS", pytak.DEFAULT_COT_ACCESS),
    )


def build_alert_cot_bytes(
    config: Union[dict, SectionProxy, None],
    marker: dict,
    own_lat: float,
    own_lon: float,
    own_hae: float,
    distance_m: float,
) -> bytes:
    """Serialize the alert CoT event to bytes, ready for transmission."""
    event = build_alert_cot_xml(config, marker, own_lat, own_lon, own_hae, distance_m)
    return pytak.serialize_cot(event, trailing_newline=True)
