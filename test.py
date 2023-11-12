import numpy as np
import pandas as pd 
import time 
from datetime import datetime,timedelta
import requests
time_epoch = str(int(time.time())) 
user_agent = "Insomnia/2023.5.7"
headers = {"User-Agent": user_agent}
json = requests.get("https://www.sreality.cz/api/cs/v2/estates/3153622092?tms="+time_epoch,headers=headers).json()
print(json)
