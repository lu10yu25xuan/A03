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

router.get('/', (req, res) => {
  res.render('index', { error: null }); // Ensure error is initialized to null
});

router.post('/', (req, res) => {
  const account = req.body.account;
  const password = req.body.password;

  // Check if the user exists in the database
  connection.query(
    'SELECT * FROM user WHERE account = ? AND password = ?',
    [account, password],
    (err, results) => {
      if (err) {
        console.error('Error querying user:', err);
        res.status(500).send('Error querying user');
      } else {
        if (results.length > 0) {
          // User exists, you can set a session or redirect as needed
          req.session.user = { account: users.account }; // 將用戶存儲在會話中
          res.redirect('/users'); // Redirect to dashboard or another page
        } else {
          // User does not exist or incorrect credentials
          res.render('index', { error: 'Invalid student_id or password' });
        }
      }
    }
  );
});

module.exports = router;
