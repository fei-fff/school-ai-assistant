-- ============================================================
-- 校园智能助手系统 v2.1 — MySQL 初始化建表脚本
-- ============================================================

CREATE DATABASE IF NOT EXISTS campus_assistant
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE campus_assistant;

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `username`      VARCHAR(64)     NOT NULL,
    `password_hash` VARCHAR(256)    NOT NULL,
    `nickname`      VARCHAR(64)     DEFAULT NULL,
    `email`         VARCHAR(128)    NOT NULL,
    `avatar`        VARCHAR(512)    DEFAULT NULL,
    `role`          ENUM('student','teacher','admin') NOT NULL DEFAULT 'student',
    `status`        TINYINT(1)      NOT NULL DEFAULT 1,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `chat_history`;
CREATE TABLE `chat_history` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `user_id`       INT             NOT NULL,
    `session_id`    VARCHAR(128)    NOT NULL,
    `role`          VARCHAR(16)     NOT NULL,
    `content`       TEXT            NOT NULL,
    `token_count`   INT             DEFAULT NULL,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_session_id` (`session_id`),
    CONSTRAINT `fk_chat_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `emotion_record`;
CREATE TABLE `emotion_record` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `user_id`       INT             NOT NULL,
    `emotion`       VARCHAR(32)     NOT NULL,
    `confidence`    FLOAT           NOT NULL DEFAULT 0.0,
    `ai_persona`    VARCHAR(32)     DEFAULT NULL,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    CONSTRAINT `fk_emotion_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `college`;
CREATE TABLE `college` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `name`          VARCHAR(128)    NOT NULL,
    `description`   TEXT            DEFAULT NULL,
    `logo`          VARCHAR(512)    DEFAULT NULL,
    `sort_order`    INT             NOT NULL DEFAULT 0,
    `status`        TINYINT(1)      NOT NULL DEFAULT 1,
    `is_deleted`    TINYINT(1)      NOT NULL DEFAULT 0,
    `delete_time`   DATETIME        DEFAULT NULL,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `teacher_profile`;
CREATE TABLE `teacher_profile` (
    `id`                  INT             NOT NULL AUTO_INCREMENT,
    `user_id`             INT             NOT NULL,
    `college_id`          INT             DEFAULT NULL,
    `avatar`              VARCHAR(512)    DEFAULT NULL,
    `real_name`           VARCHAR(64)     NOT NULL,
    `title`               VARCHAR(64)     DEFAULT NULL,
    `research_direction`  VARCHAR(256)    DEFAULT NULL,
    `laboratory`          VARCHAR(256)    DEFAULT NULL,
    `email`               VARCHAR(128)    DEFAULT NULL,
    `phone`               VARCHAR(32)     DEFAULT NULL,
    `introduction`        TEXT            DEFAULT NULL,
    `student_requirement` TEXT            DEFAULT NULL,
    `homepage`            VARCHAR(512)    DEFAULT NULL,
    `tags`                VARCHAR(512)    DEFAULT NULL,
    `is_deleted`          TINYINT(1)      NOT NULL DEFAULT 0,
    `delete_time`         DATETIME        DEFAULT NULL,
    `create_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_id` (`user_id`),
    INDEX `idx_college_id` (`college_id`),
    CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_profile_college` FOREIGN KEY (`college_id`) REFERENCES `college`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `knowledge_category`;
CREATE TABLE `knowledge_category` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `parent_id`     INT             DEFAULT NULL,
    `name`          VARCHAR(128)    NOT NULL,
    `level`         INT             NOT NULL DEFAULT 0,
    `sort_order`    INT             NOT NULL DEFAULT 0,
    `status`        TINYINT(1)      NOT NULL DEFAULT 1,
    `is_deleted`    TINYINT(1)      NOT NULL DEFAULT 0,
    `delete_time`   DATETIME        DEFAULT NULL,
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_parent_id` (`parent_id`),
    CONSTRAINT `fk_category_parent` FOREIGN KEY (`parent_id`) REFERENCES `knowledge_category`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `knowledge_document`;
CREATE TABLE `knowledge_document` (
    `id`               INT             NOT NULL AUTO_INCREMENT,
    `category_id`      INT             DEFAULT NULL,
    `uploader_id`      INT             NOT NULL,
    `title`            VARCHAR(256)    NOT NULL,
    `file_name`        VARCHAR(512)    NOT NULL,
    `file_path`        VARCHAR(1024)   NOT NULL,
    `file_size`        BIGINT          DEFAULT NULL,
    `mime_type`        VARCHAR(128)    DEFAULT NULL,
    `page_count`       INT             DEFAULT NULL,
    `content_text`     LONGTEXT        DEFAULT NULL,
    `summary_text`     TEXT            DEFAULT NULL,
    `current_step`     VARCHAR(16)     NOT NULL DEFAULT 'uploaded',
    `error_message`    TEXT            DEFAULT NULL,
    `parse_status`     VARCHAR(16)     NOT NULL DEFAULT 'waiting',
    `summary_status`   VARCHAR(16)     NOT NULL DEFAULT 'waiting',
    `classify_status`  VARCHAR(16)     NOT NULL DEFAULT 'waiting',
    `embedding_status` VARCHAR(16)     NOT NULL DEFAULT 'waiting',
    `is_deleted`       TINYINT(1)      NOT NULL DEFAULT 0,
    `delete_time`      DATETIME        DEFAULT NULL,
    `create_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_category_id` (`category_id`),
    INDEX `idx_uploader_id` (`uploader_id`),
    INDEX `idx_current_step` (`current_step`),
    CONSTRAINT `fk_doc_category` FOREIGN KEY (`category_id`) REFERENCES `knowledge_category`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_doc_uploader` FOREIGN KEY (`uploader_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 默认管理员
INSERT INTO `user` (`username`, `password_hash`, `nickname`, `email`, `role`, `status`)
VALUES ('admin', '$2b$12$LJ3m4ys3fUcCKpGfEkFuueaG5fFwzH0xk/YxKq7YEB0i5JYHd5Z1m', '系统管理员', 'admin@campus.edu', 'admin', 1);
