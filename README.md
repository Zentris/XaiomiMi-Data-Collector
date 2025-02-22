
##### Bitte zuerst lesen!

#### Ziel
* Auslesen von Xiaomi Plant Sensoren.
* Das Pythonprogramm *XiaomiMiReader.py* kann manuell oder per cron job gestartet werden.
* Die wichtigsten Laufzeit-Parameter werden in einer Konfigurations-Datei *config.cfg* ausgelagert, welche einmalig beim Start des Programms ausgelesen werden.
* Code-Grundlage https://github.com/open-homeautomation/miflora verwendet (stark angepasst)

#### Hauptfunktionen
 * Auslesen von bis zu 20 Xiaomi Plant Sensoren (Wert durch Änderung im Code einstellbar)
 * Ausgelesen werden Erdfeuchte, Temperatur, Leitwert, Helligkeit, Batteriespannung, Version
 * Ausgabe/Bereitstellung der Daten in Form eines Dictionary
 * Schreiben der Daten in Datenbanken: MySQL und Influx (für schnelle Darstellung mit Grafana)
 
#### Vorrausetzungen
* installiertes Python > V2.6 (Code ist auch unter Python 3.x funktionsfähig, jedoch nicht intensiv getestet).
* **Notwendige zusätzliche Python module**:
   * `influxdb`
   * `json`
   * `pymysql`
   * `configparser`
   
* BLE-fähiger Bluetooth-Stick (entfällt, wenn ein RasPi mit vorhandenem Bluetooth verwendet wird, z.B. RaspberryPi Zero W)
* funktionierender Bluetooth Stack innerhalb des verwendeten Betriebssystems
* Installierter MySQL- oder MariaSQL-Server auf der gleichen Maschine oder remote auf einer anderen Maschine
   * Hinweis: Der für die DB verwendete User muss Zugriff auf die DB haben (Freigabe einrichten!) 

* Getestet wurde aktuell nur unter Ubuntu 16.04 LTE und Rasbian Jessy auf RasPi Zero W

#### Files

##### Direktory /Raspi
* **XiaomiMiReader.py**     : Hauptklasse 
* **XiaomiMiConnector.py**  : Hilfscode zum Auslesen der Sensoren
* **SQLConnector.py**       : SQL Hilfsklasse
* **helper.py**             : Allgemeine Hilfsklasse, Influx Connector
* **config.cfg**            : Konfigurationseinstellungen
* **startsens.sh**          : Startscript mit Logging für cronjob Starts

##### Direktory /database
* **DB-Giesssensoren.sql**  : SQL Strukturdump der SQL Datenbank

##### Direktory /system
* **crontab**               : crontab Eintrag
* **homeautomation**        : File für logrotate für Housekeeping der Logfiles 

#### Visualisierung der Daten
* Wenn die Daten in eine Influx-DB gesendet werden, ist **Grafana** ein sehr flexibles Werkzeug zur Visualisierung der Daten.
* ~~Aktuell (21.08.17) kann die bei mir laufende Anwendung hier angesehen werden: http://www.n8chteule.de/zentris-blog/sensoren-im-netz-live-view/~~



