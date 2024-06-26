const express = require('express');
const router = express.Router();
const session = require('express-session');
const mysql = require('mysql');

// Database connection setup
const connection = mysql.createConnection({
  host: '127.0.0.1',
  port: 3306,
  user: 'root',
  password: '',
  database: 'vfc',
});


/* POST user login. */
router.post('/', function(req, res) {
  const { account, password } = req.body; // 获取用户名和密码
  req.session.user = { account: req.body.account };
  // 在此处执行用户登录逻辑，验证用户名和密码等
  // 假设您从数据库中获取用户信息，以下为示例数据
  connection.query(
    'SELECT fullname,account,password, email, weight, height,gender FROM user WHERE account = ? AND password = ?',
    [account, password],
    (err, results) => {
      if (err) {
        console.error('Error fetching user data:', err);
        res.status(500).send('Error fetching user data');
        return;
      }
      
      if (results.length === 0) { // 检查是否找到用户
        res.status(404).send('User not found');
        return;
      }
      res.render('users',{ userData: results });
    }
  );
})
/* GET user profile page. */
router.get('/', (req, res) => {
  // 執行 SQL 查詢
  const account = req.session.user.account;
  connection.query(
    'SELECT * FROM user WHERE account= ?',
    [account],
    (err, results) => {
      if (err) {
        console.error('Error fetching user data:', err);
        res.status(500).send('Error fetching user data');
        return;
      } else {
        res.render('users',{ userData: results });
      }
    }
  );
});


module.exports = router;