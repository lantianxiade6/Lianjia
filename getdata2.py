import requests
import re
import json
from pymongo import MongoClient
import os

class myFang(object):
    """
    初始化函数，爬取的城市分区楼盘信息以及连接mongodb数据库
    """
    def __init__(self):
        host = os.environ.get('MONGODB_HOST', '127.0.0.1')  # 本地数据库
        port = os.environ.get('MONGODB_PORT', '27017')  # 数据库端口
        mongo_url = 'mongodb://{}:{}'.format(host, port)#数据库地址
        mongo_db = os.environ.get('MONGODB_DATABASE', 'Lianjia_loupan')#？
        client = MongoClient(mongo_url)#连接本地的MongoDB
        self.db = client[mongo_db]#连接一个叫Lianjia_loupan的数据库，无则创建
        self.db['fang'].create_index('url', unique=True)  # 连接一个叫fang的集合，以url为主键进行去重，无则创建

    def get_data(self):
        # fang=requests.get("https://m.lianjia.com/gz/loupan/fang/")#发起请求
        # pattern = r"window.__INIT_STATE__ = (.*);"
        # bc_list = re.findall(pattern, fang.text)#找到指定数据
        # #print(len(bc_list))#只有1项的list
        # bc=json.loads(bc_list[0])#用json解析
        # bc2=bc.get('initPageData').get('data').get('filter').get('check_filter').get('region').get('options')[0].get('options')#找到指定数据
        # block_list=["nansha","liwan","yuexiu","haizhu","tianhe","baiyun","huangpugz","panyu","huadou","zengcheng","conghua"]#广州所有区

        # bc_res=[]#用于存放商圈结果
        # f=open('bc_res.txt','a')#记录商圈列表
        # for item in bc2:#遍历每个商圈
        #     if item.get('full_spell') in block_list:#只要在block_list范围内的数据
        #         for ele in item.get('options'):
        #             if ele.get('full_spell') is not None:  #遍历每个非空区域
        #                 res=[]
        #                 res.append(item.get('full_spell'))#区名
        #                 res.append(item.get('name'))
        #                 res.append(ele.get('full_spell'))#商圈名
        #                 res.append(ele.get('name'))
        #                 bc_res.append(res)
        #                 f.write(str(res))#记录商圈列表
        # f.close()

        f2=open('G:/python/Lianjia/bc_res.txt','r')
        bc_res=[bc.strip().split(" ") for bc in f2.readlines()]
        #print(bc_res)     
        f3=open('G:/python/Lianjia/error.txt','a')#记录报错的商圈

        for ele in bc_res[300:301]:#遍历每一个商圈 #一次过爬不下来，要截断for ele in bc_res#[108:]#[140:]#[203:]#[205:]#[217:]#[295:]
            has_more = 1#初始化has_more为1
            count=1#初始化count为1
            while has_more:
                url='https://m.lianjia.com/gz/loupan/{}pg{}/?_t=1&source=index'.format(ele[2],count) #广州新房
                #headers是用于避免'Connection aborted.', OSError("(10060, 'WSAETIMEDOUT')")错误，否则最多只能爬950条
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'} 
                try:
                    qu=requests.get(url,headers=headers,timeout=500)   #发起请求
                    qu2=json.loads(qu.text)#用json解析
                except Exception as e:
                    print(ele[3],'qu error: ',e)#如果报错，那么count和has_more也不会有变化
                    f3.write(" ".join(ele)+'\n')#记录报错的商圈列表
                
                try:
                    qu2_list=qu2['data']['body']['_resblock_list']#获取数据列表(no_result_resblocks是猜你喜欢)

                    for row in qu2_list:#遍历数据列表
                        result=self.getAttr(row)#调用函数获取指定数据
                        self.db['fang'].update_one({'url': result['url']}, {'$set': result}, upsert=True)#插入数据到数据库
                        print('成功保存数据：',result['resblock_name'],'from page',count,'of ',ele[3])#如果该商圈没有楼盘数据这堆代码不会报错，貌似没有运行

                    if qu2['data']['has_more_data']==0:
                        has_more=0#如果has_more_data=0则会转入下一个商圈
                    else:
                        count+=1#如果has_more_data=1则会爬下一页数据
                except Exception as e:
                    has_more=0#如果报错则直接认为这个商圈没有数据
                    print(ele[3],'error: ',e)

            print('完成：',ele)#如果该商圈没有楼盘数据这句一样会运行
        f3.close()

    @staticmethod
    def getAttr(data):
        result={}
        result['id']=data['id']#'2120036540761290'
        result['city_name']=data['city_name']#'广州市',
        result['min_frame_area']=data['min_frame_area']#'70',#最小建面
        result['max_frame_area']=data['max_frame_area']#'110',#最大建面
        result['district']=data['district']# '荔湾',
        result['bizcircle_name']=data['bizcircle_name']# '广钢新城',
        result['decoration']=data['decoration']# '精装修',
        result['longitude']=data['longitude']# '113.247911',
        result['latitude']=data['latitude']# '23.070291',
        result['frame_rooms_desc']=data['frame_rooms_desc']# '2/3居',
        result['resblock_name']=data['resblock_name']# '保利东郡',
        result['resblock_alias']=data['resblock_alias']# '曼语花园/曼源花园',
        result['address']=data['address']# '开拓路与求实一横路交界处',
        result['store_addr']=data['store_addr']# '广钢新城南区保利光合馆',
        result['average_price']=data['average_price']# '55000',
        result['converged_rooms']=data['converged_rooms']#[{'bedroom_count': '2', 'area_range': '70㎡'},{'bedroom_count': '3', 'area_range': '98-110㎡'}],
        result['tags']=data['tags']# ['品牌房企', '小户型', '绿化率高', '大型社区'],
        result['house_type']=data['house_type']# '住宅',
        result['sale_status']=data['sale_status']# '在售',
        result['open_date']=data['open_date']# '2019-05-26',
        result['lowest_total_price']=data['lowest_total_price']# '3700000',
        result['show_price']=data['show_price']# '55000',##均价
        result['show_price_unit']=data['show_price_unit']# '元/平'
        result['total_price_start']=data['total_price_start']# '364',#总价-最低价
        result['total_price_start_unit']=data['total_price_start_unit']# '万/套起',
        result['avg_price_start']=data['avg_price_start']# '51923',#均价的最低价
        result['avg_price_start_unit']=data['avg_price_start_unit']# '元/平起',
        result['on_time']=data['on_time']#'2018-12-17 16:05:28',
        result['project_desc']=data['project_desc']#'保利品牌，广佛交界，复式住宅',  
        result['url']=data['url']#"/gz/loupan/p_mjdcsabiwgg/"
        return result

if __name__ == '__main__':
    fang = myFang()#实例化一个Fang类
    fang.get_data()#调用get_data()方法