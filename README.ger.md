Readme deutsch - Ver. 0.2
### Bitte zuerst lesen!

#### Target
* Auslesen von Xiaomi Plant Sensoren
* Das Pythonprogramm *XiaomiMiReader.py* manuell oder per cron job gestartet werden.
* Die wichtigsten Laufzeit-Parameter sind in einer Konfigurations-Datei *config.cfg* ausgelagert, welche einmalig beim Start des Programms ausgelesen werden.
* Als Code-Grundlage wurde https://github.com/open-homeautomation/miflora verwendet (allerdings stark meinen Bedürfnissen angepasst)

#### Vorrausetzungen
* installiertes Python > V2.6
* BLE-fähiger Bluetooth-Stick (einfällt, wenn ein RasPi mit vorhandenem Bluetooth verwendet wird)
* funktionierender Bluetooth Stack innerhalb des verwendeten Betriebssystems
* **Hinweis**:
  * Getestet wurde aktuell nur unter Ubuntu 16.04 LTE und Rasbian Jessy auf RasPi Zero W

#### Hauptfunktionen
 * Auslesen von bis zu 20 Xiaomi Plant Sensoren (Wert erhöhbar)
 * Ausgelesen werden Erdfeucht, Temperatur, Leitwert, Helligkeit, Batteriespannung, Version
 * Ausgabe/Bereitstellung der Daten in Form eines Dictionary
 * Sreiben der Daten in eine Datenbank (MySQL und Influx)

#### Aufbau
* **XiaomiMiReader.py**     : Hauptklasse 
* **XiaomiMiConnector.py**  : Hilfscode zum Auslesen der Sensoren
* **SQLConnector.py**       : SQL Hilfsklasse
* **helper.py**             : Allgemeine Hilfsklasse
* **config.cfg**            : Konfigurationseinstellungen

