#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot Constants.

"""geofencecot Constants."""

import socket

_hostname = socket.gethostname()

# General / position (same defaults as lincot for a familiar config style)
DEFAULT_COT_STALE: str = "3600"
DEFAULT_POLL_INTERVAL: int = 61
DEFAULT_GPS_INFO_CMD: str = "gpspipe --json -n 5"
MACHINE_ID_PATHS = ("/etc/machine-id", "/var/lib/dbus/machine-id")

# Geofence evaluation
DEFAULT_DISTANCE_THRESHOLD_M: float = 500.0
# 0 disables the "ignore markers farther away than X meters" filter
DEFAULT_IGNORE_ABOVE_M: float = 0.0
DEFAULT_ALERT_COOLDOWN_S: int = 300
DEFAULT_MULTICAST_PORT: int = 6969
DEFAULT_IGNORE_OWN_UID: bool = True

# Alert / CoT emergency detail
# Valid ATAK <emergency type="..."> values.
ALERT_911 = "911 Alert"
ALERT_RING_THE_BELL = "Ring The Bell"
ALERT_GEOFENCE_BREACHED = "Geo-fence Breached"
ALERT_IN_CONTACT = "In Contact"

VALID_ALERT_TYPES = (
    ALERT_911,
    ALERT_RING_THE_BELL,
    ALERT_GEOFENCE_BREACHED,
    ALERT_IN_CONTACT,
)

DEFAULT_ALERT_TYPE: str = ALERT_GEOFENCE_BREACHED
# ATAK's emergency-alert event type ("Drawing/Emergency" atom, see TAK CoT docs)
DEFAULT_ALERT_COT_TYPE: str = "b-a-o-tbl"
DEFAULT_ALERT_STALE: int = 300
DEFAULT_CALLSIGN: str = f"geofencecot-{_hostname}"
