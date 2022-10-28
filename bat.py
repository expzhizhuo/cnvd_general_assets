# -*- coding: utf-8 -*-
import argparse
import base64
import random
import requests
import os
import xlrd
from termcolor import cprint
import time
import warnings
import csv


requests.packages.urllib3.disable_warnings()
warnings.filterwarnings('ignore')
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'

config = {
    'email': 'zzw@jia-jiu.com',  # fofa的登录邮箱
    'key': '3dc4861675be08d0afcda5bcd352301e',  # fofa个人中心的key
    'size': '10',  # 公网资产的数量默认是10，可以根据自己的习惯进行调整，
    'base_url': 'https://fofa.info/api/v1/search/stats',  # fofa api接口地址
    'user_url': 'https://fofa.info/api/v1/info/my',  # fofa 账户信息接口
}

banned_word = ['手机免费在线观看','伦理','高清完整版','成人视频','香蕉娱乐','威尼斯']


def output(self):
    if "error" in self or "ERROR" in self:
        color = "red"
    else:
        color = "green"
    time_now = time.strftime("%Y-%m-%d %X")
    cprint(f"[{time_now}]:{self}", color)


def fofa_userinfo():
    output('开始检测fofa账户信息')
    data = {
        'email': config['email'],
        'key': config['key'],
    }
    try:
        resp = requests.get(
            url=config['user_url'], data=data, timeout=10, verify=False).json()
        output('================================================')
        output('用户名：'+resp['username'])
        output('邮箱：'+resp['email'])
        if resp['isvip'] == True:
            output('是否是VIP：是')
        else:
            output('是否是VIP：否')
        output('VIP等级：'+str(resp['vip_level']))
        output('fofa cli版本：'+str(resp['fofacli_ver']))
        output('================================================')
    except Exception as e:
        output(f'ERROR:{e}')
        exit()


def xls_read_file(file_name):
    # 读取xls文件的每一行数据
    workbook = xlrd.open_workbook(file_name)
    worksheet = workbook.sheet_by_index(0)
    nrows = worksheet.nrows  # 每一行遍历数据
    for i in range(3, nrows):
        # 循环每一行数据
        data = worksheet.row_values(i)
        # 取出来第一列的数据（公司名字）
        output(f"公司名字：{data[0]}")
        fofa_search(f'body="{data_format(data[0])}" && country="CN"')


def data_format(data):
    return data.replace('有限公司', '').replace('技术', '').replace('股份', '').replace(')', '').replace('(', '')


def fofa_search(self):
    global List
    output('FOFA查询语句为：{}'.format(self))
    base_fofa_search = base64.b64encode(self.encode('utf8'))
    data = {
        'email': config['email'],
        'key': config['key'],
        'fields': 'title',
        'qbase64': base_fofa_search,
        # 'size': config['size'],
    }
    time.sleep(random.randint(5, 10))
    res = requests.get(str(config['base_url']), data, timeout=60)
    res.encoding = res.apparent_encoding
    resp = res.json()
    print(resp)
    output('FOFA语句：{} 公网资产独立ip有{}个'.format(self, resp['distinct']['ip']))
    try:
        if resp['error'] == False:
            if int(resp['distinct']['ip']) > 0:
                for i in range(len(resp['aggs']['title'])):
                    count = resp['aggs']['title'][i]['count']
                    if count > int(config['size']):
                        name = resp['aggs']['title'][i]['name'].replace("\n","").replace("\r","").replace("\t","").replace(" ","")
                        print(name)
                        if name not in banned_word:
                            # 只保存公网独立ip资产大于10的fofa语句和站点标题以及公网的资产数量
                            with open('result.txt', 'a+', encoding='utf-8') as fa:
                                fa.write('FOFA查询语句为：{}'.format(self))
                                fa.write('\n')
                                fa.write(f"网站标题：{name}")
                                fa.write('\n')
                                fa.write('公网资产数量为：{}'.format(count))
                                fa.write('\n\n')
                            str_list = []
                            str_list.append(self)
                            str_list.append(name)
                            str_list.append(count)
                            try:
                                with open("result.csv", "a", newline='') as csvfile:
                                    writer = csv.writer(csvfile)
                                    # 写入多行用writerows
                                    # writer.writerows(data_array)
                                    # 写入单行用 writerow
                                    writer.writerow(str_list)
                                    # 执行添加数据操作之后，要写close关闭，否则下次无法再次插入新的数据
                                    csvfile.close()
                            except Exception as e:
                                output(f"ERROR：{e}")
                                pass
                        else:
                            pass
                    else:
                        pass
            else:
                pass
        else:
            output(f"ERROR：{resp}")
    except Exception as e:
        output(f"ERROR：{e}")
        pass


# 数据写入函数
def write_list():
    path = 'result.csv'
    header = ['FOFA语句', '网站标题', '公网资产数量为']
    with open(path, 'w', newline='') as fp:
        # 写
        writer = csv.writer(fp)
        # 设置第一行标题头
        writer.writerow(header)


def main():
    output("Strating....")
    output_search = open('./result.txt', 'a+', encoding='utf-8')
    output_search.truncate(0)  # 对文件进行初始化操作
    output_search.close()
    write_list()
    parser = argparse.ArgumentParser(
        description='''
        \n 根据公司名字搜索通用资产基于FOFA API --By zhizhuo \n
        \n 由于FOFA会员等级限制，普通会员最多100条，高级会员做多10000条 \n
        \n 程序默认下载api可获取最大数量 \n
        ''')
    parser.add_argument('-f', '-file', dest="file",
                        help='以xls文件，默认爱企查导出就是xls格式的文件', required=True)
    file_name = parser.parse_args().file
    if file_name:
        fofa_userinfo()
        xls_read_file(file_name)
    else:
        output(f'ERROR：请使用-f参数指定爱企查导出的文件')


if __name__ == '__main__':
    main()
