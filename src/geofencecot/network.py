#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot network / multicast helpers.

"""Multicast socket helpers for reading CoT markers off the wire.

geofencecot listens for markers on the same host:port given in COT_URL
(e.g. ``udp://239.2.3.1:6969`` or ``udp+wo://239.2.3.1:6969``). The URL
scheme is only meaningful to PyTAK's own writer (used to *send* alerts);
for *receiving* we open our own multicast socket directly, independent of
the scheme prefix, and simply join the multicast group at that address.
"""

import socket
import struct
from typing import Tuple

import geofencecot


def parse_multicast_url(cot_url: str) -> Tuple[str, int]:
    """Extract (host, port) from a CoT URL, ignoring the scheme prefix."""
    _, _, rest = str(cot_url).partition("://")
    rest = rest or str(cot_url)
    host_port = rest.split("/", 1)[0]
    if ":" in host_port:
        host, port_str = host_port.rsplit(":", 1)
        port = int(port_str)
    else:
        host, port = host_port, geofencecot.DEFAULT_MULTICAST_PORT
    return host, port


def open_multicast_listener(host: str, port: int) -> socket.socket:
    """Open, bind, and join a UDP socket to the given multicast group."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
    sock.bind(("", port))
    mreq = struct.pack("4sl", socket.inet_aton(host), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)
    return sock
