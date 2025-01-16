const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(cors());

let verificationCode = null;
let registeredUsers = [];

// إعداد Nodemailer باستخدام SMTP (Gmail في هذا المثال)
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'your-email@gmail.com',  // ضع بريدك الإلكتروني هنا
    pass: 'your-email-password'    // ضع كلمة المرور هنا
  }
});

// إرسال رمز التحقق إلى البريد الإلكتروني
app.post('/send-code', (req, res) => {
  const { username, email, password } = req.body;
  verificationCode = Math.floor(100000 + Math.random() * 900000);
  registeredUsers.push({ username, email, password });

  const mailOptions = {
    from: 'your-email@gmail.com',
    to: email,
    subject: 'رمز التحقق',
    text: `رمز التحقق الخاص بك هو: ${verificationCode}`
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.error(error);
      res.status(500).send('فشل في إرسال البريد الإلكتروني');
    } else {
      res.status(200).send('تم إرسال رمز التحقق');
    }
  });
});

// التحقق من الرمز
app.post('/verify-code', (req, res) => {
  const { code } = req.body;
  if (parseInt(code) === verificationCode) {
    res.status(200).send('تم التحقق بنجاح');
  } else {
    res.status(400).send('رمز التحقق غير صحيح');
  }
});

// تسجيل الدخول
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = registeredUsers.find(u => u.email === email && u.password === password);
  if (user) {
    res.status(200).send('تم تسجيل الدخول بنجاح');
  } else {
    res.status(400).send('بيانات الدخول غير صحيحة');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});