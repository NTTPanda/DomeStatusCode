# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests>=2.32.5",
# ]
# ///


import os
from datetime import datetime
import time
import requests



status_file_path=""
log_folder=""
tasker_log_file_path=""
os.makedirs(log_folder,exist_ok=True)
url=""
tasker_url=""
while True:
    try:
        try:
            res=requests.post(url,json={},timeout=15) #Request to 3001 Port
            resData=res.json()
            ocsDomeStatus=resData.get("result",{}).get("dome",{}).get("state",{})
            
        except Exception as e:
            ocsDomeStatus=f'ERROR{e}'

        try:
           tasker_res=requests.post(url,json={},timeout=15) #Request to 3002 Port
           tasker_resData=res.json()
           tasker_Health_Status=tasker_resData.get("result",{}).get("state",{})
           tasker_Running_Status=tasker_resData.get("result",{}).get("running",{})
        except Exception as e:
            ocsDomeStatus=f'ERROR{e}'

        try:
            with open(status_file_path,"r") as f:
                status =f.read().strip()
        except Exception as e:
            status=f'ERROR{e}'
            
        current_date=datetime.now().strftime("%d%b%Y")
        log_file_name=f"{current_date}DomeStatus.log"
        log_file_path=os.path.join(log_folder,log_file_name)
        timestramp=datetime.now().strftime("%Y-%m%d %H:%M:%S")

        logentry=f"{timestramp}- Dome Status From File : {tasker_Health_Status} From OCS: {ocsDomeStatus}\n" # Log Entry For Dome Status
        tasker_logentry=f"{timestramp}- Tasker Track Status : {status} Tasker Running Status: {tasker_Running_Status}\n"
        with open(log_file_path,"a") as log_file:
            log_file.write(logentry)

        with open(tasker_log_file_path,"a") as log_file:
            log_file.write(tasker_logentry)
    except Exception as fatal:
        print("FATAL",fatal)
    time.sleep(60)
        
            