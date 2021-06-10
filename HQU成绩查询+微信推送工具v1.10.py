import time
import random
import logging
import requests
from bs4 import BeautifulSoup

# 记录日志
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S %a',
                    filename=r"./hqu-wx.log"
                    )


def login(stu_id, passwd, server_jang):
    """
    模拟登录
    """
    url_jwc = 'http://10.4.12.22/SERVER/Login.aspx'
    url_basic_info = 'http://10.4.12.22/SERVER/Student/BasicInfo.aspx'
    url_stu_mark = 'http://10.4.12.22/SERVER/Mark/StudentMark.aspx'
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Referer': 'http://10.4.12.22/SERVER/Login.aspx'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Referer': 'http://10.4.12.22/SERVER/Default.aspx'
    }

    data = {
        '__VIEWSTATE': '/wEPDwUKMTA4NDA5NzM4MmRku0RGvNK93Xxw1mnuazL3gIxESNw=',
        '__EVENTVALIDATION': '/wEWBQKo6c+LBwLPmcHwCwKvruq2CALPyszgDQLU9qXZBs0kErg7VU1+WzexjUqGv2413Hgy',
        'UserName': stu_id,
        'UserPass': passwd,
        'ButLogin': '登录'
    }

    # 登录
    s = requests.Session()
    s.get(url_jwc)
    s.post(url_jwc, data=data, headers=default_headers)

    # 获取基本信息
    # basic_data = s.get(url_basic_info, headers=headers)
    # print(basic_data.text)

    # 获取当前学期成绩
    resp = s.get(url_stu_mark, headers=headers)
    resp = resp.text

    soup = BeautifulSoup(resp, 'lxml')

    marks = soup.find('div', class_='displaynone')
    gpa = soup.find('div', id='MarkGPA')
    symbol = '|'
    mark_data = marks.text
    length = len(mark_data)
    # 根据response大小判断成绩是否更新
    with open('.cache') as f:
        cache = f.readline()
    if cache == str(length):
        logging.info("成绩未更新")
        print(time.ctime() + "：成绩未更新")
    else:
        logging.info("成绩已更新")
        print(time.ctime() + "：成绩已更新")
        with open('.cache', 'w') as f:
            f.write(str(length))
        mark_data = mark_data.split('||')
        # 以markdown形式返回到server酱
        head = '|-|-|-|-|-|-|-|-|-|'
        form = ''
        for index, item in enumerate(mark_data):
            if item is not '':
                item = item.replace('\n', '')
                item = item.replace(':', '|')
                item += symbol
                item = symbol + item
                if index == 1:
                    form += head
                    form += '\n'
                form += item
                form += '\n'
        gpa_data = gpa.text
        form += gpa_data
        get_data = {"text": "新成绩提醒.", "desp": form}
        server = requests.get(server_jang, get_data)
    return 0


if __name__ == '__main__':
    logging.info("开始程序...")
    print()
    NOTICE = """
HQU成绩查询+微信推送工具v1.10(20210610)

使用方法：
    1. 使用前请将设备连接HQU校园网
    2. 密码选项:
        ①直接运行，运行过程中输入学号、密码
        ②通过在本程序同级目录下创建config.txt文件：逐行填写学号、密码和server酱的webhook地址（看第三条）
        ③config.txt样例：
            1725131038
            password
            https://sc.ftqq.com/SCU76542Taf41211***********505e1498413ef43.send
        ④技术人员请看：新版server酱已上线，可通过企业微信推送给多人，并可以在微信接受企业微信机器人消息，只需替换webhook地址即可（替换前请注意处理推送内容中的敏感信息）
    3. server酱注册
        ①打开：http://sc.ftqq.com/
        ②页面右上方有”登入“选项，点击进入，进入后使用github账号注册
        ③扫码绑定微信后即可看到webhook地址
    4. 本程序只供HQU在校学生学习交流使用，请勿用作非法用途。因本人水平有限，如有bug且愿意交流者可联系mye_mails@126.com
    5. 其他：
        ①成绩查询随机时间1分钟~5分钟查询一次
        ②不要对他人泄露config.txt中的隐私信息
        ③图标来自：https://www.iconfont.cn/search/index?searchType=icon&q=%E5%AD%A6%E6%A0%A1
        ④该应用程序需要后台常驻（不能关闭程序界面），或联系我获取服务器版本
        ⑤推送消息包含的信息：
            学年 学期 课程名称 课程性质 学分 成绩等级 综合成绩 期末成绩 平时成绩
            ...
            绩点：5.0 排名：2
            
code by xuh, HQUCST
    """
    print(NOTICE)
    # 文件读取密码
    try:
        with open('config.txt', 'r') as f:
            stu_info = [line.strip() for line in f]
    except BaseException as identifier:
        print('请在本程序同级目录下创建config.txt文件，并按要求填写学号、密码和webhook')

    if len(stu_info):
        try:
            stu_id = stu_info[0]
            passwd = stu_info[1]
            server_jang = stu_info[2]
        except IndexError as identifier:
            print("请在config.txt配置正确的账号密码和webhook！")
    else:
        stu_id = input("请输入学号：").strip()
        passwd = input("请输入教务处密码：").strip()
        server_jang = input("请输入server酱webhook链接：").strip()

    while (True):
        try:
            login(stu_id, passwd, server_jang)
        except BaseException as identifier:
            print(identifier)
            logging.info(identifier)
            logging.info("请使用校园网，或账号密码错误！")
            print("请使用校园网，或账号密码错误！")
        # 1-5分钟查询一次
        time.sleep(random.randint(60, 300))
