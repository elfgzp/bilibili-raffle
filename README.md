# bilibili-raffle
![Github](https://img.shields.io/github/license/Billyzou0741326/bilibili-live-raffle-monitor)
![Github](https://img.shields.io/badge/python-3.6%7C3.7%7C3.8-brightgreen)

## Info
 - 以<https://github.com/Dawnnnnnn/bilibili-live-tools>为启发的抽奖工具 
 - 此项目不收集任何用户数据
 - [bilibili-live-monitor-js](https://github.com/Billyzou0741326/bilibili-live-monitor-js)为此项目的server  没有服务器的话这个是无法运行的
 - 技术有限基本上没怎么测试 自家pc(Windows)和学校服务器(Linux)是没什么问题的 别的环境没测试过...


## Features
 - b站自动参加抽奖、领取舰长亲密度
```
[2019-12-01 00:05:02]    登录信息不完整 && cookies未提供. -  'bili.yaml' Skipped.
[2019-12-01 00:05:02]    [26293612]    'user0.yaml': cookies读取成功
[2019-12-01 00:05:02]    [401986779]   'user2.yaml': cookies读取成功
[2019-12-01 00:05:03]    Established connection with [ ('131.252.208.4', 8999) ]
[2019-12-01 00:05:40]    539666        @82178        小电视飞船
[2019-12-01 00:05:49]    [26293612]    539666        @82178       辣条+5
[2019-12-01 00:05:50]    [401986779]   539666        @82178       辣条+5
[2019-12-01 00:06:01]    539668        @271270       小电视图抽奖
[2019-12-01 00:06:01]    539667        @271270       小电视飞船
[2019-12-01 00:06:04]    1707610       @7493979      舰长
[2019-12-01 00:06:05]    539669        @45827        小电视飞船
[2019-12-01 00:06:07]    [26293612]    539667        @271270      辣条+5
[2019-12-01 00:06:08]    539671        @1254457      摩天大楼
[2019-12-01 00:06:09]    [26293612]    539668        @271270      辣条+5
[2019-12-01 00:06:09]    [401986779]   539668        @271270      辣条+5
[2019-12-01 00:06:11]    [26293612]    1707610       粉丝勋章亲密度+1（当前佩戴）
[2019-12-01 00:06:11]    [401986779]   1707610       粉丝勋章亲密度+1（当前佩戴）
[2019-12-01 00:06:12]    [401986779]   539667        @271270      辣条+5
[2019-12-01 00:06:13]    [401986779]   539669        @45827       辣条+5
[2019-12-01 00:06:14]    [26293612]    539669        @45827       辣条+5
[2019-12-01 00:06:15]    [401986779]   539671        @1254457     辣条+1
[2019-12-01 00:06:15]    [26293612]    539671        @1254457     辣条+1
[2019-12-01 00:06:23]    1707611       @103071       舰长
[2019-12-01 00:06:30]    [401986779]   1707611       粉丝勋章亲密度+1（当前佩戴）
[2019-12-01 00:06:32]    [26293612]    1707611       粉丝勋章亲密度+1（当前佩戴）
```  
  

## Getting Started


### Config file  

#### ``config.yaml``
    servers:                            # 每三行一组
      - address: 127.0.0.1              # 自建服务器的话用这个 连接本地localhost
        port: 8999                      # 端口 (需与服务器匹配)
        password: changethis            # 验证 (需与服务器匹配) （JS的服务器没加验证)
      - address: fab08.cecs.pdx.edu
        port: 8999
        password: changethis
      - address: fab09.cecs.pdx.edu
        port: 8999
        password: changethis
      - address: fab10.cecs.pdx.edu
        port: 8999
        password: changethis
      - address: 54.213.157.246
        port: 8999
        password: changethis
    users:
      - bili.yaml           # 默认的模板
      - user1.yaml          # 以模板为基础 写入用户信息 (文件名可以自定 但文件要切实存在)
    # - user2.yaml          # 同上 第2个号
    # - ...
    # - user-n.yaml         # 号多内存够的话想加多少个都是可以的 但是小黑屋也是很可以的
    bilibili:
      appkey: 1d8b6e7d45233436
      app_secret: 560c52ccd288fed045859ed18bffd973

#### ``bili.yaml`` (用户登录信息模板)
    user:
        username:
        password:
    web: 
        bili_jct:               # csrf_token
        DedeUserID:             # b站id
        DedeUserID__ckMd5:      # 意义不明 cookies的一部分
        sid:                    # 同上意义不明
        SESSDATA:               # 同上意义不明
    app:
        refresh_token:          # [选填] 摆设
        access_token:           # [选填] 花瓶
        expires_in:             # [选填] 酱油
        mid:                    # [选填] b站id

用户名和密码不提供也是可以的，只要web那栏的数据没错、且没过期就行  
web的5项值都取自b站的cookies，可以考虑在浏览器手动登录然后把cookies复制过来
    

### Requirements  
 - 运行环境[Python3.6+](https://www.python.org/downloads/)
 - [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
 - [pyee](https://pyee.readthedocs.io/en/latest/)
 - [websockets](https://websockets.readthedocs.io/en/stable/intro.html)
 - [colorama](https://pypi.org/project/colorama/)
 - [ruamel.yaml](https://pypi.org/project/ruamel.yaml/)

### Execution  
 1. `pip install --user -r requirements.txt`
 2. `python3 ./main_raffle.py`

## Bug report  
有问题可以来[Issue](https://github.com/Billyzou0741326/bilibili-raffle/issues)聊天  
有大问题可以炸我邮箱<zouguanhan@gmail.com>  
世界核平了可以... 嗯 去拯救一下吧  
祝各位白piao愉快

