const express = require('express');
const router = express.Router();
const mysql = require('mysql');

// Database connection setup
const connection = mysql.createConnection({
  host: '127.0.0.1',
  port: 3306,
  user: 'root',
  password: '',
  database: 'vfc',
});

// GET 請求處理，用於渲染註冊頁面
router.get('/', (req, res) => {
  res.render('index'); 
});

// POST 請求處理，用於處理註冊邏輯和插入數據庫
router.post('/', (req, res) => {
  // 從 POST 請求中獲取用戶輸入的資訊
  const fullname = req.body.fullname;
  const account = req.body.account;
  const password = req.body.password;
  const weight = req.body.weight;
  const email = req.body.email;
  const gender = req.body.gender;
  const height = req.body.height;

  // 使用 MySQL 的 SELECT 操作檢查用戶名是否已存在
  connection.query(
    'SELECT * FROM user WHERE account = ?',
    [account],
    (selectErr, selectResults) => {
      if (selectErr) {
        // 處理查詢過程中的錯誤
        console.error('Error checking account:', selectErr);
        res.status(500).send('Error checking account');
      } else {
        // 檢查結果
        if (selectResults.length > 0) {
          // 用戶名已存在，返回錯誤給前端
          res.render('index', { error: 'account already exists' });
        } else {
          // 用戶名不存在，可以進行註冊
          // 使用 MySQL 的 INSERT 操作將用戶資訊插入數據庫
          // 使用 MySQL 的 INSERT 操作將用戶資訊插入數據庫
      connection.query(
        'INSERT INTO user (fullname, account, password, email, weight, height, gender) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [fullname, account, password, email, weight, height, gender],
        (insertErr, insertResults) => {
        if (insertErr) {
          // 處理插入過程中的錯誤
          console.error('Error inserting user:', insertErr);
          res.status(500).send('Error inserting user');
        } else {
          // 插入成功
          console.log('User inserted successfully:', insertResults);
          res.redirect('/index'); // 重定向到首頁或其他適當的頁面
          }
        }
      );

        }
      }
    }
  );
});


// 將 router 對象暴露給其他文件（例如 app.js）
module.exports = router;
