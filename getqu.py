import requests
import json
import re


fang=requests.get("https://m.lianjia.com/gz/loupan/fang/")#发起请求
pattern = r"window.__INIT_STATE__ = (.*);"
bc_list = re.findall(pattern, fang.text)#找到指定数据
#print(len(bc_list))#只有1项的list
bc=json.loads(bc_list[0])#用json解析
bc2=bc.get('initPageData').get('data').get('filter').get('check_filter').get('region').get('options')[0].get('options')#找到指定数据
block_list=["nansha","liwan","yuexiu","haizhu","tianhe","baiyun","huangpugz","panyu","huadou","zengcheng","conghua"]#广州所有区

bc_res=[]#用于存放商圈结果
f=open('G:/python/Lianjia/bc_res.txt','a')#记录商圈列表
for item in bc2:#遍历每个商圈
    if item.get('full_spell') in block_list:#只要在block_list范围内的数据
        for ele in item.get('options'):
            if ele.get('full_spell') is not None:  #遍历每个非空区域
                res=[]
                res.append(item.get('full_spell'))#区名
                res.append(item.get('name'))
                res.append(ele.get('full_spell'))#商圈名
                res.append(ele.get('name'))
                bc_res.append(res)
                f.write(" ".join(res)+'\n')#记录商圈列表
f.close()

# f2=open('G:/python/Lianjia/bc_res.txt','r')
# bc_res=[bc.strip().split(" ") for bc in f2.readlines()]
# print(bc_res)