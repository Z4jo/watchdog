import requests
import time 
import pandas as pd 
import numpy as np
import os
import sys
from datetime import datetime,timedelta

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
print(len(estates))
for index,estate in enumerate(estates):
    sys.stdout.write(f'\rProgress: {index}/{per_page_results}')
    link = estate["_links"]["self"]["href"]
    user_agent = "Insomnia/2023.5.7"
    headers = {"User-Agent": user_agent}
    result = requests.get(root_path+link,headers=headers) 
    json = result.json()
    items = np.array(json["items"])
    place = json["seo"]["locality"]
    site_id = link.split("/")[-1]
    if len(json["price_czk"])==0:
        price = json["items"][0]["value"]
    else:
        price = json["price_czk"]["value_raw"]
    id = ""
    area = 0
    exists = False
    for item in items:  
        if item["name"] == "ID zakázky" or item["name"] == "ID":
            id = str(item["value"])
            if id in ex_estates['id'].values:
                index = ex_estates[ex_estates['id']==id].index[0]
                list_of_prices =  eval(ex_estates.at[index,'prices'])
                if price != list_of_prices[-1]:
                    new_list = eval(ex_estates.at[index,'prices'])
                    new_list.append(price)
                    ex_estates.at[index,'prices']=new_list
                    new_list = eval(ex_estates.at[index,'dates_of_prices'])
                    now = datetime.fromtimestamp(time.time())
                    formatted_date = str(now.year)+"/"+str(now.month)+"/"+str(now.day)
                    new_list.append(formatted_date)
                    ex_estates.at[index,'dates_of_prices'] = new_list
                    ex_estates.at[index,'checked'] = True
                    exists = True
        elif item["name"] == "Užitná plocha":
            area = item["value"] 
            break; 
             
    if exists == True:
        sys.stdout.flush()
        continue;

    date = datetime.fromtimestamp(time.time())
    formatted_date = str(date.year)+"/"+str(date.month)+"/"+str(date.day)
    dates_of_prices = [formatted_date]
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
