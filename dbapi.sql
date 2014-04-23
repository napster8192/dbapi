DROP DATABASE IF EXISTS dbapi;
CREATE DATABASE dbapi DEFAULT CHARACTER SET = utf8;
USE dbapi;

BEGIN;
CREATE TABLE `dbapi_user` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `isAnonymous` tinyint(1) NOT NULL default 0,
    `username` varchar(30) default NULL,
    `about` longtext default NULL,
    `name` varchar(30) default NULL,
    `email` varchar(75) NOT NULL UNIQUE
)
;
CREATE TABLE `dbapi_forum` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(40) NOT NULL,
    `short_name` varchar(30) NOT NULL UNIQUE,
    `user_id` integer default NULL
)
;
ALTER TABLE `dbapi_forum` ADD CONSTRAINT `user_id_refs_id_9b906e5e` FOREIGN KEY (`user_id`) REFERENCES `dbapi_user` (`id`);
CREATE TABLE `dbapi_thread` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `isDeleted` tinyint(1) NOT NULL default 0,
    `forum_id` integer NOT NULL,
    `title` longtext NOT NULL,
    `isClosed` tinyint(1) NOT NULL default 0,
    `user_id` integer NOT NULL,
    `date` datetime NOT NULL,
    `message` longtext NOT NULL,
    `slug` varchar(40) NOT NULL,
    `likes` integer NOT NULL default 0,
    `dislikes` integer NOT NULL default 0,
    `points` integer NOT NULL default 0,
    `posts` integer NOT NULL default 0
)
;
ALTER TABLE `dbapi_thread` ADD CONSTRAINT `user_id_refs_id_70afe974` FOREIGN KEY (`user_id`) REFERENCES `dbapi_user` (`id`);
ALTER TABLE `dbapi_thread` ADD CONSTRAINT `forum_id_refs_id_e90cdd8d` FOREIGN KEY (`forum_id`) REFERENCES `dbapi_forum` (`id`);
CREATE TABLE `dbapi_post` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent` integer default NULL,
    `isApproved` tinyint(1) NOT NULL default 0,
    `isHighlighted` tinyint(1) NOT NULL default 0,
    `isEdited` tinyint(1) NOT NULL default 0,
    `isSpam` tinyint(1) NOT NULL default 0,
    `isDeleted` tinyint(1) NOT NULL default 0,
    `date` datetime NOT NULL,
    `thread_id` integer NOT NULL,
    `message` longtext NOT NULL,
    `user_id` integer NOT NULL,
    `forum_id` integer NOT NULL,
    `likes` integer NOT NULL default 0,
    `dislikes` integer NOT NULL default 0,
    `points` integer NOT NULL default 0
)
;
ALTER TABLE `dbapi_post` ADD CONSTRAINT `user_id_refs_id_f14da7ec` FOREIGN KEY (`user_id`) REFERENCES `dbapi_user` (`id`);
ALTER TABLE `dbapi_post` ADD CONSTRAINT `thread_id_refs_id_24f4334d` FOREIGN KEY (`thread_id`) REFERENCES `dbapi_thread` (`id`);
ALTER TABLE `dbapi_post` ADD CONSTRAINT `forum_id_refs_id_4623a46b` FOREIGN KEY (`forum_id`) REFERENCES `dbapi_forum` (`id`);
CREATE TABLE `dbapi_follow` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `follower_id` integer NOT NULL
)
;
ALTER TABLE `dbapi_follow` ADD CONSTRAINT `user_id_refs_id_59be0bc3` FOREIGN KEY (`user_id`) REFERENCES `dbapi_user` (`id`);
ALTER TABLE `dbapi_follow` ADD CONSTRAINT `follower_id_refs_id_59be0bc3` FOREIGN KEY (`follower_id`) REFERENCES `dbapi_user` (`id`);
CREATE TABLE `dbapi_subscription` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `thread_id` integer NOT NULL,
    `user_id` integer NOT NULL
)
;
ALTER TABLE `dbapi_subscription` ADD CONSTRAINT `user_id_refs_id_b47c8fbb` FOREIGN KEY (`user_id`) REFERENCES `dbapi_user` (`id`);
ALTER TABLE `dbapi_subscription` ADD CONSTRAINT `thread_id_refs_id_c2dc83b4` FOREIGN KEY (`thread_id`) REFERENCES `dbapi_thread` (`id`);
COMMIT;
