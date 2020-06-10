# B站爬虫
**说明：该项目为作者原创，本人大学生一枚，努力学习中，这是我的第一个项目，如有改进之处，望各位大佬指出**

### 爬取B站排行榜的相关信息及其up主信息

#### 第三库依赖：
1. ##### requests
2. ##### xlwt
3. ##### pymongo

##### 直接使用pip install -r require.txt -i https://pypi.doubanio.com/simple 安装

#### 启动程序：
使用命令行工具输入 python rank_crawler.py

#### 配置文件信息：
配置文件config.json设置了cookie信息，排行榜页面的相关链接，以及是否保存数据到MongoDB数据库等

#### 注意事项：

该程序会默认使用Excel表格存储数据；

如果爬取不成功，大概率是设置的cookie信息失效，请更换cookie后再次尝试，更换的cookie最好是另外一个账号的，否则仍有可能不成功；

若要使用MongoDB数据库存储信息，先安装好MongoDB数据库，并启动数据库服务，在config.json文件中设置主机地址和端口号；



# **整个项目的大概流程**：





## 1. 第一步获取这100个视频的页面代码

我们先是要获取整个排行榜页面的HTML源代码：

![image-20200610095408790](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610095408790.png)



按下F12启用开发者模式，找到network，按下F5刷新，找到请求页面的url，通过响应结果，我们很容易就能够找到请求的url。

![image-20200610095827621](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610095827621.png)

还可以通过浏览器的搜索栏判断请求地址。例如：

1. ![image-20200610100414998](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610100414998.png)![image-20200610100256195](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610100256195.png)
2.  ![image-20200610100718926](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610100718926.png)

![image-20200610100525922](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610100525922.png)

通过网络请求，我们就能很容易的获取整个排行榜页面HTML源代码：

![image-20200610101248440](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610101248440.png)

而我们要获取视频的信息以及up主的信息很明显是要进入视频页面的url，通过正则表达式，我们就能够获取这100个视频页面的url地址。
它们的地址都是这样的格式：

```html
https://www.bilibili.com/video/BV15Z4y1H7jh
```

每个视频都有一个唯一的BV号，例如这个视频的BV号为：**BV15Z4y1H7jh**

例如我们在浏览器地址栏输入上方这个url，进入页面后如下：

![image-20200610102036762](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610102036762.png)

通过网络请求，我们就能够很容易的这个页面的HTML源代码，而我们后续的操作都是基于此代码来实现的。

## 2. 解析单个视频页面的结构，提取有用数据

通过分析整个页面，我们找到了一个嵌入HTML页面的JavaScript脚本，里面就包含了这个视频的信息和这个视频作者（up主）的信息。

![image-20200610102751797](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610102751797.png)

复制这个脚本中的有用信息使用在线的格式化工具格式化一下，可以看到这是一个json格式的字符串

![image-20200610103322410](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610103322410.png)同样我们还是通过正则表达式提取出有用的信息

这里提取出的信息是一个json类型的字符串，所以我们要使用json.loads()将其装换为Python里的字典对象。转换完成后，直接使用字典的键索引获取到需要的信息，例如：

![image-20200610113922657](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610113922657.png)

![image-20200610114006072](C:\Users\LEGION\Desktop\小组项目\README.assets\image-20200610114006072.png)

将其存入一个新的字典中，再将每一个字典都放入同一个列表中。

## 3. 下载并保存数据信息

#### 该项目中默认使用Excel表格存储数据，另外还可以选择MongoDB数据来存储信息。

#### 1. 视频信息和up主信息的

视频除了一些基本信息外，还可以获取更加详细的信息。例如点赞数，投币数等信息，详细信息的接口为：

> ```
> https://api.bilibili.com/archive_stat/stat?aid=
> ```

aid后面接的是该视频的aid号，aid号的获取在获取视频的基本信息时已经完成。

将获取的详细信息与先前的视频信息合并成一个新的字典。

#### 2. 弹幕的获取与保存

弹幕的接口为：

> ```
> https://api.bilibili.com/x/v2/dm/history?type=1&oid=
> ```

oid后面加的是视频的cid,cid是在视频的页面获取的，除此之外，后面还可以加上data参数，data后面加上当天的日期。

#### 3. 图片的下载

图片的url地址在视频的详细信息里，请求这个地址，就可以得到图片的额二进制流，通过文件的写函数将图片保存。