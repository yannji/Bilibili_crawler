import os
import time
import datetime
import json
import re
import threading
import requests
import xlwt
config_fp = open("./config.json","r",encoding="utf-8")
config_data = json.load(config_fp)
config_fp.close()
HOST = config_data["host"]
PORT = config_data["port"]
class Crawler(object):
    def __init__(self):
        config_path = open(r'./config.json','r',encoding="utf-8")  #读取配置文件
        time.sleep(0.1) # 设置延迟
        self.rank_url = json.load(config_path)["page"]["全站榜"]["三日榜"] #参照配置文件进行选择
        config_path.close()
        self.base_url = "https://api.bilibili.com/archive_stat/stat?aid="   #视频详细信息的接口
        self.danmu_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid='
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.116 Mobile Safari/537.36",
            "Referer": "https://www.bilibili.com/"
        }
        try:
            config_path = open(r'./config.json', 'r', encoding="utf-8")
            self.cookie = json.load(config_path)["cookie"]
        except Exception as result:
            exit(result)
        self.page_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                           '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'),
            "Cookie":self.cookie
        }

        config_path.close()
        self.__get_data_from_internet()
        self.__analytical_data()
        self.__detail_analytical()
        self.__video_detail_get()
        self.__multi_threading()
        self.__save_as_excel()
        config_path = open(r'./config.json', 'r', encoding="utf-8")
        if json.load(config_path)["mongodb"]:
            self.__save_to_mongodb()
        config_path.close()

        '''
        给出相关的网址链接和伪造请求头,读取配置信息，并执行一些函数
        '''


    def __multi_threading(self):
        self.g_lock = threading.Lock()
        th1 = threading.Thread(target=self.__download_picture)
        th2 = threading.Thread(target=self.__danmu_crawler_oneday, args=(0,10))
        th3 = threading.Thread(target=self.__danmu_crawler_oneday, args=(10, 20))
        th4 = threading.Thread(target=self.__danmu_crawler_oneday, args=(20, 30))
        th5 = threading.Thread(target=self.__danmu_crawler_oneday, args=(30, 40))
        th6 = threading.Thread(target=self.__danmu_crawler_oneday, args=(40, 51))
        th1.start()
        th2.start()
        th3.start()
        th4.start()
        th5.start()
        th6.start()
    '''
     启用多线程爬虫,这里的弹幕爬虫只爬取单日的，多日爬虫真的太容易被禁止访问了
     因为访问弹幕的接口速度比其他的慢，所以在进程中给弹幕爬取设置五个线程
    '''

    def __get_data_from_internet(self):
        self.resp = requests.get(self.rank_url, headers=self.headers)
        self.text = self.resp.content.decode('utf-8')
        self.page_link_list = re.findall(r'<div class="info">.*?<a href="(.*?)".target=', self.text, re.DOTALL)
        time.sleep(1)
        self.video_data_list = []
        self.up_data_list = []
        self.danmu_id_list = []
        for page_link in self.page_link_list:
            time.sleep(0.1)
            print("正在获取来自页面%s的数据" % page_link)
            try:
                response = requests.get(url=page_link, headers=self.page_headers)
                data = response.content.decode("utf-8")
                video_data = re.findall(r'"videoData":(.*?),"rights":', data, re.DOTALL)
                self.video_data_list.append(video_data[0] + '}')
                up_data = re.findall(r'"upData":(.*?),"pendant":', data, re.DOTALL)
                self.up_data_list.append(up_data[0] + '}')
                danmu_id = re.findall(r'pages.*?cid":(.*?),.page',data,re.DOTALL)
                self.danmu_id_list.append(danmu_id[0])
            except Exception as result:
                print(result)
        self.core_data = list(zip(self.video_data_list, self.up_data_list))

        '''
                从网上获取源数据,并储存为元素为元组的列表
                '''


    def __analytical_data(self):
        self.video_dic_list = []
        self.up_dic_list = []
        for video_one, up_one in self.core_data:
            try:
                video_dic = json.loads(video_one)
                self.video_dic_list.append(video_dic)
                up_dic = json.loads(up_one)
                self.up_dic_list.append(up_dic)
            except Exception as result:
                print(result)
        '''
               对数据做进一步的分析，将列表中的元组拆包，并反序列化成字典，
               并将反序列化的视频信息和up主信息分别加入到列表self.video_dic_list和self.up_dic_list中
               '''
    def __detail_analytical(self):
        self.new_video_data_list = []
        self.new_up_data_list = []
        for video_data in self.video_dic_list:
            temp_dic_video = {
                "BV号": video_data['bvid'],
                "aid": video_data['aid'],
                "分类":video_data['tname'],
                "封面图片地址":video_data['pic'],
                "标题":video_data['title'],
                "发布日期":time.strftime('%Y-%m-%d',time.gmtime(video_data['pubdate'])),
                "发布的精准日期":time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(video_data['pubdate'])),
                "视频描述":video_data['desc'],
                "视频时长（秒）":video_data['duration'],
                "视频集数":video_data['videos']
            }
            self.new_video_data_list.append(temp_dic_video)
        for up_data in self.up_dic_list:
            temp_dic_up = {
                "UP主":up_data["name"],
                "性别":up_data["sex"],
                "UP主id":up_data["mid"],
                "粉丝数量":up_data["fans"],
                "ta的关注数":up_data["attention"],
                "个人说明":up_data["sign"]
            }
            self.new_up_data_list.append(temp_dic_up)
        '''
        对元素为字典的列表中的数据做细节分析，并存放到新的列表中
        '''

    def __video_detail_get(self):
        index = 0
        for dic in self.new_video_data_list:
            aid = dic["aid"]
            intact_url = self.base_url + str(aid)
            resp = requests.get(url=intact_url, headers=self.headers).content.decode("utf-8")
            data_dic = json.loads(resp)
            temp_dic = {
                "播放量":data_dic["data"]["view"],
                "弹幕总量":data_dic["data"]["danmaku"],
                "评论数":data_dic["data"]["reply"],
                "点赞数":data_dic["data"]["favorite"],
                "投币数":data_dic["data"]["coin"],
                "分享数":data_dic["data"]["share"]
            }
            dictMerged = dict(dic, **temp_dic)
            self.new_video_data_list[index] = dictMerged
            index += 1
            time.sleep(0.5)

    def __danmu_crawler_all(self,i,j):
        self.g_lock.acquire()
        self.i,self.j = i,j
        self.path = r'E:\数据\弹幕'
        self.folder = os.path.exists(self.path)
        if not self.folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(self.path)
        id_index = 0
        for video_data in self.new_video_data_list[self.i:self.j]:
            since_time = str(video_data["发布日期"])
            now_time = str(time.strftime('%Y-%m-%d',time.gmtime(time.time())))  #通过当前时间的时间戳获取当前时间的时间格式
            path = r'E:\数据\弹幕\视频{}'.format(video_data["BV号"])
            today_add_1 = since_time
            url_first = self.danmu_url + self.danmu_id_list[id_index] + '&date='    #初步处理的url
            print("正在下载视频{}的弹幕".format(video_data["BV号"]))
            while today_add_1 < now_time:
                new_path = path + (str(today_add_1)+"时的弹幕.txt")     #设置文件名
                resp = requests.get(url=url_first+today_add_1,headers=self.page_headers).content.decode("utf-8")
                with open(new_path,'w',encoding='utf-8') as fp:
                    print("正在对%{}作出处理".format(new_path))
                    ls = re.findall(r"<d p=.*?>(.*?)</d>", resp, re.DOTALL)     #对爬取的xml文件做进一步处理以获取纯弹幕
                    data = str(ls)
                    fp.write(data)
                    fp.write("\n日期为：")
                    fp.write(str(today_add_1))
                today_add_1 = (datetime.datetime.strptime(today_add_1,"%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d") #增加一天
            id_index +=1
        time.sleep(2)         #设置延迟，可尽量调大写，过小太容易被禁止访问，禁止后更换只要更换配置文件中的cookie即可
        self.g_lock.release()
        '''
        爬取自发布日期起的弹幕并储存文件
        '''

    def __danmu_crawler_oneday(self, i, j):
        self.g_lock.acquire()
        self.i, self.j = i, j
        self.path = r'E:\数据\弹幕'
        self.folder = os.path.exists(self.path)
        if not self.folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(self.path)
        id_index = 0
        for video_data in self.new_video_data_list[self.i:self.j]:
            now_time = str(time.strftime('%Y-%m-%d', time.gmtime(time.time())))  # 通过当前时间的时间戳获取当前时间的时间格式
            path = r'E:\数据\弹幕\视频{}的弹幕.txt'.format(video_data["BV号"])
            url = self.danmu_url + self.danmu_id_list[id_index] + '&date=' + now_time
            print("正在下载视频{}的弹幕".format(video_data["BV号"]))
            resp = requests.get(url=url, headers=self.page_headers).content.decode("utf-8")
            with open(path, 'w', encoding='utf-8') as fp:
                print("正在对{}作出处理".format(path))
                ls = re.findall(r"<d p=.*?>(.*?)</d>", resp, re.DOTALL)  # 对爬取的xml文件做进一步处理以获取纯弹幕
                data = str(ls)
                fp.write(data)
                fp.write("\n日期为：")
                fp.write(str(now_time))
            id_index += 1
        time.sleep(2)
        self.g_lock.release()

        '''
                爬取今日弹幕并储存文件
                '''

    def __download_picture(self):
        self.path = r'E:\数据\封面图片'
        self.folder = os.path.exists(self.path)
        if not self.folder:            # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(self.path)
        for dic in self.new_video_data_list:
            print("正在下载封面{}.jpg".format(dic["BV号"]))
            pic = requests.get(url=dic['封面图片地址'],headers=self.headers).content
            with open(r"E:\数据\封面图片\{}.jpg".format(dic["BV号"]),"wb") as fp:
                fp.write(pic)
                fp.close()
            time.sleep(0.1)         #设置延迟以防被禁
    '''
    封面图片的下载
    '''
    def __save_as_excel(self):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.worksheet1 = self.workbook.add_sheet('sheet1')  #创建工作表
        i = 0
        for dic in self.new_video_data_list:
            j = 0
            for key in dic:
                self.worksheet1.write(i, j, key)
                j += 1
                self.worksheet1.write(i, j, dic[key])
                j += 1
            i += 2
        i = 1
        for dic in self.new_up_data_list:
            j = 0
            for key in dic:
                self.worksheet1.write(i, j, key)
                j += 1
                self.worksheet1.write(i, j, dic[key])
                j += 1
            i += 2
        self.workbook.save(r'E:\数据\B站视频排行.xls')

        '''
        将数据保存为excel表格
        '''
    def __save_to_mongodb(self):
        import pymongo #导入模块
        self.client = pymongo.MongoClient(host=HOST, port=PORT) #创建client对象
        self.db = self.client["B站"]     #创建数据库对象
        self.collection1 = self.db["video_data"]        #创建集合
        self.collection2 = self.db["up_data"]
        self.collection1.insert_many(self.new_video_data_list)  #插入文档
        self.collection2.insert_many(self.new_up_data_list)

if __name__ == '__main__':
    print("开始启动爬虫")
    spider = Crawler()