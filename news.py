import time
import requests
import sqlite3
import re
import threading
from datetime import datetime
from urllib import parse

import smtplib
from email.mime.text import MIMEText

from config import *


class News:
    def __init__(self, conn: sqlite3.Connection, 
                 config: dict, table: str, news_url: str,
                 re_mode: str, parser=None, 
                 headers={'User-Agent': 'Mozilla 5.0'}):
        self.config = config
        self.news_url = news_url
        self.headers = headers

        self.re_mode = re_mode
        if parser is not None:
            self.parser = parser
        else:
            self.parser = lambda x: x

        self.table = table
        self.conn = conn
        cursor = conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM sqlite_master WHERE type ="table" AND name = "{self.table}"')
        result = cursor.fetchall()
        cursor.close()
        if result[0] == (0,):  # 没有为(0,)，有为(1,)
            self.create_table(self.table)
            self.init_news()
            self.show_table()

    def create_table(self, table):
        cursor = self.conn.cursor()
        cursor.execute(f'CREATE TABLE {table} (src TEXT, title TEXT)')
        self.conn.commit()
        cursor.close()

    def init_news(self):
        cursor = self.conn.cursor()
        res = requests.get(self.news_url, headers=self.headers)
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
        res = requests.get(self.news_url, headers=self.headers)
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
            except requests.ConnectionError as e:
                print(f'【{datetime.now()}】{str(e)}')
            except requests.HTTPError as e:
                print(f'【{datetime.now()}】{str(e)}')
            except Exception as e:
                # print(e)
                self.send(f'【ERROR】{self.table}', str(e))
            finally:
                time.sleep(60)

    # 发送邮件
    @staticmethod
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

    @staticmethod
    def replace_url(res: requests.Response):
        text = res.text

        # domain = parse.urlsplit(res.url)
        # scheme = domain.scheme
        # netloc = domain.netloc

        urls = re.findall('src="(.*?)"', res.text)
        for url in set(urls):  # set避免重复url导致的问题
            t = parse.urlsplit(url)
            if not t.netloc:
                # t = parse.urlunsplit((scheme, netloc, t.path, t.query, t.fragment))
                t = parse.urljoin(res.url, url)
                text = text.replace(url, t)
            # else:
            #     t = parse.urlunsplit(t)
            # print(t)
        return text
    
    def parse_text(self, res: requests.Response):
        return self.replace_url(res)
    
    def add_copy(self, title, url) -> str:
        "return copy button html code"
        return ""

    def send(self, title, src):
        if '【ERROR】' in title:
            self.send_mail(self.config, title, src)
            return
        res = requests.get(src, headers=self.headers)

        # add copy button
        button_html = self.add_copy(title, res.url)

        if res.url.endswith('.pdf'):
            self.send_mail(self.config, title, res.url+button_html)
        else:
            res.encoding = res.apparent_encoding
            self.send_mail(self.config, title, self.parse_text(res)+button_html)

    def __del__(self):
        self.conn.close()

# 考虑到网站转发信息跳到其它部门网站，无法统一处理，最多做模糊处理，因此只留下待覆写代码，留待以后完善。
# 可考虑模糊匹配 content, article等。目前使用try进行一些处理

class JWC(News):
    # # 可以不初始化直接继承父类的__init__，不然要继承得加super()
    # def __init__(self, conn: sqlite3.Connection, config: dict, table: str, news_url: str,
    #              re_mode: str, parser=None, headers={ 'User-Agent': 'Mozilla 5.0' }):
    #     super().__init__(conn, config, table, news_url, re_mode, parser, headers)

    def parse_text(self, res: requests.Response):
        text = self.replace_url(res)
        try:
            pass
        except:
            return text

class XG(News):
    # # 可以不初始化直接继承父类的__init__，不然要继承得加super()
    # def __init__(self, conn: sqlite3.Connection, config: dict, table: str, news_url: str,
    #              re_mode: str, parser=None, headers={ 'User-Agent': 'Mozilla 5.0' }):
    #     super().__init__(conn, config, table, news_url, re_mode, parser, headers)

    def parse_text(self, res: requests.Response):
        text = self.replace_url(res)
        try:
            pass
        except:
            return text

class PEC(News):
    # # 可以不初始化直接继承父类的__init__，不然要继承得加super()
    # def __init__(self, conn: sqlite3.Connection, config: dict, table: str, news_url: str,
    #              re_mode: str, parser=None, headers={ 'User-Agent': 'Mozilla 5.0' }):
    #     super().__init__(conn, config, table, news_url, re_mode, parser, headers)

    def parse_text(self, res: requests.Response):
        text = self.replace_url(res)
        try:
            pass
        except:
            return text


if __name__ == '__main__':
    conn = sqlite3.connect('news.db', check_same_thread=False)

    jwc_parser = lambda src: src.replace('../', 'http://jwc.swjtu.edu.cn/')
    jwc = JWC(conn, config, 'jwc', 'http://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList',
               '<h3><a href="(.*?)" target="_blank">(.*?)</a></h3>', parser=jwc_parser)
    jwc.show_table()
    jwc.loop()


    # xg_parser = lambda src: src.replace('/web/Home', 'http://xg.swjtu.edu.cn/web/Home')
    # xg = XG(conn, config, 'xg', 'http://xg.swjtu.edu.cn/web/Home/PushNewsList?Lmk7LJw34Jmu=010j.shtml',
    #           '<a href="(.*?)" title="(.*?)" target="_blank"', parser=xg_parser)
    # # xg.show_table()
    # # xg.loop()


    # pec_parser = lambda src: src.replace('../', 'https://pec.swjtu.edu.cn/')
    # pec = PEC(conn, config, 'pec', 'https://pec.swjtu.edu.cn/yethan/WebAction?setAction=newsList&viewType=webdept_secondstyle&selectType=bigType&bigTypeId=75EDED8C6CAA7D73&newsType=all',
    #            '<h3><a href="(.*?)" target="_blank">(.*?)</a></h3>', parser=pec_parser)
    # # pec.show_table()
    # # pec.loop()


    # jwc_t = threading.Thread(name='jwc', target=jwc.loop)
    # xg_t = threading.Thread(name='xg', target=xg.loop)
    # pec_t = threading.Thread(name='pec', target=pec.loop)

    # threads = [jwc_t, xg_t, pec_t]
    # for thread in threads:
    #     thread.daemon = True
    #     thread.start()
    
    # # 控制程序退出，有这个就能检测Ctrl+C了
    # """
    # 多线程并不能接受到发送给主线程的Ctrl+C，而主线程结束子线程并不会解锁
    # 所以将子线程设置为守护线程，这样主线程结束守护线程也会解锁
    # 故为了让主线程可以被控制，就要加个while 循环等待接收信号
    # （注释掉下面内容程序秒停）
    # """
    # # 可能是工程上的一般写法，要关注到子线程的存活
    # while True:
    #     alive = True
    #     for thread in threads:
    #         alive = alive and thread.is_alive()
    #     if not alive:
    #         break

    # # 对该项目更简单写法
    # # while True:
    # #     pass
