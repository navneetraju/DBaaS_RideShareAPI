-- phpMyAdmin SQL Dump
-- version 4.8.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 02, 2020 at 08:25 AM
-- Server version: 10.1.35-MariaDB
-- PHP Version: 7.2.9

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flask`
--
CREATE DATABASE IF NOT EXISTS `flask` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `flask`;

-- --------------------------------------------------------

--
-- Table structure for table `rides`
--

CREATE TABLE `rides` (
  `rideId` int(11) NOT NULL,
  `username` varchar(200) NOT NULL,
  `_timestamp` varchar(200) NOT NULL,
  `source` varchar(200) NOT NULL,
  `destination` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `rides`
--

INSERT INTO `rides` (`rideId`, `username`, `_timestamp`, `source`, `destination`) VALUES
(4, 'user3', '23-01-2030:12-12-10', '56', '21'),
(5, 'user3', '23-01-2030:12-12-10', '5', '51');

-- --------------------------------------------------------

--
-- Table structure for table `urides`
--

CREATE TABLE `urides` (
  `username` varchar(200) NOT NULL,
  `rideId` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `username` varchar(200) NOT NULL,
  `password` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`username`, `password`) VALUES
('user1', '3d725109c7e7c0bfb9d709836735b56d943d263f'),
('user2', '3d725039c7e7c0bfb9d709836735b56d943d263f'),
('user3', '3d72503c97e7c0bfb9d709836735b56d943d263f'),
('user4', '3d72503c97e7c0bfb9d709836735b56d943d263f'),
('user5', '3d72503c17e7c0bfb9d709836735b56d943d263f'),
('user6', '3d72503c17e7c0bfb9d709836455b56d943d263f');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `rides`
--
ALTER TABLE `rides`
  ADD PRIMARY KEY (`rideId`);

--
-- Indexes for table `urides`
--
ALTER TABLE `urides`
  ADD PRIMARY KEY (`rideId`,`username`),
  ADD KEY `username` (`username`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `rides`
--
ALTER TABLE `rides`
  MODIFY `rideId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `urides`
--
ALTER TABLE `urides`
  ADD CONSTRAINT `urides_ibfk_1` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE,
  ADD CONSTRAINT `urides_ibfk_2` FOREIGN KEY (`rideId`) REFERENCES `rides` (`rideId`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
