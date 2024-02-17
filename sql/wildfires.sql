-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 17, 2024 at 11:09 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wildfires`
--

-- --------------------------------------------------------

--
-- Table structure for table `datasets`
--

CREATE TABLE `datasets` (
  `id` int(11) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `nbr_rows` int(11) NOT NULL DEFAULT 1,
  `fwi_backtrack_size` int(11) NOT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `wildfires_data`
--

CREATE TABLE `wildfires_data` (
  `latitude` float NOT NULL,
  `longitude` float NOT NULL,
  `date` date NOT NULL,
  `dataset_id` int(11) DEFAULT NULL,
  `temperature` float DEFAULT NULL,
  `precipitation` float DEFAULT NULL,
  `air_humidity` float DEFAULT NULL,
  `wind_speed` float DEFAULT NULL,
  `ffmc` float DEFAULT NULL,
  `dmc` float DEFAULT NULL,
  `dc` float DEFAULT NULL,
  `isi` float DEFAULT NULL,
  `bui` float DEFAULT NULL,
  `fwi` float DEFAULT NULL,
  `burned_area` float DEFAULT NULL,
  `emissions` float DEFAULT NULL,
  `burnt` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `datasets`
--
ALTER TABLE `datasets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `wildfires_data`
--
ALTER TABLE `wildfires_data`
  ADD PRIMARY KEY (`latitude`,`longitude`,`date`),
  ADD KEY `dataset_parent` (`dataset_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `datasets`
--
ALTER TABLE `datasets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `wildfires_data`
--
ALTER TABLE `wildfires_data`
  ADD CONSTRAINT `dataset_parent` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
