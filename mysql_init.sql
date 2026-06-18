-- ============================================================
-- 校园智能助手系统 v2.0 — MySQL 初始化建表脚本
-- ============================================================

-- 创建数据库（如尚未创建）
CREATE DATABASE IF NOT EXISTS campus_assistant
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE campus_assistant;

-- ------------------------------------------
-- 用户表
-- ------------------------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `username`      VARCHAR(64)     NOT NULL COMMENT '用户名',
    `password_hash` VARCHAR(256)    NOT NULL COMMENT '密码哈希',
    `nickname`      VARCHAR(64)     DEFAULT NULL COMMENT '昵称',
    `email`         VARCHAR(128)    NOT NULL COMMENT '邮箱',
    `avatar`        VARCHAR(512)    DEFAULT NULL COMMENT '头像URL',
    `role`          ENUM('student','teacher','admin') NOT NULL DEFAULT 'student' COMMENT '角色',
    `status`        TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`),
    INDEX `idx_role` (`role`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ------------------------------------------
-- 聊天记录表
-- ------------------------------------------
DROP TABLE IF EXISTS `chat_history`;
CREATE TABLE `chat_history` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `user_id`       INT             NOT NULL COMMENT '用户 ID',
    `session_id`    VARCHAR(128)    NOT NULL COMMENT '会话标识',
    `role`          VARCHAR(16)     NOT NULL COMMENT '角色: user/assistant/system',
    `content`       TEXT            NOT NULL COMMENT '消息内容',
    `token_count`   INT             DEFAULT NULL COMMENT 'Token 估算数',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_session_id` (`session_id`),
    INDEX `idx_create_time` (`create_time`),
    CONSTRAINT `fk_chat_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天记录表';

-- ------------------------------------------
-- 情绪记录表
-- ------------------------------------------
DROP TABLE IF EXISTS `emotion_record`;
CREATE TABLE `emotion_record` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `user_id`       INT             NOT NULL COMMENT '用户 ID',
    `emotion`       VARCHAR(32)     NOT NULL COMMENT '情绪类别',
    `confidence`    FLOAT           NOT NULL DEFAULT 0.0 COMMENT '置信度',
    `ai_persona`    VARCHAR(32)     DEFAULT NULL COMMENT 'AI 人格',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    PRIMARY KEY (`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_create_time` (`create_time`),
    CONSTRAINT `fk_emotion_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪记录表';

-- ------------------------------------------
-- 学院表
-- ------------------------------------------
DROP TABLE IF EXISTS `college`;
CREATE TABLE `college` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `name`          VARCHAR(128)    NOT NULL COMMENT '学院名称',
    `description`   TEXT            DEFAULT NULL COMMENT '学院简介',
    `logo`          VARCHAR(512)    DEFAULT NULL COMMENT 'Logo URL',
    `sort_order`    INT             NOT NULL DEFAULT 0 COMMENT '排序',
    `status`        TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
    `is_deleted`    TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '软删除',
    `delete_time`   DATETIME        DEFAULT NULL COMMENT '删除时间',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学院表';

-- ------------------------------------------
-- 导师名片表
-- ------------------------------------------
DROP TABLE IF EXISTS `teacher_profile`;
CREATE TABLE `teacher_profile` (
    `id`                  INT             NOT NULL AUTO_INCREMENT,
    `user_id`             INT             NOT NULL COMMENT '关联用户 ID',
    `college_id`          INT             DEFAULT NULL COMMENT '所属学院 ID',
    `avatar`              VARCHAR(512)    DEFAULT NULL COMMENT '头像 URL',
    `real_name`           VARCHAR(64)     NOT NULL COMMENT '真实姓名',
    `title`               VARCHAR(64)     DEFAULT NULL COMMENT '职称',
    `research_direction`  VARCHAR(256)    DEFAULT NULL COMMENT '研究方向',
    `laboratory`          VARCHAR(256)    DEFAULT NULL COMMENT '所属实验室',
    `email`               VARCHAR(128)    DEFAULT NULL COMMENT '联系邮箱',
    `phone`               VARCHAR(32)     DEFAULT NULL COMMENT '联系电话',
    `introduction`        TEXT            DEFAULT NULL COMMENT '个人简介',
    `student_requirement` TEXT            DEFAULT NULL COMMENT '招生要求',
    `homepage`            VARCHAR(512)    DEFAULT NULL COMMENT '个人主页 URL',
    `tags`                VARCHAR(512)    DEFAULT NULL COMMENT '标签',
    `is_deleted`          TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '软删除',
    `delete_time`         DATETIME        DEFAULT NULL COMMENT '删除时间',
    `create_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_id` (`user_id`),
    INDEX `idx_college_id` (`college_id`),
    CONSTRAINT `fk_profile_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_profile_college` FOREIGN KEY (`college_id`) REFERENCES `college`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='导师名片表';

-- ------------------------------------------
-- 知识分类表（无限级）
-- ------------------------------------------
DROP TABLE IF EXISTS `knowledge_category`;
CREATE TABLE `knowledge_category` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `parent_id`     INT             DEFAULT NULL COMMENT '父分类 ID',
    `name`          VARCHAR(128)    NOT NULL COMMENT '分类名称',
    `level`         INT             NOT NULL DEFAULT 0 COMMENT '层级深度',
    `sort_order`    INT             NOT NULL DEFAULT 0 COMMENT '排序',
    `status`        TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
    `is_deleted`    TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '软删除',
    `delete_time`   DATETIME        DEFAULT NULL COMMENT '删除时间',
    `create_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_parent_id` (`parent_id`),
    CONSTRAINT `fk_category_parent` FOREIGN KEY (`parent_id`) REFERENCES `knowledge_category`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识分类表';

-- ------------------------------------------
-- 知识文档表（含异步处理状态）
-- ------------------------------------------
DROP TABLE IF EXISTS `knowledge_document`;
CREATE TABLE `knowledge_document` (
    `id`               INT             NOT NULL AUTO_INCREMENT,
    `category_id`      INT             DEFAULT NULL COMMENT '所属分类 ID',
    `uploader_id`      INT             NOT NULL COMMENT '上传者 ID',
    `title`            VARCHAR(256)    NOT NULL COMMENT '文档标题',
    `file_name`        VARCHAR(512)    NOT NULL COMMENT '原始文件名',
    `file_path`        VARCHAR(1024)   NOT NULL COMMENT '存储路径',
    `file_size`        BIGINT          DEFAULT NULL COMMENT '文件大小（字节）',
    `mime_type`        VARCHAR(128)    DEFAULT NULL COMMENT 'MIME 类型',
    `page_count`       INT             DEFAULT NULL COMMENT '页数',
    `content_text`     LONGTEXT        DEFAULT NULL COMMENT '解析后的文本内容',
    `summary_text`     TEXT            DEFAULT NULL COMMENT 'AI 摘要',
    `parse_status`     VARCHAR(16)     NOT NULL DEFAULT 'waiting' COMMENT '解析状态',
    `embedding_status` VARCHAR(16)     NOT NULL DEFAULT 'waiting' COMMENT '向量化状态',
    `summary_status`   VARCHAR(16)     NOT NULL DEFAULT 'waiting' COMMENT '摘要状态',
    `classify_status`  VARCHAR(16)     NOT NULL DEFAULT 'waiting' COMMENT '分类状态',
    `is_deleted`       TINYINT(1)      NOT NULL DEFAULT 0 COMMENT '软删除',
    `delete_time`      DATETIME        DEFAULT NULL COMMENT '删除时间',
    `create_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_category_id` (`category_id`),
    INDEX `idx_uploader_id` (`uploader_id`),
    INDEX `idx_parse_status` (`parse_status`),
    CONSTRAINT `fk_doc_category` FOREIGN KEY (`category_id`) REFERENCES `knowledge_category`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_doc_uploader` FOREIGN KEY (`uploader_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识文档表';

-- ------------------------------------------
-- 插入默认管理员（密码: admin123）
-- ------------------------------------------
INSERT INTO `user` (`username`, `password_hash`, `nickname`, `email`, `role`, `status`)
VALUES (
    'admin',
    '$2b$12$LJ3m4ys3fUcCKpGfEkFuueaG5fFwzH0xk/YxKq7YEB0i5JYHd5Z1m',
    '系统管理员',
    'admin@campus.edu',
    'admin',
    1
);

-- TODO: 后续模块将在独立的迁移脚本中添加表
-- - 聊天会话表 (chat_sessions)
-- - 系统配置表 (system_config)
-- - 日志分析表 (log_analysis)
