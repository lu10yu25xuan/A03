const express = require('express');
const path = require('path');
const session = require('express-session');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const logger = require('morgan');

const app = express();
const mysql = require('mysql');
const connection = mysql.createConnection({
  host: '127.0.0.1',
  port: 3306,
  user: 'root',
  password: '',
  database: 'vfc',
});
// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// 使用内存存储的 express-session 中间件
app.use(session({
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: false
}));


app.use('/index', require('./routes/index'));
app.use('/register', require('./routes/register'));
app.use('/users', require('./routes/users'));
app.use('/exercise', require('./routes/exercise')); // 修正路由名稱

app.get('/', (req, res) => {
  res.redirect('/index');
});

// 设置服务监听localhost:3000(127.0.0.1/:3000)
app.listen('3000', function () {  
  console.log('server start on 3000 port');
});

module.exports = app;
