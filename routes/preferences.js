const express = require('express');
const router = express.Router();
const pool = require('../config/db');

// 测试数据库连接
router.get('/test_db', async (req, res) => {
  try {
    console.log('Testing database connection...');
    const [result] = await pool.execute('SELECT 1');
    console.log('Database connection successful:', result);
    res.json({ success: true, message: 'Database connection successful' });
  } catch (error) {
    console.error('Database connection error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Database connection error',
      details: error.message
    });
  }
});

// 接收前端提交的偏好
router.post('/submit_preference', async (req, res) => {
  try {
    console.log('Received request:', req.body);
    const { taste, budget, time } = req.body;
    
    // 确保数据类型正确
    const tasteStr = taste ? String(taste) : null;
    const budgetNum = budget ? Number(budget) : null;
    const timeNum = time ? Number(time) : null;
    
    console.log('Processed params:', { tasteStr, budgetNum, timeNum });
    
    // 保存到数据库
    console.log('Saving to database...');
    const [result] = await pool.execute(
      'INSERT INTO user_preferences (taste, budget, time, created_at) VALUES (?, ?, ?, NOW())',
      [tasteStr, budgetNum, timeNum]
    );
    console.log('Insert result:', result);
    
    // 生成推荐（根据预算和时间过滤）
    console.log('Generating recommendations...');
    const [recommendations] = await pool.execute(
      'SELECT * FROM canteen_foods WHERE price <= ? AND wait_time <= ? LIMIT 5',
      [budgetNum || 999, timeNum || 999]
    );
    console.log('Recommendations found:', recommendations.length);
    
    // 确保返回的数据都是字符串类型
    const formattedRecommendations = recommendations.map(item => ({
      ...item,
      name: String(item.name),
      taste: item.taste ? String(item.taste) : null,
      location: String(item.location),
      description: item.description ? String(item.description) : null
    }));
    
    res.json({
      success: true,
      recommendations: formattedRecommendations,
      extractedParams: { taste: tasteStr, budget: budgetNum, time: timeNum }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Internal server error',
      details: error.message
    });
  }
});

module.exports = router;
