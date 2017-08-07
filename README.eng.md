### ReadMe & Hints   
All data to configure the reader will be set into the configuration  file "`config.cfg`".
This file must be located in the same directory where this python file is stored.

#### Necessary additional python modules** (normally not per default installed):
   * `influxdb`
   * `json`
   * `pymysql`
   * `configparser`
---
#### Database 
   * MySQL or MariaSQL Database 
   * optional: InfluxDB (time based DB for Grafana)
Before you starts the database must be installed on our server.
The relevant **SQL Script to create** is stored into the file "`DB-Giesssensoren.sql`".
---
#### Visualisation of data:
A good way (for my opinion) is **Grafana/Influx**.
This solution must be installed before and after than configured.
Please look to INet how to you do this (is very simple).
---
#### Current use (15.07.2017) is shown on: 
(ask me per Mail or take a lock into my Blog)