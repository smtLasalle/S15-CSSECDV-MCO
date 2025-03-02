CREATE DATABASE  IF NOT EXISTS `secdevdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `secdevdb`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: secdevdb
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `expense_list`
--

DROP TABLE IF EXISTS `expense_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expense_list` (
  `user_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `price` int NOT NULL,
  `expense_date` date DEFAULT (curdate()),
  `isIncome` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expense_list`
--

LOCK TABLES `expense_list` WRITE;
/*!40000 ALTER TABLE `expense_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `expense_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goal_list`
--

DROP TABLE IF EXISTS `goal_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goal_list` (
  `user_id` int NOT NULL,
  `goal_name` varchar(255) NOT NULL,
  `price` int DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goal_list`
--

LOCK TABLES `goal_list` WRITE;
/*!40000 ALTER TABLE `goal_list` DISABLE KEYS */;
/*!40000 ALTER TABLE `goal_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `web_user`
--

DROP TABLE IF EXISTS `web_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `web_user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(25) NOT NULL,
  `isAdmin` int DEFAULT NULL,
  `prof_img` blob,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(75) NOT NULL,
  `phone_number` varchar(15) NOT NULL,
  `password` varchar(255) NOT NULL,
  `salt` varchar(255) NOT NULL,
  `birth_date` date DEFAULT NULL,
  `account_date` date DEFAULT (curdate()),
  `net_worth` int DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `web_user`
--

LOCK TABLES `web_user` WRITE;
/*!40000 ALTER TABLE `web_user` DISABLE KEYS */;
INSERT INTO `web_user` VALUES (1,'zyn',0,NULL,'Shawne','Tumalad','shawne_tumalad@dlsu.edu.ph','+631112223333','b\'\\x07\\xe5\\xc4\\x1b\\xda0\\xd8\\xce\\xcc\\x8a\\xe4\\x021\\x82\\n\\x8dv\\x02\\xd4\\xa9\\x17\\xa2\\x1c\\xee\\x8c\\xe2.\\xfe\\x1d\\x86\\xc2\\xea\'','$2b$30$2G6God4Xu2msZWfgyXVo8.',NULL,'2025-03-03',NULL),(2,'bananaman',0,NULL,'Christian','Ibaoc','christian_ibaoc@dlsu.edu.ph','+632223331111','b\'zM\\x1a/\\xc8\\xf5\\xf0\\xb6\\x8b\\x1bj\\x94\\xe3\\x0c\\x1ca\\xc8\\xaf`\\xbfhnkN\\x92\\xa5\\xbe\\xf8\\xcf\\x8e\\xdc\\xd1\'','$2b$30$H.DcpdVWU/J4w7mkLZxc5e',NULL,'2025-03-03',NULL),(3,'A2-ard',0,NULL,'Jan ','Relucio','jan_relucio@dlsu.edu.ph','+633332221111','b\'\\xa8n\\x067E\\x7f3U(\\xc3\\x84\\xbc\\x06\\xc2K\\xdd\\xcb\\x19u\\xd29\\xef\\xf1s\\x0b\\x14\\xaa7\\xd5bm|\'','$2b$30$DEu42/KyiMNszD3PRhS5k.',NULL,'2025-03-03',NULL),(4,'admin',1,NULL,'Sir','Mantua','mantua@dlsu.edu.ph','+631113332222','b\'\\x8at\\xe6\\\\L\\xad\\x86\\x88Q\\x9b\\xedI\\x0b\\x16V]\\x97L\\xc8U\\xde\\xe5hw~\\x1f\\xec(\\xfclFX\'','$2b$30$Q83vGMG6xkPiOWyXWfS/L.',NULL,'2025-03-03',NULL);
/*!40000 ALTER TABLE `web_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-03  2:25:26
