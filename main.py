import sys
import requests
import re
import time
from datetime import datetime

import utils
from data.config import *


class User:
    def __init__(self, username, password, mail_config):
        self.ss = self.login(username, password)
        self.mail_config = mail_config
        # self.score_formal = self.score_query_formal()
        # self.score_normal = self.score_query_normal()
        # print(self.score_normal)
        # print(self.score_formal)
        # print('\n\n')

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
        res = self.ss.get('http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentScoreQuery&viewType=printScoreAll')
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
                if '未登录' in self.score_normal:
                    raise Exception('【登录过期】')
                reg = re.compile('西南交通大学 教务处<br>(.*?)</td>')
                if reg.sub('', self.score_formal) != reg.sub('', formal):
                    self.send('全部成绩记录', formal)
                    print(f'{datetime.now()} send mail')
                    self.score_formal = formal
            except Exception as e:
                # self.send('全部成绩查询报错', str(e))
                print(f'\n【全部成绩查询报错 {datetime.now()}】\n', e)

            try:
                normal = self.score_query_normal()
                if '未登录' in self.score_normal:
                    raise Exception('【登录过期】')
                if self.score_normal != normal:
                    self.send('平时成绩', normal)
                    print(f'{datetime.now()} send mail')
                    self.score_normal = normal
            except Exception as e:
                # self.send('平时成绩查询报错', str(e))
                print(f'\n【平时成绩查询报错 {datetime.now()}】\n', e)

            if '未登录' in self.score_normal or '未登录' in self.score_formal:
                # print('\n\n【登录过期】\n\n')
                self.ss = self.login(username, password)
            time.sleep(60)

    def email_check(self):
        url = 'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoAction'
        data = {
            'setAction': 'queryMyMessage',
            'viewType': 'received',
            'is_read': '0',
            'keyword': ''
        }
        res = self.ss.post(url=url, data=data)
        res.encoding = res.apparent_encoding
        # print(res.text)
        num = re.findall('共(\d+)条', res.text)[0]
        return int(num)

    def get_mail(self, sid):
        url = f'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoAction?setAction=messageInfo&viewType=reply&sid={sid}'
        res = self.ss.get(url=url)
        res.encoding = res.apparent_encoding
        return res.text.replace('..//', 'http://jwc.swjtu.edu.cn/')

    def mail_list(self, n):
        url = 'http://jwc.swjtu.edu.cn/vatuu/WebMessageInfoAction?setAction=queryMyMessage&viewType=received'
        res = self.ss.get(url=url)
        res.encoding = res.apparent_encoding
        li = re.findall('onclick="readMessage(\'(.*?)\')"', res.text)
        return li[:n]

    # def mail_loop(self):
    #     while True:
    #         try:
    #             try:
    #                 num = self.email_check()
    #             except IndexError as e:
    #                 self.send('email check error', str(e))
    #                 # print(e)
    #                 break
    #             if num:
    #                 sids = self.mail_list(num)
    #                 for sid in sids:
    #                     text = self.get_mail(sid)
    #                     self.send('教学邮箱', text)
    #                 time.sleep(60)
    #             else:
    #                 time.sleep(60)
    #         except Exception as e:
    #             print(datetime.now(), end=': ')
    #             print(e)
    #             time.sleep(60)
    def mail_loop(self):
        index_err_time = 0
        while True:
            try:
                num = self.email_check()
                if num:
                    sids = self.mail_list(num)
                    for sid in sids:
                        text = self.get_mail(sid)
                        self.send('教学邮箱', text)
                    time.sleep(60)
                else:
                    time.sleep(60)
                if index_err_time > 0:
                    index_err_time -= 1
            except IndexError as indexErr:
                self.send('email index error', str(indexErr))
                index_err_time += 1
                self.login(username, password)
                if index_err_time > 3:
                    self.send('Index Err more times, exit', '')
                    sys.exit()
            except Exception as e:
                print(datetime.now(), end=': ')
                print(e)
                time.sleep(60)

    def ocw_query(self):
        pass


if __name__ == '__main__':
    user = User(username, password, config)
    # user.run_score_query()
    user.mail_loop()
