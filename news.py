import time
import requests
import sqlite3
import re
import threading

import smtplib
from email.mime.text import MIMEText

from config import *

headers = {
    'User-Agent': 'Mozilla 5.0'
}


# 发送邮件
def send_mail(config, subject, text):
    # 构建邮件
    msg = MIMEText(text, 'html', 'utf-8')
    msg['From'] = config['from']
    msg['To'] = ','.join(config['to'])
    msg['Subject'] = subject

    # 发送邮件
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as smtp:
        smtp.login(config['from'], config['pwd'])
        smtp.send_message(msg)
        # smtp.sendmail(mail, to, msg.as_string())  # 一样的，但明显上面更简单


class News:
    def __init__(self, conn: sqlite3.Connection, config: dict, table: str, news_url: str, re_mode: str, parser=None):
        self.config = config
        self.news_url = news_url
        self.re_mode = re_mode
        if parser is not None:
            self.parser = parser
        else:
            self.parser = lambda x: x
        self.table = table
        self.conn = conn
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM sqlite_master WHERE type ="table" AND name = "{table}"')
        result = cursor.fetchall()
        cursor.close()
        if result[0] == (0,):  # 没有为(0,)，有为(1,)
            self.create_table(table)
            self.init_news()
            self.show_table()

    def create_table(self, table):
        cursor = self.conn.cursor()
        cursor.execute(f'CREATE TABLE {table} (src TEXT, title TEXT)')
        self.conn.commit()
        cursor.close()

    def init_news(self):
        cursor = self.conn.cursor()
        res = requests.get(self.news_url, headers=headers)
        res.encoding = res.apparent_encoding
        news = re.findall(self.re_mode, res.text)
        for src, title in news:
            src = self.parser(src)
            cursor.execute(f'INSERT INTO {self.table} VALUES ("{src}", "{title}")')
        self.conn.commit()
        cursor.close()

    def show_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.table}')
        for i in cursor.fetchall():
            print(i)

    def check(self):
        cursor = self.conn.cursor()
        res = requests.get(self.news_url, headers=headers)
        res.encoding = res.apparent_encoding
        news = re.findall(self.re_mode, res.text)
        for src, title in news:
            src = self.parser(src)
            cursor.execute(f'SELECT * FROM {self.table} WHERE src="{src}"')
            if len(cursor.fetchall()):
                break
            else:
                cursor.execute(f'INSERT INTO {self.table} VALUES ("{src}", "{title}")')
                self.conn.commit()
                self.send(f'【{self.table}】{title}', src)
        cursor.close()

    def loop(self):
        while True:
            try:
                self.check()
            except Exception as e:
                print(e)
                self.send(f'【ERROR】{self.table}', str(e))
            finally:
                time.sleep(60)

    def send(self, title, src):
        if '【ERROR】' in title:
            send_mail(self.config, title, src)
            return
        res = requests.get(src, headers=headers)
        res.encoding = res.apparent_encoding
        send_mail(self.config, title, res.text)

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    conn = sqlite3.connect('news.db', check_same_thread=False)

    jwc_parser = lambda src: src.replace('../', 'http://jwc.swjtu.edu.cn/')
    jwc = News(conn, config, 'jwc', 'http://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList',
               '<h3><a href="(.*?)" target="_blank">(.*?)</a></h3>', parser=jwc_parser)
    # jwc.show_table()
    # jwc.loop()


    xg_parser = lambda src: src.replace('/web/Home', 'http://xg.swjtu.edu.cn/web/Home')
    xg = News(conn, config, 'xg', 'http://xg.swjtu.edu.cn/web/Home/PushNewsList?Lmk7LJw34Jmu=010j.shtml',
              '<a href="(.*?)" title="(.*?)" target="_blank"', parser=xg_parser)
    # xg.show_table()
    # xg.loop()


    pec_parser = lambda src: src.replace('../', 'https://pec.swjtu.edu.cn/')
    pec = News(conn, config, 'pec', 'https://pec.swjtu.edu.cn/yethan/WebAction?setAction=newsList&viewType=webdept_secondstyle&selectType=bigType&bigTypeId=75EDED8C6CAA7D73&newsType=all',
               '<h3><a href="(.*?)" target="_blank">(.*?)</a></h3>', parser=pec_parser)
    # pec.show_table()
    # pec.loop()


    jwc_t = threading.Thread(name='jwc', target=jwc.loop)
    xg_t = threading.Thread(name='xg', target=xg.loop)
    pec_t = threading.Thread(name='pec', target=pec.loop)

    threads = [jwc_t, xg_t, pec_t]
    for thread in threads:
        thread.daemon = True
        thread.start()
    
    # 控制程序退出，有这个就能检测Ctrl+C了
    """
    多线程并不能接受到发送给主线程的Ctrl+C，而主线程结束子线程并不会解锁
    所以将子线程设置为守护线程，这样主线程结束守护线程也会解锁
    故为了让主线程可以被控制，就要加个while 循环等待接收信号
    （注释掉下面内容程序秒停）
    """
    # 可能是工程上的一般写法，要关注到子线程的存活
    while True:
        alive = True
        for thread in threads:
            alive = alive and thread.is_alive()
        if not alive:
            break

    # 对该项目更简单写法
    # while True:
    #     pass
