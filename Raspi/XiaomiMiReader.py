#!/usr/bin/python
# -*- coding: utf8 -*-

# ----------------------------------------------------------------
# ----- Simple XaiomiMi Measurement Data Collector for RasPi -----
# ----------------------------------------------------------------
# Current features:
#   - current tested for Python 2.7 or better, not 3.x (!)
#   - read the data of up to 20 Sensors via BLT 4.x
#   - Export of data into a MySQL / MariaSQL DB (for access of other processes if necessary)
#   - Export of data into a Influx-DB (for Grafana visualizing)
#   - Log of data into a external log file
#
# The Python script will be run per cron job.
# For a good performance, low battery load of sensors and smooth visibility
# of data a call cycle of >= 15 min are recommented.
#
#
# -----
# Author:
#   Ralf Wiessner (Nick: Zentris)
#   eMail: 4git@zentris.net
#   Blog: http://www.n8chteule.de/zentris-blog/
#
# -----
# Contributions from other sources:
#   Parts of my code were inspired by the following sources:
#       https://github.com/ChristianKuehnel/plantgateway
#       https://github.com/open-homeautomation/miflora
#
# -----
# History:
#   Remark: This version is an older version (State of code is from 15/03/2017)
#           The code is used by me at the time, a newer version is in progress.
#
#   15/03/2017 : v0.2.1
#                   - read the data of up to 20 Sensors via BLT 4.x
#                   - Export of data into a MySQL / MariaSQL DB
#                   - Export of data into a Influx-DB (for Grafana visualizing)
#                   - Log of data into a external log file
# ----------------------------------------------------

# - - - - - - - - - - - - - - - -  - - - - - - - -
# =================     ReadMe & Hints   ===================
# - - - - - - - - - - - - - - - -  - - - - - - - -
# All data to configure the reader will be set into the configuration
# file "config.cfg".
# This file must be located in the same directory where this python file is stored.
#
# Necessary additional python modules (normally not per default installed):
#   * influxdb
#   * json
#   * pymysql
#   * configparser
#
# Database (MySQL or MariaSQL):
#   Before you starts the database must be installed on our server.
#   The relevant SQL Script to create is stored into the fiel "DB-Giesssensoren.sql".
#
# Visualisation of data:
#   A good way (for my opinion) is Grafana/Influx.
#   This solution must be installed before and after than configured.
#   Please look to INet how to you do this (is very simple).
#
# Current use (15.07.2017) is shown on: (ask me per Mail or take a lock into my Blog)
# - - - - - - - - - - - - - - - -  - - - - - - - -


import logging
import os

import helper
import SQLConnector
import XiaomiMiConnector

#---------------------------
# config data structure for influx database connection
# :: This structure are represent the config data structure
#
# :: Do not change if you do not know what you're doing
#---------------------------
class cfgInflux:
    Section = "influx-vm2-sensors"
    Host = "influxHost"
    Port = "influxPort"
    User = "influxUser"
    Password = "influxPassword"
    DbName = "influxDbName"
    DbUser = "influxDbUser"
    DbPassword = "influxDbPassword"
    Measurement = "influxMeasurement"

# config data structure for main options data
# :: This structure are represent the config data structure
#
# :: Do not change if you do not know what you're doing
#---------------------------
class cfgOptions:
    Section = "options"
    tracelevel = "tracelevel"
    pingIp = "pingip"

# config data structure for sensor data
# :: This structure are represent the config data structure
#
# :: Do not change if you do not know what you're doing
#---------------------------
class cfgSensors:
    Section = "XiaomiMiSensors"
    SensorPrefix = "sens_"

# config data structure for mysql access data
# :: This structure are represent the config data structure
#
# :: Do not change if you do not know what you're doing
#---------------------------
class cfgMySql:
    Section = "mysql-cubi-Giessensoren"
    DbHost = "DbHost"
    DbUser = "DbUser"
    DbPassword = "DbPassword"
    DbName = "DbName"
    DbTableName = "DbTableName"
    TableMapping = "tableMapping"

#---------------------------
# Mapping and white list (filtering of not used data) for Mysql-DB insert
# :: This structure are represent the config data structure
#
# :: Do not change if you do not know what you're doing
#---------------------------
SQLTableMapping = {"mac": "sensormac",
                   "collectorip": "collectorip",
                   "collectormac": "collectormac",
                   "date": "date",
                   "time": "time",
                   "moisture": "moisture",
                   "temperature": "temperature",
                   "light": "light",
                   "conductivity": "conductivity",
                   "battery": "battery",
                   "cputmp" : "cputmp"}



# for test or stand alone work via cron job
if __name__ == '__main__':
    logfilename = helper.Helper.getFilenameWithDate(filename=os.path.basename(__file__))
    logging.basicConfig(filename=logfilename, level=logging.DEBUG, datefmt="%d.%m.%Y %H:%M:%S",
                        format="%(asctime)s [%(levelname)-8s] [%(module)s:%(funcName)s:%(lineno)d]: %(message)s")
    log = logging.getLogger()
    log.info("------------Start measurement------------")

    cfg = helper.ConfigData(filename="./config.cfg")
    cfg.readIn()

    # set log level from config file
    lglvl = cfg.getData(cfgOptions.Section, cfgOptions.tracelevel, default="INFO", type=str)
    print(lglvl)
    if lglvl.upper() == "INFO":
        log.setLevel(logging.INFO)
    elif lglvl.upper() == "WARNING":
        log.setLevel(logging.WARNING)
    elif lglvl.upper() == "DEBUG":
        log.setLevel(logging.DEBUG)
    elif lglvl.upper() == "ERROR":
        log.setLevel(logging.ERROR)
    elif lglvl.upper() == "CRITICAL":
        log.setLevel(logging.CRITICAL)

    # get my own mac for statistics and for information, which collector the data has scan.
    ownMac= helper.Helper.getMAC(separeate=':', capitalization=True)                 # without decoration
    ownIp = None
    try:
        ownIp = helper.Helper.getIP(cfg.getData(cfgOptions.Section, cfgOptions.pingIp, "192.168.178.1", str))    # Fritzbox pinging
    except Exception as ex:
        log.error("Own IP can not be determined ('{}')".format(ex.message))

    log.info("ownIP='{}', ownMAC='{}'".format(ownIp, ownMac))
    log.debug("Loglevel={}".format(log.getEffectiveLevel()))

    # read sensor macs from config file
    SensorsMac = []
    for sensorCounter in range(1, 20):
        s = cfg.getData(cfgSensors.Section, "{}{}".format(cfgSensors.SensorPrefix, sensorCounter))
        if s is not None:
            SensorsMac.append(s)

    # starts sensor calling
    for mac in SensorsMac:
        log.info("Measurement starts for sensor mac={}".format(mac))
        miSensor = None
        try:
            print("connect to Sensor {}".format(mac))
            miSensor = XiaomiMiConnector.XiaomiMiSens(log, mac)
        except Exception as ex:
            log.error("Exception: {}".format(ex))
            continue

        sensorDaten = miSensor.getAllData()

        sensorDaten["collectorip"] = ownIp
        sensorDaten["collectormac"] = ownMac
        sensorDaten["cputmp"] = helper.Helper.getCpuTemp(float)

        # print(sensorDaten)
        for val in sensorDaten:
            print("{} = {}".format(val, sensorDaten.get(val)))

        # Write data into Influx database
        inflx = None
        inflx = helper.InfluxConnector(log,
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.Host)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.Port)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.User)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.Password)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.DbName)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.DbUser)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.DbPassword)),
                                   str(cfg.getData(cfgInflux.Section, cfgInflux.Measurement, default="XiaomiMiSensors"))
                                   )
        inflx.writeData(sensorDaten, aTimeShift="+01:00", aTraceOn=True, aTestOnly=False)

        # Write data into MySQL database ()
        try:
            db = SQLConnector.MySQLConnector(log,
                                         cfg.getData(cfgMySql.Section, cfgMySql.DbHost),
                                         cfg.getData(cfgMySql.Section, cfgMySql.DbUser),
                                         cfg.getData(cfgMySql.Section, cfgMySql.DbPassword),
                                         cfg.getData(cfgMySql.Section, cfgMySql.DbName),
                                         cfg.getData(cfgMySql.Section, cfgMySql.DbTableName))

            db.writeData(sensorDaten, nameMapping=SQLTableMapping)
            db.closeDbConnection()
        except Exception as ex:
            log.error("MySQL database not rechable or other error: '{}'".format(ex))

        log.info("Measurement ends for sensor mac={}".format(mac))

    log.info("------------End measurement------------{}".format(os.linesep))


