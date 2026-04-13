const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: String('localhost'),
  user: String('root'),
  password: String('zzh061218'),
  database: String('canteen'),
  charset: 'utf8mb4',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

module.exports = pool;
