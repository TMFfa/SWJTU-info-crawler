## description

爬取教务等信息，有新通知第一时间通过邮箱发送给自己进行提醒

## introduction

教务网、学工网、大物实验等通知在单个文件[news.py](./news.py)

需要登录教务网的如成绩和邮件通知在[main.py](./main.py)（未设置同时）

utils是登录相关组件和邮箱发送模块（news.py已单独设置，不需导入）

## Usage

项目需要将个人信息以`config.py`导入

在`data`目录下修改`config.py`，形如：

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

### Dockerfile使用

修改好`config.py`后，

使用`docker build -t news-reminder .`来构建docker镜像，

使用`docker run -d --restart=always -v ~/your/path/SWJTU-news-reminder/data:/app/data --name news news-reminder`运行

​	-d表示后台运行

​	--restart=always表示自动重启（开机、出错容器退出等情况）

   -v 表示将本地路径映射到容器内路径，实现配置信息的替换，注意**必须为绝对路径**，因为相对路径是相对于docker容器管理那边的路径的，且这里是不允许有`./`之类的(可以有~来表示家目录)

   --name 后面是用于管理容器的别名

   镜像名一定要放最后

若要停止，运行`docker stop news`

或`docker ps -a` 查看运行中的容器id，使用`docker stop ID前3位`来停止，

再使用`docker rm ID前3位`删除容器（容器是镜像的实例，不会删除镜像）

若要删除镜像，使用`docker images`查看镜像ID，`docker rmi ID前3位`删除镜像

## 使用微信发送通知————news-wechat.py
使用微信必须先开启微信服务，详见项目：https://github.com/faf4r/cli-wechat
开启微信后就可以使用微信接口发送消息，发送通知改为运行`news-wechat.py`
