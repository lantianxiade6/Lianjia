# Lianjia

爬取链家数据  
getqu.py获取链家的商圈，并存于bc_res.txt  
getdata2.py根据bc_res.txt的商圈爬取链家数据，存入MongoDB，如果有error会记入error.txt（需手动重爬）  
楼盘图鉴.ipynb为jupyter程序，对爬取到的数据进行数据分析，以获取广佛新楼盘最新情况
