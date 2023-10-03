import requests
import time 
import pandas as pd 
import numpy as np
import os
import sys
from datetime import datetime,timedelta

class Estate:
    id = ""
    counting_date = datetime.fromtimestamp(time.time())
    prices = []
    dates_of_prices = [] 
    area = 0
    place = ""
    site_id = 0
    link_to_site = "https://www.sreality.cz/detail/prodej/komercni/cinzovni-dum/"+place+"/"+str(site_id)
    def __init__(self,id, counting_date, price, area, place,site_id):
        self.id = id
        self.prices.append(price)
        self.dates_of_prices.append(datetime.fromtimestamp(time.time()))
        self.area = area
        self.place = place 
        self.site_id = site_id
        if counting_date == 0 :
            self.counting_date = datetime.fromtimestamp(time.time())
        else:
            self.counting_date = counting_date


main_data_file = "sreality.xlsx"
data_over = "sreality_6_mesicu.xlsx"
if not os.path.exists(main_data_file):
    #TODO:throw error
    with open(main_data_file,'w') as file:
        pass

if not os.path.exists(data_over):
    with open(data_over,'w') as file:
        pass

time_epoch = str(int(time.time())) 
per_page_results = "1"
root_path = "https://www.sreality.cz/api"
base_path = "/cs/v2/estates?category_main_cb=4&category_sub_cb=38&category_type_cb=1&per_page="+per_page_results+"&tms="+time_epoch+"&usable_area=400%7C700"
result = requests.get(root_path+base_path)
json = result.json()
per_page_results = str(json["result_size"])
base_path = "/cs/v2/estates?category_main_cb=4&category_sub_cb=38&category_type_cb=1&per_page="+per_page_results+"&tms="+time_epoch+"&usable_area=400%7C700"
result = requests.get(root_path+base_path)
json = result.json()
estates = np.array(json["_embedded"]["estates"])
ex_estates = pd.read_excel(main_data_file)
ex_estates_six = pd.read_excel(data_over)
ex_estates = pd.concat([ex_estates,ex_estates_six],axis=0)
ex_estates['checked'] = False
for index,estate in enumerate(estates):
    sys.stdout.write(f'\rProgress: {index}/{per_page_results}')
    link = estate["_links"]["self"]["href"]
    result = requests.get(root_path+link) 
    json = result.json()
    items = np.array(json["items"])
    place = json["seo"]["locality"]
    site_id = link.split("/")[-1]
    price = ""
    id = ""
    area = 0
    exists = False
    for item in items:  
        if item["name"] == "Cena" or item["name"] == "Celková cena":
            price = item["value"].replace("\xa0",'') 
        elif item["name"] == "ID zakázky" or item["name"] == "ID":
            id = str(item["value"])
            if id in ex_estates['id'].values:
                row = ex_estates[ex_estates['id']==id]
                if price != row['prices'][-1]:
                    row['prices'].append(price) 
                    row['date_of_prices'].append(datetime.fromtimestamp(time.time()))
                    row['checked'] = True
                    exists = True
                break;
        elif item["name"] == "Užitná plocha":
            area = item["value"] 
            break; 
             
    if exists == True:
        break;

    date = datetime.fromtimestamp(time.time())
    dates_of_prices = [date]
    prices = [price]
    link_to_site = "https://www.sreality.cz/detail/prodej/komercni/cinzovni-dum/"+place+"/"+str(site_id)
    ex_estates.loc[len(ex_estates)] = {'id':id,'counting_date':date,'prices':prices,'dates_of_prices':dates_of_prices,'area':area,'place':place,'site_id':site_id,'link_to_site':link_to_site,'checked':True}
    sys.stdout.flush()
    

ex_estates = ex_estates[ex_estates['checked'] == True]
sorted_estates = ex_estates.sort_values(by = 'counting_date')
six_months_ago = datetime.now() - timedelta(days=180)
older_than_six_months_df = ex_estates[ex_estates['counting_date'] <= six_months_ago]
newer_than_six_months_df = ex_estates[ex_estates['counting_date'] > six_months_ago]
older_than_six_months_df.to_excel(data_over,index = False)
newer_than_six_months_df.to_excel(main_data_file,index = False)
