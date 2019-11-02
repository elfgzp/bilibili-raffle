# bilibili-raffle

## Info
 - 以<https://github.com/Dawnnnnnn/bilibili-live-tools>为启发的缺陷型舰长监听服务   
 - 此项目不收集任何用户数据  
 - [bilibili-raffle-monitor](git@github.com:Billyzou0741326/bilibili-raffle-monitor.git)为此项目的server  没有服务器的话这个是无法运行的
 - 技术有限基本上没怎么测试 自家pc(Windows)和学校服务器(Linux)是没什么问题的 别的环境没测试过...


## Features
 - 领取接收自服务器的舰长/高能推送
  

## Getting Started


### Config file  

#### ``config.yaml``
    server:
      address: 0.0.0.0      # 如果服务器也在同一个设备上运行 就用localhost
      port: 8999            # 服务器端口
      password: changethis  # [选填] 需与服务器端匹配
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

