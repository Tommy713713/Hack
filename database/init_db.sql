-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_canteen;
USE ai_canteen;

-- 用户需求记录表（ai_canteen_assistant）
DROP TABLE IF EXISTS ai_canteen_assistant;
CREATE TABLE ai_canteen_assistant (
    sno CHAR(20) PRIMARY KEY COMMENT '主键（UUID前20位）',
    staste VARCHAR(20) COMMENT '口味需求',
    sbudget VARCHAR(20) COMMENT '预算',
    stime VARCHAR(20) COMMENT '预计用餐时间（含等待时间）',
    speople VARCHAR(20) COMMENT '用餐人数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 菜品信息表（dish）
DROP TABLE IF EXISTS dish;
CREATE TABLE dish (
    sid CHAR(20) PRIMARY KEY COMMENT '主键（可自定义）',
    sname VARCHAR(20) NOT NULL COMMENT '菜品/餐厅名称',
    staste VARCHAR(20) COMMENT '口味（逗号分隔）',
    sprice VARCHAR(20) NOT NULL COMMENT '价格（字符串，如"12"）',
    stime VARCHAR(20) NOT NULL COMMENT '准备时间（分钟，字符串）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入示例数据到 dish 表
INSERT INTO dish (sid, sname, staste, sprice, stime) VALUES
('D001', '水煮鱼', '辣,川菜', '28', '15'),
('D002', '番茄鸡蛋面', '清淡', '12', '8'),
('D003', '麻辣香锅', '辣', '18', '12'),
('D004', '清蒸鲈鱼', '清淡', '35', '20'),
('D005', '宫保鸡丁', '辣', '22', '10'),
('D006', '蒜蓉西兰花', '清淡', '10', '5'),
('D007', '麻婆豆腐', '辣', '12', '7');