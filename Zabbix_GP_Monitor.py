#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

@author: kikyoar
@contact: nokikyoar@gmail.com
@time: 2018/12/11 14:57

"""
"""
- CPU\IO\内存

- 任务调度监控

- 

此脚本务必放入GP_Master所在服务器上
0说明正常，1说明有问题
"""

import sys
import os
import subprocess
import textwrap
import string
import re

# GP 数据库整体检查
"""
若无输出，说明GP数据库总体运行状态正常无错误。同时可以用gpstate命令来查看GP数据库具体的状态信息
"""


def gp_status():
    commands = os.popen('su - gpadmin -c "gpstate | grep -i error"', 'r')
    if 'error' in [command.lower() for command in commands]:
        print(1)
    else:
        print(0)


# GP 对节点的数据同步状态进行检查
"""
若无输出，说明同步已完成，状态正常
"""


def synchronizing_data():
    commands = os.popen('su - gpadmin -c "gpstate -m | grep -i synchronizing"')
    # 判断commands是否有值
    if any(commands) == True:
        print(1)
    else:
        print(0)


# GP 对standby的数据同步状态进行检查
"""
若无输出，说明同步已完成，状态正常
"""


def standby_data():
    commands = os.popen('su - gpadmin -c "gpstate -f | grep -i synchronizing"')
    if any(commands) == True:
        print(1)
    else:
        print(0)


# GP 检查数据库集群中是否有实例宕，若无输出说明没有实例宕

def instance_Downtime():
    # 使用shell执行sql命令
    commands = subprocess.Popen(textwrap.dedent("""\
        #!/bin/bash
        su - gpadmin -c "psql -d postgres"<<EOF
        select * from gp_segment_configuration where status='d' or mode<>'s';
        \q
        EOF
        """), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    str_commands = commands.communicate()  # 元组
    str_command = "0 rows"
    # 判断str_command 是否是str_commands[0]中的字符串
    if string.find(str_commands[0], str_command) != -1:
        print(0)
    else:
        print(1)


# 检查集群中角色实例是否正确，若无输出说明角色实例均正确

def instance_role():
    # 使用shell执行sql命令
    commands = subprocess.Popen(textwrap.dedent("""\
        #!/bin/bash
        su - gpadmin -c "psql -d postgres"<<EOF
        select * from gp_segment_configuration where preferred_role<>role;
        \q
        EOF
        """), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    str_commands = commands.communicate()  # 元组
    str_command = "0 rows"
    # 判断str_command 是否是str_commands[0]中的字符串
    if string.find(str_commands[0], str_command) != -1:
        print(0)
    else:
        print(1)


# 检查执行时间超长SQL语句，此例为检查执行时间大于1小时的SQL语句，若无输出说明没有执行时间大于1小时的SQL语句

def longtime_sql():
    # 使用shell执行sql命令
    commands = subprocess.Popen(textwrap.dedent("""\
        #!/bin/bash
        su - gpadmin -c "psql -d postgres"<<EOF
        select * from pg_stat_activity where now()-query_start>'01:00:00' and current_query <> '<IDLE>';
        \q
        EOF
        """), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    str_commands = commands.communicate()  # 元组
    str_command = "0 rows"
    # 判断str_command 是否是str_commands[0]中的字符串
    if string.find(str_commands[0], str_command) != -1:
        print(0)
    else:
        print(1)


# 查看sqmmt数据库占用空间大小


def sqmmt_size():
    # 使用shell执行sql命令
    # select pg_size_pretty(pg_database_size('sqmmt')); 其中数据库自行更换
    os.system("touch /tmp/GP_databasesize.txt|chmod 777 /tmp/GP_databasesize.txt")

    str_pg_size = open("/tmp/GP_databasesize.txt", "r")
    pg_size = re.findall(r'\d*', str_pg_size.read())
    # 单位是GP
    print(pg_size[0])
    str_pg_size.close()

    subprocess.Popen("""su - gpadmin -c "psql -d postgres"<<EOF
    COPY(select pg_size_pretty(pg_database_size('sqmmt'))) to '/tmp/GP_databasesize.txt' 
    \q
    EOF
    """, shell=True, stdout=subprocess.PIPE)


#    str_commands = commands.communicate()  # 元组
#    str_command = str_commands[0]
#    正则表达式匹配，提取sqmmt数据库的大小
#    pg_size = re.findall(r'\d*\sGB', str_command)

#    print(pg_size)


# 查看死锁表的数量

def deadlock_number():
    # 使用shell执行sql命令
    commands = subprocess.Popen(textwrap.dedent("""\
        #!/bin/bash
        su - gpadmin -c "psql -d postgres"<<EOF
        select locktype, database, c.relname, l.relation, l.transactionid, l.transaction, l.pid, l.mode, l.granted, 
        a.current_query from pg_locks l, pg_class c, pg_stat_activity a
        where l.relation=c.oid and l.pid=a.procpid and a. waiting_reason ='lock'
        order by c.relname;
        \q
        EOF
        """), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    str_commands = commands.communicate()  # 元组
    str_command = "0 rows"
    # 判断str_command 是否是str_commands[0]中的字符串
    if string.find(str_commands[0], str_command) != -1:
        print(0)
    else:
        print(1)


# 查看GP连接数item

def item_number():
    commands = subprocess.Popen(textwrap.dedent("""\
        #!/bin/bash
        su - gpadmin -c "psql -d postgres"<<EOF
        select count(*) from pg_stat_activity;
        \q
        EOF
        """), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    str_commands = commands.communicate()  # 元组
    str_command = str(str_commands)  # 转换为字符串
    str_split = str_command.split()[3]  # 截取拆分字符串
    itemnumber = re.findall(r'\d+', str_split)  # 匹配正则后的数字列表
    print(itemnumber[0])


if sys.argv[1] == "gp_status":
    gp_status()
elif sys.argv[1] == "synchronizing_data":
    synchronizing_data()
elif sys.argv[1] == "standby_data":
    standby_data()
elif sys.argv[1] == "instance_Downtime":
    instance_Downtime()
elif sys.argv[1] == "instance_role":
    instance_role()
elif sys.argv[1] == "longtime_sql":
    longtime_sql()
elif sys.argv[1] == "sqmmt_size":
    sqmmt_size()
elif sys.argv[1] == "deadlock_number":
    deadlock_number()
elif sys.argv[1] == "item_number":
    item_number()
