## description

爬取教务等信息，有新通知第一时间通过邮箱发送给自己进行提醒

## introduction

教务网、学工网、大物实验等通知在单个文件[news.py](./news.py)

需要登录教务网的如成绩和邮件通知在[main.py](./main.py)（未设置同时）

utils是登录相关组件和邮箱发送模块（news.py已单独设置，不需导入）

## Usage

项目需要将个人信息以`config.py`导入

在当前目录下修改`config.py`，形如：

```python
# 教务处登录的账号密码
username = '2022*****'  # 学号
password = '**************'  # 密码

# email config
config = {
    'from': 'send_from@example.com',  # 邮件发送方，需要开通SMTP服务
    'pwd': 'abcdefghyukj',  # 开通SMTP后给的登录秘钥
    'to': ['send_to@example.com']  # 邮件接收方，可以是自己，也可以多人
}
```
注：如果不需要登录，则不需要`ddddocr`（验证码识别）
