const express = require('express');
const { exec } = require('child_process');
const session = require('express-session');
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
  res.render('exercise');
});

router.post('/', (req, res) => {
  const account = req.session.user.account;
  const exerciseType = req.body.exerciseType;
  if (exerciseType === '深蹲') {
    exec(`python squat.py ${account} ${exerciseType}`, (error, stdout, stderr) => {
      if (error) {
        console.error(`exec error: ${error}`);
        return res.status(500).send('Error executing Python script');
      }
      console.log(`stdout: ${stdout}`);
      console.error(`stderr: ${stderr}`);
      res.render('exercise');
    });
  } else {
    res.send('Not a squat exercise');
  }
});

router.get('/login', (req, res) => {
  const account = req.body.account;
  req.session.user = { account: req.body.account };
  connection.query(
    'SELECT * FROM user WHERE account = ?',
    [account],
    (err, results) => {
      if (err) {
        console.error('Database query error:', err);
        return res.status(500).send('Database query error');
      }
      res.render('exercise');
    }
  );
});

module.exports = router;
