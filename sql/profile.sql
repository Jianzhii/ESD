-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 12, 2020 at 02:17 AM
-- Server version: 5.7.19
-- PHP Version: 7.1.9
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!40101 SET NAMES utf8mb4 */
;
--
-- Database: `order`
--
CREATE DATABASE IF NOT EXISTS `profile` DEFAULT CHARACTER SET UTF8MB4 COLLATE utf8mb4_0900_ai_ci;
USE `profile`;
-- --------------------------------------------------------
--
-- Table structure for table `portfolio`
--
DROP TABLE IF EXISTS `profile`;
CREATE TABLE IF NOT EXISTS `profile` (
  `user_id` VARCHAR(32) NOT NULL,
  `name` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 2 DEFAULT CHARSET = UTF8MB4;
--
-- Dumping data for table `profile`
--
INSERT INTO `profile` (`user_id`, `name`, `email`)
VALUES ('Apple TAN', 'Apple TAN', 'appleTan@smu.edu.sg');