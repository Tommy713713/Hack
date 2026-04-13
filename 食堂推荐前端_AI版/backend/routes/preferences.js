const express = require('express');
const router = express.Router();
const pool = require('../config/db');

// 接收前端提交的偏好
router.post('/submit_preference', async (req, res) => {
  try {
    const { taste, budget, time } = req.body;
    
    // 保存到数据库
    const [result] = await pool.execute(
      'INSERT INTO user_preferences (taste, budget, time, created_at) VALUES (?, ?, ?, NOW())',
      [taste, budget, time]
    );
    
    // 生成推荐（根据预算和时间过滤）
    const [recommendations] = await pool.execute(
      'SELECT * FROM canteen_foods WHERE price <= ? AND wait_time <= ? LIMIT 5',
      [budget || 999, time || 999]
    );
    
    res.json({
      success: true,
      recommendations: recommendations,
      extractedParams: { taste, budget, time }
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

module.exports = router;
