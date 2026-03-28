-- 数据库表结构

-- 创建用户偏好表
CREATE TABLE IF NOT EXISTS user_preferences (
  id INT AUTO_INCREMENT PRIMARY KEY,
  taste VARCHAR(50),
  budget INT,
  time INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建食堂食物表
CREATE TABLE IF NOT EXISTS canteen_foods (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  taste VARCHAR(50),
  price INT NOT NULL,
  wait_time INT NOT NULL,
  location VARCHAR(100),
  description TEXT
);

-- 插入示例数据
INSERT INTO canteen_foods (name, taste, price, wait_time, location, description) VALUES
('麻辣香锅', '川菜', 12, 8, '二食堂三楼', '自选配菜，麻辣鲜香'),
('重庆小面', '川菜', 9, 5, '一食堂一楼', '地道重庆风味，劲道爽滑'),
('麻辣烫', '川菜', 10, 10, '美食街A区', '荤素搭配，汤底浓郁'),
('广式烧腊', '粤菜', 15, 12, '三食堂二楼', '正宗广式风味'),
('寿司拼盘', '日韩料理', 25, 15, '留学生食堂', '新鲜食材，口感丰富'),
('意大利面', '西餐', 22, 10, '西餐厅', '经典意式风味'),
('泰式咖喱饭', '东南亚菜', 18, 12, '国际美食区', '正宗泰国咖喱'),
('鲁菜糖醋里脊', '鲁菜', 16, 15, '一食堂二楼', '酸甜可口，外酥里嫩'),
('淮扬狮子头', '淮扬菜', 14, 18, '二食堂二楼', '传统淮扬名菜'),
('福建沙县小吃', '闽菜', 10, 5, '小吃街', '经济实惠，品种丰富');
