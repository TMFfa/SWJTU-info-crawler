import sys
import requests
import re
import time
from datetime import datetime

import utils
from config import *


class User:
    def __init__(self, username, password, mail_config):
        self.ss = self.login(username, password)
        self.mail_config = mail_config
        self.score_formal = self.score_query_formal()
        self.score_normal = self.score_query_normal()
        print(self.score_normal)
        print(self.score_formal)
        print('\n\n')

    @staticmethod
    def login(username, password) -> requests.Session:
        while True:
            try:
                ss = utils.login(username, password)
                return ss
            except ValueError as msg:
                print(f'【{datetime.now()}】')
                print(msg)
            except Exception as e:
                print(f'*******************\n意外报错： {datetime.now()}\n', e)
                sys.exit()

    def send(self, subject, text):
        utils.send(self.mail_config, subject, text)

    def score_query_formal(self):
        res = self.ss.get("http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentScoreQuery&viewType=studentScore&orderType=submitDate&orderValue=desc")
        res.encoding = res.apparent_encoding
        return res.text

    def score_query_normal(self):
        res = self.ss.get('http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentNormalMark')
        res.encoding = res.apparent_encoding
        return res.text

    def run_score_query(self):
        while True:
            try:
                formal = self.score_query_formal()
                if '未登录' in formal or "未登陆" in formal:
                    raise ZeroDivisionError('【登录过期】')
                reg = re.compile('西南交通大学 教务处<br>(.*?)</td>')
                if reg.sub('', self.score_formal) != reg.sub('', formal):
                    self.send('全部成绩记录', formal)
                    print(f'{datetime.now()} send mail')
                    self.score_formal = formal
            except ZeroDivisionError:
                print("\n\n【登录过期】 {datetime.now()}】\n")
            except Exception as e:
                # self.send('全部成绩查询报错', str(e))
                print(f'\n【全部成绩查询报错 {datetime.now()}】\n', e)

            try:
                normal = self.score_query_normal()
                if "未登录" in normal or "未登陆" in normal:
                    raise Exception('【登录过期】')
                if self.score_normal != normal:
                    self.send('平时成绩', normal)
                    print(f'{datetime.now()} send mail')
                    self.score_normal = normal
            except ZeroDivisionError:
                print("\n\n【登录过期】 {datetime.now()}】\n")
            except Exception as e:
                # self.send('平时成绩查询报错', str(e))
                print(f'\n【平时成绩查询报错 {datetime.now()}】\n', e)

            if '未登录' in self.score_normal or '未登录' in self.score_formal or "未登陆" in self.score_formal or "未登陆" in self.score_normal:
                # print('\n\n【登录过期】\n\n')
                self.ss = self.login(username, password)
            time.sleep(60)

    def email_check(self):
        url = f'http://jwc.swjtu.edu.cn/vatuu/AjaxXML?selectType=UserMessageNum&ts={int(time.time()*100)}'
        res = self.ss.get(url=url)
        res.encoding = res.apparent_encoding
        # print(res.text)
        num = re.findall('<messageNum>(\d+)</messageNum>', res.text)[0]
        return int(num)

    def get_mail(self, sid):
        url = f'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoAction?setAction=messageInfo&viewType=reply&sid={sid}'
        res = self.ss.get(url=url)
        res.encoding = res.apparent_encoding
        html = res.text.replace('..//', 'http://jwc.swjtu.edu.cn/')
        html = html.replace('<span class="c-blue">温馨提示</span>.', '')
        html = html.replace('若使用单个工号或学号：（收件人输入框的值为精确查找值）输入完之后<span', '')
        html = html.replace('class="c-blue">按Enter键查询</span>&nbsp;&nbsp;&nbsp;&nbsp;输入的值必须<span', '')
        html = html.replace('class="c-red">完整且正确</span>否则查询不到输入的值对应的用户基本信息', '')
        return html

    def mail_list(self, n):
        url = 'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoAction'
        data = {'setAction': 'queryMyMessage',
                'viewType': 'received',
                'is_read': 0,
                'keyword': ''}
        res = self.ss.post(url=url, data=data)
        res.encoding = res.apparent_encoding
        li = re.findall('onclick="readMessage\(\'(.*?)\'\)"', res.text)
        return li[:n]

    def read_mail(self, sid):
        # 邮件需要主动发送请求才能设置为已读
        url = 'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoSetAction?setAction=setStatus&sid=' + sid
        data = {
            'setAction': 'setStatus',
            'sid': sid
        }
        return self.ss.post(url=url, data=data).text

    def mail_loop(self):
        index_err_time = 0
        while True:
            try:
                num = self.email_check()
                if num:
                    sids = self.mail_list(num)
                    for sid in sids:
                        print(f'【{datetime.now()}】 sid: {sid}')
                        text = self.get_mail(sid)
                        self.send('教学邮箱', text)
                        self.read_mail(sid)
                    time.sleep(60)
                else:
                    time.sleep(60)
                if index_err_time > 0:
                    index_err_time -= 1
            except IndexError as indexErr:
                # self.send('email index error', str(indexErr))
                index_err_time += 1
                if index_err_time > 3:
                    self.send('Index Err more times, exit', '')
                    sys.exit()
                print(f"【{datetime.now()}】 重新登陆...")
                self.ss = self.login(username, password)
            except Exception as e:
                print(datetime.now(), end=': ')
                print(e)
                time.sleep(60)


if __name__ == '__main__':
    user = User(username, password, config)
    # user.run_score_query()
    user.mail_loop()
