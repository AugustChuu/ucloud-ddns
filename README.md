# ucloud-ddns
通过python为ucloud的域名解析api编写的ddns脚本

服务商的域名解析服务是免费的，但似乎需要将域名转入。脚本无需安装第三方sdk，主要通过python的http请求来实现。
经测试可于自己的openwrt上运行

# 使用方法
+ 安装python库 requests, re, hashlib.
+ 按照注释在脚本头部填入配置(需要注册ucloud账号).
+ 在设备上创建定时任务定期执行，如crontab：
```
crontab -e
```
添加定时命令
```
*/10 * * * * python ucloud-ddns.py
```
