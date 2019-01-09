@author: kikyoar  
@contact: nokikyoar@gmail.com  


**此脚本配置支持Zabbix3.0及以上版本**  
**python脚本支持2.7**
**监控项如下：**  
	- GP数据库总体运行状态
	- 对节点的数据同步状态进行检查
	- 对standby的数据同步状态进行检查
	- 检查数据库集群中是否有实例宕
	- 检查集群中角色实例是否正确
	- 检查执行时间超长SQL语句，此例为检查执行时间大于1小时的SQL语句
	- 查看数据库占用空间大小
	- 查看死锁表的数量
	- 查看GP连接数item







**脚本配置办法：**

- 上传脚本Zabbix_GP_Monitor.py至/home/zabbix目录下
- chmod + x Zabbix_GP_Monitor.py
- 修改并添加zabbix_agentd.conf配置文件
	
	- AllowRoot=1
	- UnsafeUserParameters=1
	- UserParameter=gp_monitor[*],python /home/zabbix/Zabbix_GP_Monitor.py $1
	- Timeout=30  
- 修改并添加zabbix_server.conf配置文件
	- Timeout=30
- 重启zabbix_agentd，zabbix_server

- 测试   
	GP服务器:  
		输入：zabbix_agentd -t gp_monitor[deadlock_number]
		返回：gp_monitor[deadlock_number]                   [t|0]
	zabbix_server:  
		输入：zabbix_get -s 192.168.6.210 -p 10050 -k "gp_monitor[deadlock_number]"
		返回：0
					
 
**Zabbix直接导入模板即可**