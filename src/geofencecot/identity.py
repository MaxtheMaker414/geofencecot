#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot identity helpers (adapted from lincot).

"""Host identity helpers for geofencecot CoT events."""

import re
import socket
from configparser import SectionProxy
from typing import Optional, Union

import geofencecot

_MACHINE_ID_RE = re.compile(r"^[a-f0-9]{32}$")


def get_hostname() -> str:
    """Return the system hostname (short name, no domain)."""
    name = socket.gethostname().strip()
    if "." in name:
        return name.split(".", maxsplit=1)[0]
    return name or "localhost"


def get_machine_id() -> Optional[str]:
    """Read Linux machine-id, if present and valid."""
    for path in geofencecot.MACHINE_ID_PATHS:
        try:
            with open(path, encoding="utf-8") as handle:
                value = handle.read().strip().lower()
        except OSError:
            continue
        if _MACHINE_ID_RE.match(value):
            return value
    return None


def get_callsign(config: Union[dict, SectionProxy, None]) -> str:
    """Callsign for the alert contact element; defaults to hostname."""
    config = config or {}
    override = config.get("CALLSIGN")
    if override is not None and str(override).strip():
        return str(override).strip()
    return get_hostname()


def get_uid(config: Union[dict, SectionProxy, None]) -> str:
    """Stable base uid for alert events; defaults to machine-id."""
    config = config or {}
    override = config.get("COT_UID")
    if override is not None and str(override).strip():
        return str(override).strip()
    machine_id = get_machine_id()
    if machine_id:
        return machine_id
    return f"geofencecot-{get_hostname()}"
