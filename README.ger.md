Readme deutsch - Ver. 0.2
### Bitte zuerst lesen!

#### Target
* Auslesen von Xiaomi Plant Sensoren
* Das Pythonprogramm *XiaomiMiSens.py* kann ``standalone`` als auch als Klasse in ein anderes Programm ``eingebunden`` (import) werden.
* Die wichtigsten Laufzeit-Parameter sind in einer Konfigurations-Datei *config.cfg* ausgelagert, welche einmalig beim Start des Programms ausgelesen werden.
* Als Code-Grundlage wurde https://github.com/open-homeautomation/miflora verwendet (allerdings stark meinen Bedürfnissen angepasst)

#### Vorrausetzungen
* installiertes Python > V2.6
* BLE-fähiger Bluetooth-Stick
* funktionierender Bluetooth Stack innerhalb des verwendeten Betriebssystems
* **Hinweis**:
  * Getestet wurde aktuell nur unter Ubuntu 16.04 LTE und Rasbian Jessy

#### Hauptfunktionen
 * Auslesen von bis zu 20 Xiaomi Plant Sensoren (Wert erhöhbar)
 * Ausgelesen werden Erdfeucht, Temperatur, Leitwert, Helligkeit, Batteriespannung, Version
 * Ausgabe/Bereitstellung der Daten in Form eines Dictionary

#### Aufbau
* **XiaomiMiSens.py** : Hauptklasse und Hilfscode
* **XiaomiMiSensHelper.py** : allgemeine Helperklasse
* **config.cfg** : Konfigurationseinstellungen

