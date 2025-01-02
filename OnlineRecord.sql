drop database OnlineRecord;
create database if not exists OnlineRecord;
use OnlineRecord;
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    account VARCHAR(100) NOT NULL UNIQUE, -- 账号
    username VARCHAR(100) NOT NULL default 'bite', -- 用户名
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 题单表
CREATE TABLE IF NOT EXISTS problem_sets (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    set_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
-- 题目表
-- 创建新的problems表
CREATE TABLE IF NOT EXISTS problems (
    problem_id INT AUTO_INCREMENT PRIMARY KEY,
    problem_name VARCHAR(100) NOT NULL,
    link VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    difficulty ENUM('easy', 'medium', 'hard') NOT NULL,  -- 题目的难度
    user_id INT NOT NULL,  -- 上传者的用户 ID，作为联合主键的一部分
    set_id INT NOT NULL,
    CONSTRAINT problems_unique_user_link UNIQUE (user_id, link,set_id), -- 联合主键
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE, -- user_id 同时为外键
    FOREIGN KEY (set_id) REFERENCES problem_sets(set_id) ON DELETE CASCADE -- set_id 同时为外键
);

-- 刷题状态表
-- 当一个表用来表示两个表的关系的时候，这个表需要有多个字段以满足查找的需求
CREATE TABLE IF NOT EXISTS user_problem_status (
    user_id INT,
    problem_id INT,
    status ENUM('not_started', 'completed') DEFAULT 'not_started',
    time_spent INT DEFAULT 0,  -- 所用时间，单位为秒
    description TEXT DEFAULT NULL,
    image LONGBLOB DEFAULT NULL,
    PRIMARY KEY (user_id, problem_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
);
-- 订阅表
CREATE TABLE IF NOT EXISTS user_subscriptions (
    user_id INT,
    set_id INT,
    authority bool default false,
    PRIMARY KEY (user_id, set_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (set_id) REFERENCES problem_sets(set_id) ON DELETE CASCADE
);