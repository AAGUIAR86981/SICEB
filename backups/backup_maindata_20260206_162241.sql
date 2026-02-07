/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.6.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: maindata
-- ------------------------------------------------------
-- Server version	11.6.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Current Database: `maindata`
--

/*!40000 DROP DATABASE IF EXISTS `maindata`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `maindata` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin */;

USE `maindata`;

--
-- Table structure for table `cat_departamentos`
--

DROP TABLE IF EXISTS `cat_departamentos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cat_departamentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_departamentos`
--

LOCK TABLES `cat_departamentos` WRITE;
/*!40000 ALTER TABLE `cat_departamentos` DISABLE KEYS */;
INSERT INTO `cat_departamentos` VALUES
(1,'Tecnologia',1,'2026-02-06 19:40:01'),
(2,'Logistica',1,'2026-02-06 19:41:19'),
(3,'RRHH',1,'2026-02-06 19:42:34'),
(4,'Ventas',1,'2026-02-06 19:43:04');
/*!40000 ALTER TABLE `cat_departamentos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cat_tipos_nomina`
--

DROP TABLE IF EXISTS `cat_tipos_nomina`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cat_tipos_nomina` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_tipos_nomina`
--

LOCK TABLES `cat_tipos_nomina` WRITE;
/*!40000 ALTER TABLE `cat_tipos_nomina` DISABLE KEYS */;
/*!40000 ALTER TABLE `cat_tipos_nomina` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catalogo_productos`
--

DROP TABLE IF EXISTS `catalogo_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `catalogo_productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catalogo_productos`
--

LOCK TABLES `catalogo_productos` WRITE;
/*!40000 ALTER TABLE `catalogo_productos` DISABLE KEYS */;
INSERT INTO `catalogo_productos` VALUES
(1,'Harina Precocida','Alimento',1,'2026-02-06 19:45:42'),
(2,'Aceite vegetal','Alimento',1,'2026-02-06 19:47:27'),
(3,'Alas de Pollo','Proteína',1,'2026-02-06 19:47:55'),
(4,'Pechuga de Pollo','Proteína',1,'2026-02-06 19:49:50'),
(5,'Muslos de Pollo','Proteína',1,'2026-02-06 19:50:36'),
(6,'Arroz','Grano',1,'2026-02-06 19:50:55'),
(7,'Caraota','Grano',1,'2026-02-06 19:51:27');
/*!40000 ALTER TABLE `catalogo_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combo_items`
--

DROP TABLE IF EXISTS `combo_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `combo_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `combo_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_combo_producto` (`combo_id`,`producto_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `combo_items_ibfk_1` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `combo_items_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `catalogo_productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combo_items`
--

LOCK TABLES `combo_items` WRITE;
/*!40000 ALTER TABLE `combo_items` DISABLE KEYS */;
INSERT INTO `combo_items` VALUES
(1,1,3,1),
(2,1,1,2),
(3,1,2,1),
(4,1,6,1);
/*!40000 ALTER TABLE `combo_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `combos`
--

DROP TABLE IF EXISTS `combos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `combos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `combos_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `combos`
--

LOCK TABLES `combos` WRITE;
/*!40000 ALTER TABLE `combos` DISABLE KEYS */;
INSERT INTO `combos` VALUES
(1,'Semana del 9 al 14/02/2026','Combo Básico inicial',1,NULL,'2026-02-06 19:53:38','2026-02-06 19:53:38');
/*!40000 ALTER TABLE `combos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `empleados` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_empleado` int(11) NOT NULL,
  `cedula` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `departamento` varchar(50) NOT NULL,
  `tipoNomina` int(2) NOT NULL DEFAULT 1,
  `boolValidacion` int(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idEmpleado_cedula` (`id_empleado`,`cedula`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
INSERT INTO `empleados` VALUES
(28,1001,20000001,'Pedro','Garcia','Recursos Humanos',3,1),
(29,1002,20000002,'Sofia','Gonzalez','Ventas',2,1),
(30,1003,20000003,'Sofia','Torres','Recursos Humanos',4,1),
(31,1004,20000004,'Jose','Garcia','Logistica',3,1),
(32,1005,20000005,'Miguel','Garcia','Administracion',1,1),
(33,1006,20000006,'Jorge','Martinez','Administracion',4,1),
(34,1007,20000007,'Elena','Sanchez','Administracion',1,1),
(35,1008,20000008,'Sofia','Lopez','Logistica',2,1),
(36,1009,20000009,'Sofia','Garcia','Recursos Humanos',1,1),
(37,1010,20000010,'Carmen','Garcia','Ventas',2,1),
(38,1011,20000011,'Pedro','Lopez','Logistica',2,1),
(39,1012,20000012,'Pedro','Gonzalez','Logistica',1,1),
(40,1013,20000013,'Carmen','Lopez','Ventas',1,1),
(41,1014,20000014,'David','Garcia','Ventas',1,1),
(42,1015,20000015,'David','Garcia','Ventas',2,1),
(43,1016,20000016,'Pedro','Perez','Logistica',1,1),
(44,1017,20000017,'Pedro','Hernandez','Recursos Humanos',1,1),
(45,1018,20000018,'Sofia','Perez','Almacen',1,1),
(46,1019,20000019,'Elena','Sanchez','Logistica',2,1),
(47,1020,20000020,'Carmen','Hernandez','Ventas',4,1),
(48,1021,20000021,'Carmen','Sanchez','Ventas',3,1),
(49,1022,20000022,'Miguel','Garcia','Almacen',2,1),
(50,1023,20000023,'Jorge','Perez','Logistica',1,1),
(51,1024,20000024,'Carmen','Martinez','Logistica',2,1),
(52,1025,20000025,'Pedro','Gonzalez','Ventas',2,1),
(53,1026,20000026,'Jose','Torres','Administracion',3,1),
(54,1027,20000027,'Elena','Perez','Almacen',2,1),
(55,1028,20000028,'Miguel','Sanchez','Logistica',1,1),
(56,1029,20000029,'Jorge','Hernandez','Almacen',4,1),
(57,1030,20000030,'David','Lopez','Almacen',1,1),
(58,1031,20000031,'Miguel','Gonzalez','Administracion',4,1),
(59,1032,20000032,'Jorge','Torres','Recursos Humanos',4,1),
(60,1033,20000033,'Pedro','Sanchez','Administracion',1,1),
(61,1034,20000034,'Jose','Rodriguez','Ventas',3,1),
(62,1035,20000035,'Miguel','Hernandez','Almacen',1,1),
(63,1036,20000036,'Pedro','Garcia','Recursos Humanos',2,1),
(64,1037,20000037,'Pedro','Gonzalez','Administracion',1,1),
(65,1038,20000038,'David','Torres','Administracion',2,1),
(66,1039,20000039,'Carmen','Hernandez','Almacen',2,1),
(67,1040,20000040,'Laura','Ramirez','Almacen',1,1),
(68,1041,20000041,'Miguel','Hernandez','Ventas',2,1),
(69,1042,20000042,'David','Garcia','Logistica',1,1),
(70,1043,20000043,'Laura','Gonzalez','Logistica',2,1),
(71,1044,20000044,'Jose','Martinez','Almacen',2,1),
(72,1045,20000045,'Jose','Gonzalez','Recursos Humanos',1,1),
(73,1046,20000046,'Ana','Rodriguez','Logistica',3,1),
(74,1047,20000047,'Carmen','Gonzalez','Ventas',4,1),
(75,1048,20000048,'Laura','Garcia','Ventas',2,1),
(76,1049,20000049,'Jorge','Sanchez','Ventas',2,1),
(77,1050,20000050,'Jorge','Martinez','Administracion',4,1),
(78,1051,20000051,'INVALIDO','TEST_51','Sin Asignar',1,0),
(79,1052,20000052,'INVALIDO','TEST_52','Sin Asignar',1,0),
(80,1053,20000053,'INVALIDO','TEST_53','Sin Asignar',1,0),
(81,1054,20000054,'INVALIDO','TEST_54','Sin Asignar',1,0),
(82,1055,20000055,'INVALIDO','TEST_55','Sin Asignar',1,0);
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados_audit`
--

DROP TABLE IF EXISTS `empleados_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `empleados_audit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empleado_id` int(11) DEFAULT NULL,
  `accion` enum('INSERT','UPDATE','DELETE') NOT NULL,
  `campo_modificado` varchar(100) DEFAULT NULL,
  `valor_anterior` text DEFAULT NULL,
  `valor_nuevo` text DEFAULT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `fecha_modificacion` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_empleado` (`empleado_id`),
  KEY `idx_fecha` (`fecha_modificacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados_audit`
--

LOCK TABLES `empleados_audit` WRITE;
/*!40000 ALTER TABLE `empleados_audit` DISABLE KEYS */;
/*!40000 ALTER TABLE `empleados_audit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(100) NOT NULL,
  `module` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES
(1,'Crear Provisiones','create_provisions','provisions'),
(2,'Ver Historial','view_history','provisions'),
(3,'Ver Empleados Aprobados','view_approved_employees','employees'),
(4,'Ver Empleados No Aprobados','view_unapproved','employees'),
(5,'Crear Usuarios','create_users','auth'),
(6,'Gestionar Roles','manage_roles','auth');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prov_emp_logs`
--

DROP TABLE IF EXISTS `prov_emp_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prov_emp_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idEmpleado` int(11) NOT NULL,
  `semana` int(11) NOT NULL,
  `boolValidacion` tinyint(1) NOT NULL,
  `fechaProv` datetime(3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prov_emp_logs`
--

LOCK TABLES `prov_emp_logs` WRITE;
/*!40000 ALTER TABLE `prov_emp_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `prov_emp_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prov_logs`
--

DROP TABLE IF EXISTS `prov_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prov_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `semana` varchar(50) NOT NULL,
  `cantAprob` int(11) NOT NULL,
  `cantRecha` int(11) NOT NULL,
  `tipoNom` varchar(100) NOT NULL,
  `Usuario` varchar(100) NOT NULL,
  `fechaProv` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prov_logs`
--

LOCK TABLES `prov_logs` WRITE;
/*!40000 ALTER TABLE `prov_logs` DISABLE KEYS */;
INSERT INTO `prov_logs` VALUES
(1,'1',0,0,'Semanal','Admin Principal','2026-02-04 22:07:38'),
(2,'1',0,0,'Quincenal','Admin Principal','2026-02-04 22:09:21'),
(3,'1',18,0,'Quincenal','Admin Principal','2026-02-04 22:13:31'),
(4,'1',18,0,'Quincenal','Admin Principal','2026-02-04 22:14:11'),
(5,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:14:28'),
(6,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:22:59'),
(7,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:23:09'),
(8,'1',18,0,'Quincenal','Admin Principal','2026-02-04 22:23:58'),
(9,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:24:47'),
(10,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:26:02'),
(11,'1',18,5,'Semanal','Admin Principal','2026-02-04 22:26:37'),
(12,'1',18,5,'Semanal','Admin Principal','2026-02-05 12:31:43'),
(13,'1',18,0,'Quincenal','Luis Visualizador','2026-02-05 12:35:56');
/*!40000 ALTER TABLE `prov_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provision_configs`
--

DROP TABLE IF EXISTS `provision_configs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provision_configs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `week_number` varchar(50) NOT NULL,
  `provision_type` enum('semanal','quincenal') NOT NULL,
  `active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provision_configs`
--

LOCK TABLES `provision_configs` WRITE;
/*!40000 ALTER TABLE `provision_configs` DISABLE KEYS */;
INSERT INTO `provision_configs` VALUES
(1,'1','semanal',1,'2026-02-04 21:52:27'),
(2,'1','quincenal',1,'2026-02-04 21:52:27');
/*!40000 ALTER TABLE `provision_configs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provision_items`
--

DROP TABLE IF EXISTS `provision_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provision_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provision_config_id` int(11) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `provision_config_id` (`provision_config_id`),
  CONSTRAINT `provision_items_ibfk_1` FOREIGN KEY (`provision_config_id`) REFERENCES `provision_configs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provision_items`
--

LOCK TABLES `provision_items` WRITE;
/*!40000 ALTER TABLE `provision_items` DISABLE KEYS */;
INSERT INTO `provision_items` VALUES
(1,1,'Harina',2),
(2,1,'Arroz',2),
(3,1,'Pasta',2),
(4,1,'Azucar',1),
(5,1,'Aceite',1),
(6,2,'Pollo',1),
(7,2,'Carne',1),
(8,2,'Huevos',1),
(9,2,'Queso',1),
(10,2,'Mortadela',1);
/*!40000 ALTER TABLE `provision_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provision_productos_historial`
--

DROP TABLE IF EXISTS `provision_productos_historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provision_productos_historial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provision_id` int(11) NOT NULL,
  `producto_nombre` varchar(100) NOT NULL,
  `cantidad` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_provision` (`provision_id`),
  CONSTRAINT `provision_productos_historial_ibfk_1` FOREIGN KEY (`provision_id`) REFERENCES `provisiones_historial` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provision_productos_historial`
--

LOCK TABLES `provision_productos_historial` WRITE;
/*!40000 ALTER TABLE `provision_productos_historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `provision_productos_historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provisiones_historial`
--

DROP TABLE IF EXISTS `provisiones_historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provisiones_historial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_provision` varchar(20) NOT NULL,
  `semana` int(11) NOT NULL,
  `productos` text NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT current_timestamp(),
  `usuario_id` int(11) DEFAULT NULL,
  `usuario_nombre` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provisiones_historial`
--

LOCK TABLES `provisiones_historial` WRITE;
/*!40000 ALTER TABLE `provisiones_historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `provisiones_historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `punchlog`
--

DROP TABLE IF EXISTS `punchlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `punchlog` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `devdt` datetime NOT NULL,
  `devid` varchar(255) NOT NULL,
  `devnm` varchar(255) DEFAULT NULL,
  `user_name` varchar(255) DEFAULT NULL,
  `bsevtc` varchar(255) NOT NULL,
  `bsevtid` varchar(255) NOT NULL,
  `bsevtdt` datetime NOT NULL,
  `user_id` varchar(255) DEFAULT NULL,
  `bsevtm` varchar(255) NOT NULL,
  `bsevtli` varchar(255) DEFAULT NULL,
  `tk` varchar(255) DEFAULT NULL,
  `tki` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `punchlog_unique_idx` (`bsevtli`,`devdt`,`bsevtid`),
  KEY `punchlog_idx_1` (`devdt`),
  KEY `punchlog_idx_2` (`bsevtdt`),
  KEY `punchlog_idx_3` (`bsevtid`),
  KEY `punchlog_idx_4` (`bsevtm`),
  KEY `punchlog_idx_5` (`bsevtli`),
  KEY `punchlog_idx_6` (`devid`),
  KEY `punchlog_idx_7` (`user_id`),
  KEY `punchlog_idx_8` (`tk`),
  KEY `punchlog_idx_9` (`bsevtc`),
  KEY `punchlog_idx_10` (`type`),
  KEY `punchlog_idx_11` (`devid`,`tk`)
) ENGINE=InnoDB AUTO_INCREMENT=187065 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `punchlog`
--

LOCK TABLES `punchlog` WRITE;
/*!40000 ALTER TABLE `punchlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `punchlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role_permissions` (
  `role_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_activities`
--

DROP TABLE IF EXISTS `user_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_activities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_date` timestamp NULL DEFAULT current_timestamp(),
  `user_id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `activity_type` varchar(100) NOT NULL,
  `activity_details` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_activities_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_activities`
--

LOCK TABLES `user_activities` WRITE;
/*!40000 ALTER TABLE `user_activities` DISABLE KEYS */;
INSERT INTO `user_activities` VALUES
(1,'2026-02-04 22:05:24',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(2,'2026-02-04 22:06:08',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(3,'2026-02-04 22:06:27',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(4,'2026-02-04 22:06:44',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(5,'2026-02-04 22:06:44',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(6,'2026-02-04 22:23:45',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(7,'2026-02-04 22:23:45',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(8,'2026-02-04 22:25:44',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(9,'2026-02-04 22:25:44',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(10,'2026-02-04 22:34:26',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(11,'2026-02-04 22:44:07',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(12,'2026-02-04 23:41:02',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(13,'2026-02-04 23:41:02',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(14,'2026-02-04 23:49:59',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(15,'2026-02-05 00:16:43',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(16,'2026-02-05 00:16:51',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(17,'2026-02-05 00:16:51',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(18,'2026-02-05 00:17:20',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(19,'2026-02-05 00:17:20',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(20,'2026-02-05 00:39:06',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(21,'2026-02-05 00:49:46',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(22,'2026-02-05 02:48:57',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(23,'2026-02-05 02:49:04',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(24,'2026-02-05 02:49:04',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(25,'2026-02-05 02:49:31',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(26,'2026-02-05 12:31:16',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(27,'2026-02-05 12:31:26',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(28,'2026-02-05 12:31:26',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(29,'2026-02-05 12:33:15',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(30,'2026-02-05 12:34:03',4,'visor1','Solicitud de restablecimiento','Usuario solicitó restablecer contraseña'),
(31,'2026-02-05 12:34:53',4,'visor1','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(32,'2026-02-05 12:35:13',4,'visor1','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(33,'2026-02-05 12:35:36',4,'visor1','Inicio de sesión','El usuario inició sesión correctamente'),
(34,'2026-02-05 12:35:36',4,'visor1','Inicio de sesión','El usuario inició sesión correctamente'),
(35,'2026-02-05 12:37:19',4,'visor1','Cierre de sesión','Usuario cerró sesión'),
(36,'2026-02-05 14:43:25',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(37,'2026-02-05 14:43:25',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(38,'2026-02-05 14:45:39',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(39,'2026-02-05 14:46:38',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(40,'2026-02-05 14:46:38',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(41,'2026-02-05 14:54:28',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(42,'2026-02-05 14:54:35',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(43,'2026-02-05 14:54:35',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(44,'2026-02-05 14:55:08',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(45,'2026-02-05 14:55:58',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(46,'2026-02-05 14:55:58',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(47,'2026-02-05 14:57:21',1,'admin','Cierre de sesión','Usuario cerró sesión'),
(48,'2026-02-06 19:16:07',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(49,'2026-02-06 19:16:07',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(50,'2026-02-06 19:23:53',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(51,'2026-02-06 19:24:00',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(52,'2026-02-06 19:24:00',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(53,'2026-02-06 19:45:42',1,'Admin Principal','Creación de producto','Producto \"Harina Precocida\" creado (ID: 1)'),
(54,'2026-02-06 19:47:27',1,'Admin Principal','Creación de producto','Producto \"Aceite vegetal\" creado (ID: 2)'),
(55,'2026-02-06 19:47:55',1,'Admin Principal','Creación de producto','Producto \"Alas de Pollo\" creado (ID: 3)'),
(56,'2026-02-06 19:49:50',1,'Admin Principal','Creación de producto','Producto \"Pechuga de Pollo\" creado (ID: 4)'),
(57,'2026-02-06 19:50:08',1,'Admin Principal','Actualización de producto','Producto \"Alas de Pollo\" actualizado (ID: 3)'),
(58,'2026-02-06 19:50:36',1,'Admin Principal','Creación de producto','Producto \"Muslos de Pollo\" creado (ID: 5)'),
(59,'2026-02-06 19:50:55',1,'Admin Principal','Creación de producto','Producto \"Arroz\" creado (ID: 6)'),
(60,'2026-02-06 19:51:27',1,'Admin Principal','Creación de producto','Producto \"Caraota\" creado (ID: 7)'),
(61,'2026-02-06 20:01:27',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(62,'2026-02-06 20:01:36',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(63,'2026-02-06 20:01:36',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(64,'2026-02-06 20:02:46',1,'admin','Intento de inicio de sesión fallido','Contraseña incorrecta'),
(65,'2026-02-06 20:02:51',1,'admin','Inicio de sesión','El usuario inició sesión correctamente'),
(66,'2026-02-06 20:02:51',1,'admin','Inicio de sesión','El usuario inició sesión correctamente');
/*!40000 ALTER TABLE `user_activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_logs`
--

DROP TABLE IF EXISTS `user_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `userID` int(11) NOT NULL,
  `loggedAt` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `userID` (`userID`),
  CONSTRAINT `user_logs_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_logs`
--

LOCK TABLES `user_logs` WRITE;
/*!40000 ALTER TABLE `user_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_roles` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `assigned_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `isAdmin` tinyint(1) DEFAULT 0,
  `name` varchar(100) DEFAULT NULL,
  `lastname` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `activo` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'admin','admin@example.com','$pbkdf2-sha256$29000$qzXmXEsJ4dxbq7X23hvj3A$GNDejFd9iMsZeQGOSZtMIu4EV3sfQoIObjdEwb7fnjw',1,'Admin','Principal','2026-02-04 21:52:27',1),
(2,'supervisor1','supervisor1@test.com','$pbkdf2-sha256$29000$ca6Vsjbm3Fvr3RtDSAlh7A$jOzCYyWqgMwhz1Q5JIjaTKbJd73PrbhDzxM9HSsQlvc',0,'Carlos','Supervisor','2026-02-04 22:11:42',1),
(3,'usuario1','usuario1@test.com','$pbkdf2-sha256$29000$EqIUohRizHnPWQshBIAwJg$qENlUOq2MSurF5iIPHn9OAm84COFzh48AS242QlbtVI',0,'Maria','Usuario','2026-02-04 22:11:42',1),
(4,'visor1','visor1@test.com','$pbkdf2-sha256$29000$9p4zZuxdS0mpNSaEkFKqlQ$Lo0lK03GDUM1.L8mYUHB3OoVuK8SwBeRWZ9bDiF3UZY',0,'Luis','Visualizador','2026-02-04 22:11:42',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'maindata'
--

--
-- Dumping routines for database 'maindata'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-02-06 16:22:43
