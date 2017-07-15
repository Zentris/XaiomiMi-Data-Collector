#!/usr/bin/python
# -*- coding: utf8 -*-

#from datetime import datetime, timedelta
import inspect
import datetime
import time
import logging
import helper
import re


# ------------------------------------------------------
# class Xiaomi-Mi
# based on code on https://github.com/open-homeautomation/miflora
# ------------------------------------------------------
class XiaomiMiSens:
    """"
    A class to read data from Mi Flora / Xiaomi-Mi plant sensors.
    """
    CLASS_VERSION = "0.2.1:20170314"

    MI_TEMPERATURE = "temperature"
    MI_LIGHT = "light"
    MI_MOISTURE = "moisture"
    MI_CONDUCTIVITY = "conductivity"
    MI_BATTERY = "battery"
    MI_FIRMVERSION = "firmwareversion"
    MI_NAME = "sensorname"
    MI_MAC = "mac"
    MI_DATUM = "date"
    MI_TIME = "time"

    SensDaten = {}

    def __init__(self, logger=None, sensMac=None, cache_timeout=300, retries=3, adapter='hci0'):
        assert sensMac is not None, "[ERROR] XiaomiMiSens.init(): no mac given"

        self.log = logger
        self._sensMac = sensMac
        self._adapter = adapter
        self._cache = None
        self._cacheTimeout = datetime.timedelta(seconds=cache_timeout)
        self._lastRead = None
        self._fw_last_read = datetime.datetime.now()
        self.retries = retries
        self.ble_timeout = 10
        self._firmware_version = None

        self.SensDaten[self.MI_TEMPERATURE] = self.parameter_value(self.MI_TEMPERATURE)
        self.SensDaten[self.MI_MOISTURE] = self.parameter_value(self.MI_MOISTURE)
        self.SensDaten[self.MI_LIGHT] = self.parameter_value(self.MI_LIGHT)
        self.SensDaten[self.MI_CONDUCTIVITY] = self.parameter_value(self.MI_CONDUCTIVITY)
        self.SensDaten[self.MI_BATTERY] = self.parameter_value(self.MI_BATTERY)
        self.SensDaten[self.MI_MAC] = self._sensMac
        self.SensDaten[self.MI_FIRMVERSION] = self.firmware_version()
        self.SensDaten[self.MI_NAME] = self.name()
        self.SensDaten[self.MI_DATUM] = time.strftime("%Y.%m.%d")
        self.SensDaten[self.MI_TIME] = time.strftime("%H:%M:%S")

    def getAllData(self):
        """
        Returned all data in a dictionary
        :return: sensor data dictionary
        """
        return self.SensDaten

    def classLogger(self, loglevel, msg):
        """
        Spezial logger selector
        :param loglevel:
        :param msg:
        :return: None
        """
        frame = inspect.stack()[1][0]
        module = inspect.getmodule(frame)
        addString = "(realLineNo={}): ".format(frame.f_lineno)
        if frame is not None:
            del frame
        if module is not None:
            del module

        if self.log is not None:
            self.log.log(loglevel, addString + msg)
        else:
            print(loglevel, addString + msg)

    def write_ble(self, handle, value):
        """
        Read from a BLE address

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: value - value to write to the given handle
        """

        attempt = 0
        delay = 10

        self.classLogger(logging.DEBUG, "Enter read_ble")

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-write-req -a {} -n {} --adapter={}"\
                .format(self._sensMac, handle, value, self._adapter)
            self.classLogger(logging.DEBUG, "Running gatttool with a timeout of '{}'".format(self.ble_timeout))

            mycmd = helper.cmdCall(logger=self.log, writeConsole=False)
            retVal, stdOut, stdErr = mycmd.execute(cmd)
            if retVal == 0:
                result = stdOut[0]

                self.classLogger(logging.DEBUG, "Got '{}' from gatttool".format(result))
                # Parse the output
                if "successfully" in result:
                    self.classLogger(logging.DEBUG, "Exit read_ble with result '{}'".format(result))
                    return True
            else:
                self.classLogger(logging.ERROR, "Error in connection to Sensor: '{}'".format(stdErr))

            attempt += 1
            self.classLogger(logging.DEBUG, "Waiting for '{}' seconds before retrying".format(delay))
            if attempt < self.retries:
                datetime.time.sleep(delay)
                delay *= 2

        self.classLogger(logging.WARNING, "Exit read_ble, no data.")
        return False

    def read_ble(self, handle):
        """
        Read from a BLE address

        @param: mac - MAC address in format XX:XX:XX:XX:XX:XX
        @param: handle - BLE characteristics handle in format 0xXX
        @param: timeout - timeout in seconds
        """

        attempt = 0
        delay = 1
        self.classLogger(logging.DEBUG, "Enter read_ble")

        while attempt <= self.retries:
            cmd = "gatttool --device={} --char-read -a {} --adapter={}".format(self._sensMac, handle, self._adapter)
            self.classLogger(logging.DEBUG, "Running gatttool with a timeout of '{}'".format(self.ble_timeout))

            mycmd = helper.cmdCall(logger=self.log, writeConsole=False)
            retVal, stdOut, stdErr = mycmd.execute(cmd)
            if retVal == 0:
                self.classLogger(logging.DEBUG, "stdOut='{}'".format(stdOut))

                result = stdOut[0]
                self.classLogger(logging.DEBUG, "Got '{}' from gatttool".format(result))

                # Parse the output
                res = re.search("( [0-9a-fA-F][0-9a-fA-F])+", result)
                if res:
                    self.classLogger(logging.DEBUG, "Exit read_ble with result '{}'".format([int(x, 16) for x in res.group(0).split()]))
                    return [int(x, 16) for x in res.group(0).split()]
            else:
                self.classLogger(logging.ERROR, "Error in connection to Sensor: '{}'".format(stdErr))

            attempt += 1
            self.classLogger(logging.DEBUG, "Waiting for '{}' seconds before retrying".format(delay))
            if attempt < self.retries:
                time.sleep(delay)
                delay *= 2

        self.classLogger(logging.WARNING, "Exit read_ble, no data.")
        return None

    def name(self):
        """
        Return the name of the sensor.
        """
        name = self.read_ble("0x03")
        return ''.join(chr(n) for n in name)

    def fill_cache(self):
        firmware_version = self.firmware_version()
        if not firmware_version:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._lastRead = datetime.datetime.now() - self._cacheTimeout + datetime.timedelta(seconds=300)
            return

        if firmware_version >= "2.6.6":
            if not self.write_ble("0x33", "A01F"):
                # If a sensor doesn't work, wait 5 minutes before retrying
                self._lastRead = datetime.datetime.now() - self._cacheTimeout + datetime.timedelta(seconds=300)
                return
        self._cache = self.read_ble("0x35")
        self._check_data()
        if self._cache is not None:
            self._lastRead = datetime.datetime.now()
        else:
            # If a sensor doesn't work, wait 5 minutes before retrying
            self._lastRead = datetime.datetime.now() - self._cacheTimeout + datetime.timedelta(seconds=300)


    def firmware_version(self):
        """ Return the firmware version. """
        if (self._firmware_version is None) or \
                (datetime.datetime.now() - datetime.timedelta(hours=24) > self._fw_last_read):
            self._fw_last_read = datetime.datetime.now()
            res = self.read_ble('0x38')
            if res is None:
                self.battery = 0
                self._firmware_version = None
            else:
                self.battery = res[0]
                self._firmware_version = "".join(map(chr, res[2:]))
        return self._firmware_version

    def battery_level(self):
        """
        Return the battery level.

        The battery level is updated when reading the firmware version. This
        is done only once every 24h
        """
        self.firmware_version()
        return self.battery

    def parameter_value(self, parameter, readCached=True):
        """
        Return a value of one of the monitored paramaters.

        This method will try to retrieve the data from cache and only
        request it by bluetooth if no cached value is stored or the cache is
        expired.
        This behaviour can be overwritten by the "readCached" parameter.
        """

        # Special handling for battery attribute
        if parameter == self.MI_BATTERY:
            return self.battery_level()

        # Use the lock to make sure the cache isn't updated multiple times
        if (readCached is False) or (self._lastRead is None) or (datetime.datetime.now()-self._cacheTimeout > self._lastRead):
            self.fill_cache()
        else:
            self.classLogger(logging.DEBUG, "Using cache ('{}' < '{}' )".format(datetime.datetime.now() - self._lastRead, self._cacheTimeout))

        if self._cache and (len(self._cache) == 16):
            return self._parseData()[parameter]
        else:
            raise IOError("Could not read data from Mi Flora sensor '{}' ".format(self._sensMac))

    def _check_data(self):
        if self._cache is None:
            return
        if self._cache[7] > 100:  # moisture over 100 procent
            self._cache = None
            return
        if self._firmware_version >= "2.6.6":
            if sum(self._cache[10:]) == 0:
                self._cache = None
                return
        if sum(self._cache) == 0:
            self._cache = None
            return None

    def _parseData(self):
        data = self._cache
        res = {}
        res[self.MI_TEMPERATURE] = float(data[1] * 256 + data[0]) / 10
        res[self.MI_MOISTURE] = data[7]
        res[self.MI_LIGHT] = data[4] * 256 + data[3]
        res[self.MI_CONDUCTIVITY] = data[9] * 256 + data[8]
        return res
