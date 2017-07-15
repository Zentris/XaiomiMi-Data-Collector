# coding: utf-8

import sys
import time
import subprocess
import socket
import uuid
import os
import stat
import errno
import threading

from influxdb import InfluxDBClient
import json
import math

import pymysql

if sys.version_info[0] == 2:
    import ConfigParser as cParser
else:
    import configparser as cParser

pymysql.install_as_MySQLdb()


# ----------------------------------------------------
# Common functions helper class
# ----------------------------------------------------
class Helper:
    def __init__(self):
        pass

    @staticmethod
    def getVersion():
        __versionNumber = "4.2.20170424"
        return __versionNumber

    @staticmethod
    def getIP(pingIp = None):
        assert (pingIp is not None), "Error: no ping address given"

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((pingIp, 0))
        ip = s.getsockname()[0]
        s.close()
        return ip

    @staticmethod
    def getMAC(separeate = None, capitalization=False):
        mac = hex(uuid.getnode()).replace('0x', '')
        if capitalization is not False:
            mac = mac.upper()
        return "".join(mac[i:i+2] for i in range(0, 11, 2)) if separeate is None \
            else separeate.join(mac[i:i+2] for i in range(0, 11, 2))

    @staticmethod
    def getCpuTemp(rType=None):
        cmd = cmdCall(writeConsole=None)
        cmd.execute("cat /sys/class/thermal/thermal_zone0/temp")
        if rType is float:
            return float(cmd.getStdOut()[0])/1000
        else:
            return str(float(cmd.getStdOut()[0])/1000)

    @staticmethod
    def reformatDateTimeString(dateString, timeString = None):
        def normaliseDate(date):
            return date.replace(".", "-").replace("_", "-")
        def normaliseTime(time):
            return time.replace(".", ":").replace("-", ":")

        if dateString.find("_") >= 0:   # Format "2012-11-12_12:13:14"
            dVal = dateString.split("_")
            return normaliseDate(dVal[0]), normaliseTime(dVal[1])
        else:
            if timeString is not None:
                return normaliseDate(dateString), normaliseTime(timeString)
            else:
                return normaliseDate(dateString), ""

    @staticmethod
    def getFilenameWithDate(filename="log", path=".", suffix=".log", separator="_", fulltime=False, notime=False):
        """
        Helper function: get a decorated file name for logging or other use.

        :param filename: main part of file name, default='log'
        :param path: the file location, default='.'
        :param suffix: the file suffix, default='.log'
        :param separator: the separator between the filename part and the time stamp
        :param fulltime: a boolean for switching the time stamp: true => 'YYYYMMDD_HHMM'
                                                                 false=> 'YYYYMMDD'
        :param notime: if set to True no time extension will be append to the log name, default=False
        :return: full filled path name
        """

        if not path.endswith(os.sep):
            path = path + os.sep
        if notime is False:
            if fulltime:
                today = time.strftime("%Y%m%d" + separator + "%H%M")
            else:
                today = time.strftime("%Y%m")
        if not suffix.startswith("."):
            suffix = "." + suffix
        return path + filename + separator + today + suffix if notime is False else path + filename + suffix

    @staticmethod
    def safe_cast(val, to_type, default=None):
        if to_type is bool:
            # special handling for different/universal string representations of boolean values
            falseVals = ["False", "false", "falsch", "no", "nein", "n", "0", 0]
            trueVals = ["True", "true", "wahr", "yes", "ja", "y", "1", 1]

            if val in falseVals:
                return False
            elif val in trueVals:
                return True
            else:
                if default is not None:
                    return default
                else:
                    raise ValueError("string value '{}' is invalid for conversion. Valid values for True:[{}], for False:[{}]"
                        .format(val, trueVals, falseVals))
        else:
            try:
                return to_type(val)
            except (ValueError, TypeError):
                return default if default is not None else val

# ----------------------------------------------------
# Command line execution helper
# ----------------------------------------------------
class cmdCall:
    @staticmethod
    def getVersion():
        __versionNumber = "1.1.0"
        return __versionNumber

    def __init__(self, tmpEnv=None, addOsEnv=True, logger=None, writeConsole=True):
        self.tmpEnv = tmpEnv                # additional environment in dictionary style
        self.addOsEnv = addOsEnv            # if True the existing shell env will be added
        self.writeConsole = writeConsole    # write log aData to default console
        self.stdOutArray = []               # string array with stdout content of executed call
        self.stdErrArray = []               # string array with errout content of executed call
        self.retVal = 0                     # return value of executed command
        self.logger = logger                # if a logger class given it will be used also to write out

        self.cmd = ""
        self.process = None

    def execute(self, command, log=True, writeConsole=True):
        """
        @todo: ausbauen mit timeout feature!
        :param command:
        :param timeout:
        :param log:
        :param writeConsole:
        :return:
        """

        e = {}
        self.stdOutArray = []
        self.stdErrArray = []

        if self.addOsEnv:
            e = dict(os.environ)
        if self.tmpEnv is not None:
            e.update(self.tmpEnv)

        if self.logger is not None and log is True:
            self.logger.debug("env: {}".format(e))
            self.logger.info("{:-<10}> '{}'".format("exec", command))
        if self.writeConsole and writeConsole is True:
            print("{:-<14}> '{}'".format("exec", command))

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=e)

        for line in p.stdout.readlines(): self.stdOutArray.append(bytes.decode(line).strip())
        for line in p.stderr.readlines(): self.stdErrArray.append(bytes.decode(line).strip())
        self.retVal = p.wait()

        if self.logger is not None and log is True:
            self.logger.info("{:-<10}> {}".format("return value", self.retVal))
        if self.writeConsole is True and writeConsole is True:
            print("{:-<14}> {}".format("return value", self.retVal))

        return self.retVal, self.stdOutArray, self.stdErrArray

    def getStdOut(self):
        return self.stdOutArray

    def getStdErr(self):
        return self.stdErrArray

    def getRetVal(self):
        return self.retVal


# ----------------------------------------------------
# MySQL helper class
# ----------------------------------------------------
class dbAccessBase:
    @staticmethod
    def getVersion():
        __versionNumber = "1.1.0"
        return __versionNumber

    def __init__(self, log=None, dbhost=None, dbuser=None, dbpw=None, dbname=None, charset="utf8"):
        assert (dbhost is not None),  "dbhost not set"
        assert (dbuser is not None),  "dbuser not set"
        assert (dbpw is not None),  "dbpw not set"
        assert (dbname is not None),  "dbname not set"

        self.dbhost = dbhost
        self.dbuser = dbuser
        self.dbpw = dbpw
        self.dbname = dbname
        self.charset = charset
        self.log = log
        self.connect()

    def connect(self):
        try:
            self.curDb = pymysql.connect(host=self.dbhost, database=self.dbname, user=self.dbuser, password=self.dbpw, charset=self.charset)
            if self.log is not None:
                self.log.info("Connection aufgebaut zu DbHost '{}', DB '{}' als DbUser '{}'".format(self.dbhost, self.dbname, self.dbname))
            else:
                print("Connection aufgebaut zu DbHost '{}', DB '{}' als DbUser '{}'".format(self.dbhost, self.dbname, self.dbname))
        except pymysql.Error as e:
            print(e)
            if self.log is not None:
                self.log.error("Connection to DbHost '{}', DB '{}' als DbUser '{}' failed: {}".format(self.dbhost, self.dbname, self.dbname, e))
            else:
                print("Connection to DbHost='{}', DB='{}' as DbUser='{}' with pw='{}' failed: {}".format(self.dbhost, self.dbname, self.dbuser, self.dbpw,  e))

    def countFromTable(self, tablename=None):
        assert (tablename is not None), "Error: no tablename given"

        self.cursor = self.curDb.cursor()
        self.cursor.execute("select count(*) from {}".format(tablename))
        data = self.cursor.fetchall()
        self.cursor.close()
        self.cursor = None
        return data[0][0]

    def insert(self, tablename=None, values=None, letCommit=True):
        assert (tablename is not None), "Error: no tablename given"
        assert (values is not None), "Error: no values given"

        if len(values) > 0:
            query = "insert into %s (" % tablename
            qvalues = []
            for key in values:
                query += "%s, " % key
                qvalues.append(values.get(key))
            query = query[:-2]
            query += ") values ("
            for v in qvalues:
                query += "'%s', " % v
            query = query[:-2]
            query += ")"

            self.select(query=query, letCommit=letCommit)

    def select(self, query=None, letCommit=True):
        assert (query is not None), "Error: no query given"

        if self.log is not None:
            self.log.info("query = {}".format(query))
        cursor = self.curDb.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        if letCommit:
            self.curDb.commit()
        cursor.close()
        return data

    def commit(self):
        self.curDb.commit()

    def closeDb(self):
        self.curDb.commit()
        #self.curDb.close


# ----------------------------------------------------
# Influx database connector class
# ----------------------------------------------------
class InfluxConnector:
    dataFormatString = 1
    dataFormatFloat = 2

    @staticmethod
    def getVersion():
        __versionNumber = "1.0.0"
        return __versionNumber

    def __init__(self, log, host, port, user, password, dbname, dbuser, dbpassword, dbMeasurement):
        assert (host is not None), "InfluxConnector: host value is None!"
        assert (port is not None), "InfluxConnector: port value is None!"
        assert (user is not None), "InfluxConnector: user name value is None!"
        assert (password is not None), "InfluxConnector: password value is None!"
        assert (dbname is not None), "InfluxConnector: dbname name value is None!"
        assert (dbuser is not None), "InfluxConnector: dbuser name value is None!"
        assert (dbpassword is not None), "InfluxConnector: dbpassword value is None!"
        assert (dbMeasurement is not None), "InfluxConnector: measurement value is None!"
        assert (len(dbMeasurement) > 0), "InfluxConnector: measurement value is empty!"

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpassword = dbpassword
        self.dbMeasurement = dbMeasurement
        self.log = log

        self.myInfluxDb = InfluxDBClient(self.host, self.port, self.user, self.password, self.dbname)
        self.myInfluxDb.create_database(self.dbname)    # repeated call possible, also the database exists
        self.myInfluxDb.switch_user(self.dbuser, self.dbpassword)

    def writeData(self, aDataSet, aTimeShift="Z", aTraceOn=False, aTestOnly=False):
        """
        Write aData into the influx database
        :param aDataSet: a Dictionary where contained the aData, tagged values "date" and "time" are necessarily
        :param aTimeShift: time shift to UTC ("Z"), for MEZ get "+01:00"
        :param aTraceOn: give more output to console
        :param aTestOnly: no sending to influx database
        :return: None
        """
        if self.log is not None:
            self.log.debug("incomming = {}".format(aDataSet))
        dataSet = aDataSet.copy()                #importend! The function changed the dictionary

        inflxDataSet = {}
        inflxDataSet["measurement"] = self.dbMeasurement

        # reformat the date time string
        dataSet["date"], dataSet["time"] = Helper.reformatDateTimeString(dataSet["date"], dataSet["time"])

        if self.log is not None:
            self.log.debug("date/time after reformat: date='{}', time='{}'".format(dataSet["date"], dataSet["time"]))

        inflxDataSet["time"] = "{0}T{1}{2}".format(dataSet["date"], dataSet["time"], aTimeShift)

        # clear useless tags
        if dataSet.has_key("debug"):
            dataSet.pop("debug")
        dataSet.pop("date")
        dataSet.pop("time")

        # assemble the json structure
        inflxDataSet["fields"] = dataSet

        if self.log is not None:
            self.log.info("InfluxConnector: inflxDataSet = {}".format(json.dumps([inflxDataSet])))
        if aTraceOn:
            print(json.dumps([inflxDataSet], sort_keys=True, indent=4))

        if aTestOnly is not True:
            try:
                self.myInfluxDb.write_points([inflxDataSet])
            except Exception as ex:
                msg = "InfluxConnector: inflxDataSet='{}' => Input format error: {}".format(json.dumps([inflxDataSet]), ex)
                if self.log is not None:
                    self.log.error(msg)
                else:
                    print(msg)

    def readData(self, dataset=None, aQuery=None):
        if dataset is None:
            dataset = {}

        self.myInfluxDb.request()
        pass
    # todo: unvollständig!!


# ---------------------------------------------------------
#
# ---------------------------------------------------------
class ConfigData():
    def __init__(self, filename=None):
        self.filename = filename
        self.conf = cParser.RawConfigParser()

    def getParserObject(self):
        return self.conf

    def putData(self, section=None, key=None, value=None):
        assert (section is not None), "Error: no section given"
        assert (key is not None), "Error: no key given"
        assert (value is not None), "Error: no value given"

        if self.conf.has_section(section) is False:
            self.conf.add_section(section)
        self.conf.set(section, key, value)

    def getData(self, section=None, key=None, default=None, type=None):
        assert (section is not None), "Error: no section given"
        assert (key is not None), "Error: no key given"

        val = None
        if self.conf.has_section(section):
            try:
                val = self.conf.get(section, key)
            except cParser.NoOptionError:
                pass

#        return default if val is None and default is not None else val if type is None else Helper.safe_cast(val, type)
        if val is not None and len(val) > 0:
            if type is None:
                return val
            else:
                return Helper.safe_cast(val, type)
        elif default is not None:
            return default
        else:
            return None

    def writeOut(self, filename=None):
        assert (self.filename is not None or filename is not None), "no valid filename given"
        with open(filename if filename is not None else self.filename, "w") as f:
            self.conf.write(f)

    def readIn(self, filename=None):
        assert (self.filename is not None or filename is not None), "no valid filename given"
        self.conf.read(filename if filename is not None else self.filename)

