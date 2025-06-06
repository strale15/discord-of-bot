-- Create chatter_ci_ping table
CREATE TABLE IF NOT EXISTS chatter_ci_ping (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  chatter_id varchar(50) DEFAULT NULL,
  model_channel_id varchar(50) DEFAULT NULL,
  timestamp datetime DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=517 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Create mma_sent table
CREATE TABLE IF NOT EXISTS mma_sent (
  id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  user_id varchar(100) DEFAULT NULL,
  model_channel_id varchar(100) DEFAULT NULL,
  timestamp datetime DEFAULT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Create nda_signed table
CREATE TABLE IF NOT EXISTS nda_signed (
  user_id bigint(20) unsigned NOT NULL,
  discord_nick varchar(100) DEFAULT NULL,
  full_name varchar(100) DEFAULT NULL,
  sign_time datetime DEFAULT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

CREATE TABLE IF NOT EXISTS `hw_schedule` (
  `id` uuid NOT NULL,
  `img_id` varchar(100) NOT NULL,
  `trainee_id` varchar(100) NOT NULL,
  `completed` tinyint(1) DEFAULT 0,
  `start_time` timestamp NULL DEFAULT NULL,
  `end_time` timestamp NULL DEFAULT NULL,
  `completion_time` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;