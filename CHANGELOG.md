# geofencecot 1.0.0

- Initial release.
- `GeofenceWorker`: reads CoT markers via UDP multicast (e.g.
  `udp+wo://239.2.3.1:6969`), joining the group directly regardless of the
  configured URL scheme.
- Own position from static `STATIC_LAT`/`STATIC_LON`/`STATIC_HAE` config or
  `gpsd` via `GPS_INFO_CMD` (`gpspipe`), same pattern as lincot.
- Haversine distance check against `DISTANCE_THRESHOLD_M`, with
  `IGNORE_ABOVE_M` noise filter, `ALERT_COOLDOWN_S` de-dupe, and
  `IGNORE_OWN_UID` self-alert protection.
- Sends an ATAK-compatible `<emergency>` CoT alert (911 Alert, Ring The
  Bell, Geo-fence Breached, In Contact) back onto the CoT bus on breach.
