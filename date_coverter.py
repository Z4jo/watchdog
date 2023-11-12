import pandas as pd
import numpy as np 
import re
path = "sreality.xlsx"

df = pd.read_excel(path)
indexes = df.index
pattern = r'\[datetime.datetime\((\d{4}), (\d|\d{2}), (\d|\d{2}),'
for i in indexes:
    date = df.at[i,'dates_of_prices']
    match = re.search(pattern, date)
    year,month,day = "","",""
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
    formated_string = year + "/" +month+"/"+day 
    df.at[i,'dates_of_prices']=[formated_string]
df.to_excel(path,index=False)






















