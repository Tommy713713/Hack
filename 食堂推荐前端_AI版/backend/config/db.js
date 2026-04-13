const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: '数据库主机地址', // 例如：localhost
  user: '数据库用户名',    // 例如：root
  password: '数据库密码',   // 例如：123456
  database: '数据库名',     // 例如：canteen
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = pool;
