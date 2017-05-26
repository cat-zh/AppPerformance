#coding=utf-8

############################################################################################
# FileName:performance.py
# Author:CathyZhang
# Date:2017-5-26
# Function Description:获取app的内存、cpu数据，并生成折线图
# 注：使用dumpsys cpuinfo方法时，概率出现取不到当前app的cpu信息，故使用top命令获取cpu信息
############################################################################################

import os, time
import logging
import conf.ReadConf
import pylab as pl


logging.basicConfig(level=logging.DEBUG)

# pkgName = conf.ReadConf.read_appInfo()['appPackage']
pkgName = 'com.mcafee.security.safefamily'

path_data_file = os.getcwd() + '\\data'

file_name_mem = 'mem_info.txt'
file_name_cpu = 'cpu_info.txt'

save_to_pic_mem = 'mem_' + time.strftime('%Y%m%d%H%M%S') + '.png'
save_to_pic_cpu = 'cpu_' + time.strftime('%Y%m%d%H%M%S') + '.png'


def get_cpu(num, seconds):
    '''
    通过 adb shell top 获取cpu信息，并写入txt文件中：
    -n    刷新次数
    -d    刷新间隔时间
    '''
    global results
    print 'Start to get cpu data...'

    save_path = os.path.join(path_data_file, file_name_cpu)
    cmd = 'adb shell top -n ' + str(num) + ' -d ' + str(seconds) + ' >' + save_path
    os.popen(cmd).readlines()


def extract_cpu_data():
    cpu_list = []

    f = open(os.path.join(path_data_file, file_name_cpu), 'r')
    results = f.readlines()
    for data in results:
        if pkgName in data:
            cpu_value = data.split()[2].split('%')[0]
            cpu_list.append(cpu_value)
    f.close()
    print ('cpu_list = %s' % cpu_list)
    return cpu_list


def get_mem(num, seconds):
    '''
    通过调用get_meminfo()函数获得mem信息，并写入txt文件值：
    num: 获取次数
    seconds: 获取时间间隔
    '''
    print 'Start to get mem data...'

    i = 0
    p_list = []

    while i < num:
        p_data = get_meminfo()

        f = open(os.path.join(path_data_file, file_name_mem), 'a')
        f.write(p_data + '\n')
        f.close()

        p_list.append(p_data)
        time.sleep(seconds)
        i += 1

    print p_list
    return p_list


def get_meminfo():
    '''
    通过adb shell dumpsys meminfo 获取pss
    '''

    global mem_pss
    cmd = 'adb shell dumpsys meminfo ' + pkgName
    results = os.popen(cmd).readlines()

    for data in results:
        try:
            if 'TOTAL' in data:
                mem_pss = data.strip().split()[1]
        except Exception, e:
            print Exception, ': ', e

    print mem_pss
    return mem_pss


def generate_chart():
    '''
    根据保存的cpu、mem数据生成趋势图
    '''

    for path in os.listdir(path_data_file):
        print path
        try:
            if path.endswith('.txt'):
                draw_plot(path)
        except Exception, e:
            print Exception, ': ', e


def draw_plot(path):
    '''
    使用 pylab 库绘制折线图，并保存为png格式的图片
    '''

    f = open(os.path.join(path_data_file, path), 'r')
    mem_list = f.read().split('\n')[:-1]
    print mem_list
    f.close()

    cpu_list = extract_cpu_data()

    if 'mem' in path:
        pl.plot(mem_list, 'b')

        pl.title("Performance of MEM")
        pl.xlabel('TIME(second)')
        pl.ylabel('MEM(KB)')

        chart_path = os.path.join(path_data_file, save_to_pic_mem)
        pl.savefig(chart_path)

    elif 'cpu' in path:
        pl.plot(cpu_list, 'b')

        pl.title("Performance of CPU")
        pl.xlabel('TIME(second)')
        pl.ylabel('CPU(%)')

        chart_path = os.path.join(path_data_file, save_to_pic_cpu)
        pl.savefig(chart_path)

    else:
        print('Please check the data type...')

    pl.close()


def setupEnv():
    '''
    1. 检查存放数据文件的目录是否存在，若未存在，创建此目录
    2. 若存放的目录存在，检查文件夹中是否有遗留的历史数据，若有，删除历史数据文件
    '''
    if os.path.isdir(path_data_file):
        for data in os.listdir(path_data_file):
            if data.endswith('.txt'):
                try:
                    os.remove(os.path.join(path_data_file, data))
                except Exception, e:
                    print Exception, ': ', e
                print ('Delete File: ' + os.path.join(path_data_file, data))

    else:
        os.makedirs(path_data_file)


def wait_for_device():
    '''
    检查设备是否连接，重试10次
    '''

    device_exist = ''
    retry = 0
    while retry < 10:
        device_state = os.popen('adb get-state').readline()

        if 'device' in device_state:
            device_exist = True
            break
        else:
            device_exist = False
            os.popen('adb kill-server')
            time.sleep(2)
            os.popen('adb start-server')
            time.sleep(1)
            retry += 1

    if not device_exist:
        print u'未识别到手机，请检查手机是否连接'
        exit()
