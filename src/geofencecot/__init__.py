#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot: CoT Geo-fence Guard.

"""geofencecot: reads CoT markers via UDP multicast and alerts on geofence breach."""

from pathlib import Path

__version__ = (
    Path(__file__).resolve().parent.joinpath("VERSION").read_text(encoding="utf-8").strip()
)

from geofencecot.constants import (  # noqa: E402
    ALERT_911,
    ALERT_GEOFENCE_BREACHED,
    ALERT_IN_CONTACT,
    ALERT_RING_THE_BELL,
    DEFAULT_ALERT_COOLDOWN_S,
    DEFAULT_ALERT_COT_TYPE,
    DEFAULT_ALERT_STALE,
    DEFAULT_ALERT_TYPE,
    DEFAULT_CALLSIGN,
    DEFAULT_COT_STALE,
    DEFAULT_DISTANCE_THRESHOLD_M,
    DEFAULT_GPS_INFO_CMD,
    DEFAULT_IGNORE_ABOVE_M,
    DEFAULT_IGNORE_OWN_UID,
    DEFAULT_MULTICAST_PORT,
    DEFAULT_POLL_INTERVAL,
    MACHINE_ID_PATHS,
    VALID_ALERT_TYPES,
)
from geofencecot.functions import (  # noqa: E402
    build_alert_cot_bytes,
    build_alert_cot_xml,
    create_tasks,
)
from geofencecot.classes import GeofenceWorker  # noqa: E402
