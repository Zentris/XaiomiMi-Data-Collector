#!/usr/bin/python
#  -*- coding: utf8 -*-

import pymysql
import helper


# ----------------------------------------------------
# MySQL/MariaSQL database connector class
# ----------------------------------------------------
class MySQLConnector:
    __versionNumber = "3.0.0"

    @staticmethod
    def getVersion(self):
        return self.__versionNumber

    def __init__(self, log=None, dbHost=None, dbUser=None, dbPassword=None, dbName=None, dbTableName=None,
                 nameMapping=None, charset="utf8"):
        assert (dbHost is not None), "Error: database host ip is mandatory"
        assert (dbUser is not None), "Error: database user is mandatory"
        assert (dbPassword is not None), "Error: database password is mandatory"
        assert (dbName is not None), "Error: database name is mandatory"
        assert (dbTableName is not None), "Error: database table name is mandatory"

        self.log = log
        self.host = dbHost
        self.user = dbUser
        self.password = dbPassword
        self.dbName = dbName
        self.dbTableName = dbTableName
        self.nameMapping = nameMapping
        self.charset = charset
        self.mydb = None

        self.connect()

    def connect(self):
        try:
            self.mydb = pymysql.connect(host=self.host, database=self.dbName, user=self.user, password=self.password, charset=self.charset)
            if self.log is not None:
                self.log.info("Connection aufgebaut zu DbHost '{}', DB '{}' als DbUser '{}'".format(self.host, self.dbName, self.user))
            else:
                print("Connection aufgebaut zu DbHost '{}', DB '{}' als DbUser '{}'".format(self.host, self.dbName, self.user))
        except pymysql.Error as e:
            print(e)
            if self.log is not None:
                self.log.error("Connection to DbHost '{}', DB '{}' als DbUser '{}' failed: {}".format(self.host, self.dbName, self.user, e))
            else:
                print("Connection to DbHost='{}', DB='{}' as DbUser='{}' with pw='{}' failed: {}".format(self.host, self.dbName, self.user, self.password,  e))

    def select(self, query=None, letCommit=True):
        assert (query is not None), "Error: no query given"

        if self.log is not None:
            self.log.info("query = {}".format(query))
        cursor = self.mydb.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        if letCommit:
            self.mydb.commit()
        cursor.close()
        return data

    def commit(self):
        self.mydb.commit()

    def closeDbConnection(self):
        self.mydb.close()

    def countFromTable(self, tablename=None):
        assert (tablename is not None), "Error: no tablename given"

        cursor = self.mydb.cursor()
        cursor.execute("select count(*) from {}".format(tablename))
        data = cursor.fetchall()
        cursor.close()
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

    def writeData(self, dataSet_outside, closeConnection=False, nameMapping=None):
        if self.log is not None:
            self.log.info("incoming data set: {}".format(dataSet_outside))
        if nameMapping is not None:
            self.nameMapping = nameMapping

        dataSet = dataSet_outside.copy()

        if "date" in dataSet:
            dataSet["date"], dataSet["time"] = helper.Helper.reformatDateTimeString(dataSet["date"],
                                                                                    dataSet["time"])

            # Filterung auf gültige Tags wird absichtlich "late" gemacht, somit kümmert sich jeder
            # Connector selbst um die Validierung der für ihn zulässigen Werte !
            sqlDataSet = {}
            for k in dataSet.keys():
                # remapping and ignoring non accepted tags
                if self.nameMapping is not None:
                    if k not in self.nameMapping:
                        if self.log is not None:
                            self.log.warning("MySQLConnector: Tag '{}' not accepted, ignored and remove from data set".format(k))
                        dataSet.pop(k)
                    else:
                        sqlDataSet[self.nameMapping[k]] = dataSet[k]
                else:
                    sqlDataSet = dataSet

            if self.log is not None:
                self.log.info("final data set to send: '{}'".format(sqlDataSet))

            self.insert(tablename=self.dbTableName, values=sqlDataSet)

            if closeConnection:
                self.closeDbConnection()
        else:
            if self.log is not None:
                self.log.error("Dataset contained no 'date' tag, nothing to send.")



# for test or stand alone work
if __name__ == '__main__':
    pass
