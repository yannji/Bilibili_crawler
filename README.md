# B站爬虫
**说明：该项目为作者原创，本人大学生一枚，努力学习中，这是我的第一个项目，如有改进之处，望各位大佬指出**

### 爬取B站排行榜的相关信息及其up主信息

#### 第三库依赖：
1. requests
2. xlwt
3. pymongo

直接使用pip install -r require.txt -i https://pypi.doubanio.com/simple 安装

#### 启动程序：
使用命令行工具输入 python rank_crawler.py

#### 配置文件信息：
配置文件config.json设置了cookie信息，排行榜页面的相关链接，以及是否保存数据到MongoDB数据库等

#### 注意事项：
如果爬取不成功，大概率是设置的cookie信息失效，请更换cookie后再次尝试，更换的cookie最好是另外一个账号的，否则仍有可能不成功；
若要使用MongoDB数据库存储信息，先安装好MongoDB数据库，并启动数据库服务，在config.json文件中设置主机地址和端口号



