# -*- coding: utf-8 -*-
from flask import render_template, Blueprint, session, request, jsonify, redirect
import time
import requests
import re
from bs4 import BeautifulSoup
import json
import collections
wxchart = Blueprint('v1', __name__)


@wxchart.route('')
def login():
    ctime = time.time() * 1000  # 模拟一个相同的时间戳
    base_url = 'https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}'
    url = base_url.format(ctime)  # 字符串拼接，生成新的url
    response = requests.get(url)  # 向新的url发送get请求
    xcode_list = re.findall('window.QRLogin.uuid = "(.*)";',
                            response.text)  # 通过正则表达式，提取到对于的参数列表['YZzTdz9m_A==', 'YZzTdz9m_A==']
    session['xcode'] = xcode_list[0]  # 获取到参数，存入session内
    return render_template('index.html', xcode=xcode_list[0])  # 返回给login页面此参数


@wxchart.route('/check_login')
def check_login():
    tip = request.args.get('tip')  # 标记是否扫码
    # 自定义返回的json数据格式
    ret = {
        'code': 408,  # 初始值408代表没有任何操作
        'data': None
    }
    ctime = time.time() * 1000  # 根据得到的url，伪造匹配的时间戳
    base_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip={1}&r=903313058&_={2}'
    url1 = base_url.format(session['xcode'], tip, ctime)  # 字符串修饰
    r1 = requests.get(url1)  # 获取响应
    if 'window.code=201' in r1.text:
        # 有人扫码
        v = re.findall("window.userAvatar = '(.*)';", r1.text)
        avatar = v[0]
        ret['code'] = 201  # 状态码，代表有人扫码了
        ret['data'] = avatar  # 用户头像
    elif 'window.code=200;' in r1.text:
        # 扫码之后，点击确定登录
        session['login_cookie'] = r1.cookies.get_dict()  # 获取确认登陆的cookie
        uri = re.findall('window.redirect_uri="(.*)";', r1.text)  # 之前的图片，已经发现这里是一个重定向路由，所以获取重定向的路由
        # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AfpJ_ZmEJGcJ8iU62SiPyuTo@qrticket_0&uuid=gZHgYImvDQ==&lang=zh_CN&scan=1532410951
        redirect_url = '{0}&fun=new&version=v2'.format(uri[0])  # 字符串拼接，形成新的url
        # 获取凭证
        r2 = requests.get(redirect_url)  # 网页重定向的时候，会返回凭证用来进行之后的验证
        ticket_dict = {}
        soup = BeautifulSoup(r2.text, 'html.parser')  # 标签文本实例化bs对象
        for item in soup.find(name='error').children:  # 找到需要的凭证
            ticket_dict[item.name] = item.text  # 凭证存入字典
        session['ticket_dict'] = ticket_dict  # 凭证存入session
        session['ticket_cookie'] = r2.cookies.get_dict()  # session中存入获取重定向的cookie
        ret['code'] = 200  # 200表示确定登陆了
        session['is_login'] = True  # 给后面的url判断是否登陆
    return jsonify(ret)  # Json序列化返回


@wxchart.route('/index')
def index():
    # 判断是否已经登陆
    if not session.get('is_login'):
        return redirect('/wechat/login')
    # 发送post请求，根据ticket_dict进行构造数据
    # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=892259194&pass_ticket=TS7TEfumVaVzKhn%252FrnLKS2zZyhixJDEYxlXqGgQVplQ%253D
    base_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=892259194&pass_ticket={0}'
    url = base_url.format(session['ticket_dict']['pass_ticket'])
    # BaseRequest
    # :
    # {Uin: "184513440", Sid: "U4WojQwDRwKqdeMs", Skey: "", DeviceID: "e409571391728320"}  # 伪造的数据格式样板

    form_data = {  # 伪造数据
        'BaseRequest': {
            'DeviceID': "e409571391728320",
            'Sid': session['ticket_dict']['wxsid'],
            'Skey': session['ticket_dict']['skey'],
            'Uin': session['ticket_dict']['wxuin']
        }
    }
    r1 = requests.post(
        url=url,
        json=form_data
    )
    r1.encoding = r1.apparent_encoding  # 使用默认编码原则
    user_info = json.loads(r1.content)
    for key in user_info:
        print(key)
    session['current_user_info'] = user_info['User']
    return render_template('index1.html', user_info = user_info)


@wxchart.route('/contact_all')
def contact_all():
    # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket=z%252BTVxEioLl3A5arKy%252BUMHbeTME%252BmAkJEulNYIYgGcpw%253D&r=1532421128264&seq=0&skey=@crypt_41bed7c6_e213390395ab3a4ef54bfef5d004f719
    base_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?pass_ticket={0}&r={1}&seq=0&skey={2}'
    url = base_url.format(
        session['ticket_dict']['pass_ticket'],
        time.time() * 1000,
        session['ticket_dict']['skey'],
    )  # url拼接
    all_cookies = {}
    all_cookies.update(session['login_cookie'])
    all_cookies.update(session['ticket_cookie'])  # 带入所有的cookies

    r1 = requests.get(url, cookies=all_cookies)
    r1.encoding = r1.apparent_encoding
    contact_dict = json.loads(r1.content)

    # 获取联系人过滤公众号
    remark_name_list = [item['RemarkName'] for item in contact_dict['MemberList'] if item['RemarkName']]
    # 获取地区列表
    area_list = [item['Province'] for item in contact_dict['MemberList'] if item['RemarkName'] and item['Province']]
    area_dict = collections.Counter(area_list)
    area_data1 = [i for i in area_dict.keys()]
    area_data2 = [i for i in area_dict.values()]
    # 个性签名列表
    signature_dict = {item['RemarkName']: item['Signature'] for item in contact_dict['MemberList'] if item['RemarkName'] and item['Signature']}

    return jsonify({"remark_name_list": remark_name_list
                    ,"area_data1": area_data1
                    ,"area_data2": area_data2
                    ,"signature_list": signature_dict})


@wxchart.route('/send_msg')
def send_msg():
    recv = request.args.get('recv')
    content = request.args.get('content')
    # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?pass_ticket=wtwzy%252F7fxQgJaTA511weqPXIkIGSJmZdCRATgZdIfYY%253D
    base_url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?pass_ticket={0}'
    url = base_url.format(session['ticket_dict']['pass_ticket'])
    ctime = time.time() * 1000
    form_data = {  # 伪造数据格式
        'BaseRequest': {
            'DeviceID': "e939509344931677",
            'Sid': session['ticket_dict']['wxsid'],
            'Skey': session['ticket_dict']['skey'],
            'Uin': session['ticket_dict']['wxuin']
        },
        'Msg': {
            'ClientMsgId': ctime,
            'Content': content,
            'FromUserName': session['current_user_info']['UserName'],
            'LocalID': ctime,
            'ToUserName': recv,
            'Type': 1,  # 文本
        },
        'Scene': 0
    }
    all_cookies = {}
    all_cookies.update(session['login_cookie'])
    all_cookies.update(session['ticket_cookie'])  # 带入cookie，试验过证明是需要的
    r1 = requests.post(
        url=url,
        data=bytes(json.dumps(form_data, ensure_ascii=False), encoding='utf-8'),
        cookies=all_cookies,
        headers={
            'Content-Type': 'application/json'  # 这句话用来表示，需要序列化成json数据；也可以去掉data跟headers直接用json=form_data来实现
        }
    )
    print(r1.text)
    return '.....'