#!/usr/bin/env python3
"""Basic tests for geofencecot: distance, marker parsing, alert building."""

import xml.etree.ElementTree as ET

import geofencecot
from geofencecot.distance import haversine_m
from geofencecot.marker import parse_marker
from geofencecot.functions import build_alert_cot_xml, build_alert_cot_bytes
from geofencecot.position import static_position_configured, static_position
from geofencecot.network import parse_multicast_url

SAMPLE_MARKER = b"""<?xml version="1.0"?>
<event version="2.0" uid="ANDROID-deadbeef" type="a-h-G" time="2026-07-12T12:00:00Z"
       start="2026-07-12T12:00:00Z" stale="2026-07-12T12:05:00Z" how="m-g">
    <point lat="52.5210" lon="13.4060" hae="50.0" ce="10.0" le="5.0"/>
    <detail>
        <contact callsign="INTRUDER-1"/>
    </detail>
</event>"""


def test_haversine_zero():
    assert haversine_m(52.52, 13.405, 52.52, 13.405) == 0.0


def test_haversine_known_distance():
    # ~1 degree of latitude is ~111.2 km
    d = haversine_m(0.0, 0.0, 1.0, 0.0)
    assert 110_000 < d < 112_000


def test_parse_marker_ok():
    marker = parse_marker(SAMPLE_MARKER)
    assert marker is not None
    assert marker["uid"] == "ANDROID-deadbeef"
    assert marker["callsign"] == "INTRUDER-1"
    assert abs(marker["lat"] - 52.5210) < 1e-9
    assert abs(marker["lon"] - 13.4060) < 1e-9


def test_parse_marker_null_island_rejected():
    xml_bytes = SAMPLE_MARKER.replace(b'lat="52.5210" lon="13.4060"', b'lat="0.0" lon="0.0"')
    assert parse_marker(xml_bytes) is None


def test_parse_marker_invalid_xml():
    assert parse_marker(b"not xml") is None


def test_static_position_config():
    config = {"STATIC_LAT": "52.5200", "STATIC_LON": "13.4050", "STATIC_HAE": "40.0"}
    assert static_position_configured(config)
    lat, lon, hae = static_position(config)
    assert lat == 52.52
    assert lon == 13.405
    assert hae == 40.0


def test_multicast_url_parsing():
    assert parse_multicast_url("udp+wo://239.2.3.1:6969") == ("239.2.3.1", 6969)
    assert parse_multicast_url("udp://239.2.3.1:6969") == ("239.2.3.1", 6969)
    assert parse_multicast_url("239.2.3.1:6969") == ("239.2.3.1", 6969)


def test_build_alert_cot_xml_within_threshold():
    config = {
        "STATIC_LAT": "52.5200",
        "STATIC_LON": "13.4050",
        "DISTANCE_THRESHOLD_M": "500",
        "ALERT_TYPE": "Geo-fence Breached",
        "CALLSIGN": "TESTNODE",
    }
    marker = parse_marker(SAMPLE_MARKER)
    own_lat, own_lon, own_hae = static_position(config)
    distance_m = haversine_m(own_lat, own_lon, marker["lat"], marker["lon"])

    event = build_alert_cot_xml(config, marker, own_lat, own_lon, own_hae, distance_m)
    xml_str = ET.tostring(event, encoding="unicode")

    assert event.get("type") == geofencecot.DEFAULT_ALERT_COT_TYPE
    assert 'type="Geo-fence Breached"' in xml_str
    assert "cancel=\"false\"" in xml_str
    assert 'callsign="TESTNODE"' in xml_str
    assert f'uid="{marker["uid"]}"' in xml_str

    raw = build_alert_cot_bytes(config, marker, own_lat, own_lon, own_hae, distance_m)
    assert isinstance(raw, bytes)
    assert b"<emergency" in raw


def test_invalid_alert_type_falls_back_to_default():
    config = {
        "STATIC_LAT": "52.5200",
        "STATIC_LON": "13.4050",
        "ALERT_TYPE": "Not A Real Type",
    }
    marker = parse_marker(SAMPLE_MARKER)
    event = build_alert_cot_xml(config, marker, 52.52, 13.405, 0.0, 100.0)
    xml_str = ET.tostring(event, encoding="unicode")
    assert f'type="{geofencecot.DEFAULT_ALERT_TYPE}"' in xml_str


if __name__ == "__main__":
    import sys

    failures = 0
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {t.__name__}: {exc}")
    sys.exit(1 if failures else 0)
