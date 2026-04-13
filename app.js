const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const preferenceRoutes = require('./routes/preferences');

const app = express();

// 中间件
app.use(cors());
app.use(bodyParser.json());

// 路由
app.use('/', preferenceRoutes);

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// 启动服务器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API endpoint: http://localhost:${PORT}/submit_preference`);
  console.log(`Health check: http://localhost:${PORT}/health`);
});
