# geofencecot — CoT Geo-fence Guard

geofencecot liest Cursor-on-Target-Marker (CoT) per UDP-Multicast
(z. B. `udp+wo://239.2.3.1:6969`) und berechnet die Entfernung jedes
Markers zur eigenen Position. Die eigene Position kommt entweder von
`gpsd` (`gpspipe`) oder aus einer statisch konfigurierten Koordinate —
genau wie bei [lincot](https://github.com/snstac/lincot), an dessen
Config-Stil sich `example-config.ini` orientiert.

Unterschreitet ein Marker die konfigurierte Entfernung, sendet
geofencecot einen CoT-Alarm-Marker (`<emergency>`-Detail) zurück auf den
gleichen Multicast-Kanal. Das Design ist auf [PyTAK](https://github.com/snstac/pytak)
aufgebaut.

## Installation auf dem Raspberry Pi (via GitHub)

### Debian-Paket (.deb) aus den GitHub Releases (wie bei lincot)

Der mitgelieferte Workflow `.github/workflows/ci.yml` baut bei jedem
Git-Tag (`v1.0.0` z. B.) automatisch ein `.deb`-Paket (`make package`,
über `stdeb`/`dpkg-buildpackage`, exakt der lincot-Build) und lädt es als
GitHub Release hoch. Installation auf dem Pi — 1:1 dieselbe
Zwei-Schritt-Reihenfolge wie im [lincot-README](https://github.com/snstac/lincot#install):
erst die `pytak`-Abhängigkeit als eigenes Debian-Paket, dann
geofencecot selbst:

```sh
wget https://github.com/snstac/pytak/releases/latest/download/pytak_latest_all.deb
sudo apt install -f ./pytak_latest_all.deb
wget https://github.com/MaxtheMaker414/geofencecot/releases/latest/download/python3-geofencecot_latest_all.deb
sudo apt install -f ./python3-geofencecot_latest_all.deb
```

(`apt install -f` löst dabei automatisch weitere Abhängigkeiten wie
Python-Laufzeit-Pakete auf.)

Das Paket installiert genau wie bei lincot einen systemd-Service
(`debian/geofencecot.service`) und legt beim `postinst` einen
dedizierten, unprivilegierten Systembenutzer `geofencecot`
(Gruppe `geofencecot`, Home `/run/geofencecot`, kein Login, kein
Passwort) an — identisches Rechtemodell wie bei lincot mit seinem
`lincot`-Systembenutzer. Der Dienst läuft also nie als root.
Konfiguration danach unter `/etc/default/geofencecot` (analog
`/etc/default/lincot`), Start mit:

```sh
sudo systemctl enable --now geofencecot
sudo journalctl -fu geofencecot
```

Voraussetzung in beiden Optionen: `pytak` (>= 7.3.12) — wird bei
Option A automatisch als Python-Abhängigkeit mitinstalliert, bei
Option B über das separate `pytak`-Debian-Paket (siehe oben). Optional
`gpsd`/`gpspipe` für eigene Live-Position.

## Nutzung

```sh
geofencecot -c config.ini
```

Minimalbeispiel `config.ini`:

```ini
[geofencecot]
COT_URL = udp+wo://239.2.3.1:6969
STATIC_LAT = 52.5200
STATIC_LON = 13.4050
DISTANCE_THRESHOLD_M = 500
ALERT_TYPE = Geo-fence Breached
```

Vollständige Optionen: siehe `example-config.ini`.

## Konfiguration (Kurzüberblick)

- `COT_URL` — Multicast-Adresse, von der Marker gelesen und auf die
  Alarme geschrieben werden.
- `STATIC_LAT` / `STATIC_LON` / `STATIC_HAE` — statische eigene
  Position; wenn leer, wird `GPS_INFO_CMD` (gpsd/gpspipe) benutzt.
- `DISTANCE_THRESHOLD_M` — Alarm-Schwelle in Metern.
- `IGNORE_ABOVE_M` — Marker, die weiter als dieser Wert entfernt sind,
  werden ignoriert (0 = deaktiviert).
- `ALERT_COOLDOWN_S` — Mindestabstand zwischen zwei Alarmen für
  denselben Marker (uid).
- `IGNORE_OWN_UID` — eigene CoT-uid nicht gegen sich selbst prüfen.
- `ALERT_TYPE` — Warnungsart: `911 Alert`, `Ring The Bell`,
  `Geo-fence Breached` oder `In Contact` (ATAK-Emergency-Typen).
- `ALERT_COT_TYPE` — CoT-Typ des Alarm-Events (Standard `b-a-o-tbl`,
  ATAK's Emergency-Alert-Typ).
- `CALLSIGN` / `COT_UID` — Identität für Alarm-Events (Standard:
  Hostname / machine-id).

## Wie der Alarm aussieht

```xml
<event version="2.0" uid="<uid>-ALERT-xxxxxxxx" type="b-a-o-tbl" ...>
  <point lat="..." lon="..." hae="..." ce="10.0" le="10.0"/>
  <detail>
    <contact callsign="..."/>
    <emergency type="Geo-fence Breached" cancel="false"/>
    <link uid="<marker-uid>" type="<marker-type>" relation="p-p"/>
    <remarks>Geofence alert (...): marker ... is ...m away, threshold is ...m.</remarks>
  </detail>
</event>
```

## Lizenz

Apache License 2.0.
