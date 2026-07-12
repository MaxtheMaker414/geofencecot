#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# geofencecot Class Definitions.

"""geofencecot worker: read CoT markers via UDP multicast, alert on breach."""

import asyncio
import time
from typing import Dict

import pytak

import geofencecot
from geofencecot.distance import haversine_m
from geofencecot.functions import build_alert_cot_bytes
from geofencecot.identity import get_uid
from geofencecot.marker import parse_marker
from geofencecot.network import open_multicast_listener, parse_multicast_url
from geofencecot.position import get_own_position


class GeofenceWorker(pytak.QueueWorker):
    """Listen for CoT markers, compute distance to own position, alert on breach."""

    async def run(self, _=-1) -> None:
        """Run worker loop: read multicast CoT markers and evaluate distance."""
        cot_url = self.config.get("COT_URL")
        if not cot_url:
            self._logger.error("COT_URL not set, exiting.")
            return

        host, port = parse_multicast_url(cot_url)
        self._logger.info("Listening for CoT markers on %s:%s", host, port)

        self.threshold_m: float = float(
            self.config.get("DISTANCE_THRESHOLD_M")
            or geofencecot.DEFAULT_DISTANCE_THRESHOLD_M
        )
        self.ignore_above_m: float = float(
            self.config.get("IGNORE_ABOVE_M") or geofencecot.DEFAULT_IGNORE_ABOVE_M
        )
        self.cooldown_s: int = int(
            self.config.get("ALERT_COOLDOWN_S") or geofencecot.DEFAULT_ALERT_COOLDOWN_S
        )
        self.ignore_own_uid: bool = str(
            self.config.get("IGNORE_OWN_UID", geofencecot.DEFAULT_IGNORE_OWN_UID)
        ).strip().lower() not in ("false", "0", "no")

        self._last_alert: Dict[str, float] = {}
        self._own_uid = get_uid(self.config)

        try:
            sock = open_multicast_listener(host, port)
        except OSError as exc:
            self._logger.error("Could not join multicast group %s:%s: %s", host, port, exc)
            return

        loop = asyncio.get_running_loop()
        try:
            while True:
                try:
                    data, _addr = await loop.sock_recvfrom(sock, 65535)
                except (BlockingIOError, InterruptedError):
                    await asyncio.sleep(0.1)
                    continue
                except OSError as exc:
                    self._logger.warning("Socket read error: %s", exc)
                    await asyncio.sleep(1)
                    continue

                try:
                    await self._handle_datagram(data)
                except Exception as exc:  # noqa: BLE001 - keep the listener alive
                    self._logger.warning("Error handling marker: %s", exc)
        finally:
            sock.close()

    async def _handle_datagram(self, data: bytes) -> None:
        """Parse one CoT datagram and alert if it breaches the geofence."""
        marker = parse_marker(data)
        if marker is None:
            return

        uid = marker.get("uid") or "unknown"
        if self.ignore_own_uid and uid == self._own_uid:
            return

        own_pos = get_own_position(self.config)
        if own_pos is None:
            self._logger.debug(
                "Own position unavailable, cannot evaluate marker %s", uid
            )
            return
        own_lat, own_lon, own_hae = own_pos

        distance_m = haversine_m(own_lat, own_lon, marker["lat"], marker["lon"])

        if self.ignore_above_m > 0 and distance_m > self.ignore_above_m:
            self._logger.debug(
                "Ignoring marker %s at %.1fm (> IGNORE_ABOVE_M=%.1fm)",
                uid,
                distance_m,
                self.ignore_above_m,
            )
            return

        if distance_m > self.threshold_m:
            return

        now = time.monotonic()
        last = self._last_alert.get(uid, 0.0)
        if now - last < self.cooldown_s:
            self._logger.debug("Marker %s still in alert cooldown", uid)
            return
        self._last_alert[uid] = now

        self._logger.warning(
            "Geo-fence breach: %s (%s) at %.1fm (threshold=%.1fm)",
            marker.get("callsign"),
            uid,
            distance_m,
            self.threshold_m,
        )

        alert_bytes = build_alert_cot_bytes(
            self.config, marker, own_lat, own_lon, own_hae, distance_m
        )
        await self.put_queue(alert_bytes)
