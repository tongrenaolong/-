create database if not exists OnlineRecord;
use OnlineRecord;
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 题单表
CREATE TABLE IF NOT EXISTS problem_sets (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
-- 题目表
CREATE TABLE IF NOT EXISTS problems (
    problem_id INT AUTO_INCREMENT PRIMARY KEY,
    link VARCHAR(255) NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    difficulty ENUM('easy', 'medium', 'hard') NOT NULL,  -- 题目的难度
    user_id INT,  -- 上传者的用户 ID
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);
-- 刷题状态表
CREATE TABLE IF NOT EXISTS user_problem_status (
    user_id INT,
    problem_id INT,
    status ENUM('not_started', 'completed') DEFAULT 'not_started',
    time_spent INT DEFAULT 0,  -- 所用时间，单位为秒
    PRIMARY KEY (user_id, problem_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
);
-- 订阅表
CREATE TABLE IF NOT EXISTS user_subscriptions (
    user_id INT,
    set_id INT,
    PRIMARY KEY (user_id, set_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (set_id) REFERENCES problem_sets(set_id) ON DELETE CASCADE
);
-- 题单与题目关联表
CREATE TABLE IF NOT EXISTS problem_set_problems (
    set_id INT,
    problem_id INT,
    PRIMARY KEY (set_id, problem_id),
    FOREIGN KEY (set_id) REFERENCES problem_sets(set_id) ON DELETE CASCADE,
    FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
);