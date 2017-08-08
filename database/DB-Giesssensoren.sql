-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2+deb7u8
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Erstellungszeit: 08. Aug 2017 um 19:50
-- Server Version: 5.5.54
-- PHP-Version: 5.4.45-0+deb7u7

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Datenbank: `Giesssensoren`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `Logging`
--

DROP TABLE IF EXISTS `Logging`;
CREATE TABLE IF NOT EXISTS `Logging` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `mac` varchar(18) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT 'MAC Address',
  `date` date NOT NULL,
  `time` time NOT NULL,
  `logtext` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `level` tinyint(4) NOT NULL DEFAULT '0' COMMENT 'Log Level Value',
  PRIMARY KEY (`id`),
  KEY `mac` (`mac`),
  KEY `level` (`level`),
  KEY `date` (`date`),
  KEY `time` (`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `Sensordaten`
--

DROP TABLE IF EXISTS `Sensordaten`;
CREATE TABLE IF NOT EXISTS `Sensordaten` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `sensormac` varchar(18) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `collectorip` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  `collectormac` varchar(18) COLLATE utf8_unicode_ci DEFAULT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `moisture` float DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `light` float DEFAULT NULL,
  `conductivity` float DEFAULT NULL,
  `battery` float DEFAULT NULL,
  `cputmp` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `date` (`date`),
  KEY `time` (`time`),
  KEY `collectorip` (`collectorip`),
  KEY `sensormac_2` (`sensormac`),
  KEY `sensormac` (`sensormac`,`collectorip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `Sensoren`
--

DROP TABLE IF EXISTS `Sensoren`;
CREATE TABLE IF NOT EXISTS `Sensoren` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `mac` varchar(18) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `myname` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'frei vergebbarer Name',
  `devicename` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Name des Sensors, der fest im Sensor ist',
  `deviceid` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `osversion` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT 'Version des OS auf dem Sensor',
  `lastchange` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `localisation` text COLLATE utf8_unicode_ci COMMENT 'Standort des Sensors',
  `comment` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`mac`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;
