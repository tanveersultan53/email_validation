from unittest import result
import pandas as pd
import time
import requests
df = pd.read_csv('test_email.csv')
df.dropna(subset=['Email'],inplace=True)

result = {}


email_list = df['Email'].to_list()

count = 0


for item in email_list:
    time.sleep(2)
    print(item)
    count = count + 1
    try:
        if item:
            response = requests.post('http://127.0.0.1:5000/email_verify',json={
                "email":f"{item}"
            })
            if response.status_code == 200:
                if response.json()['data'] !=None:
                    result[item] = {
                        "lionfish" :{
                        "status":response.json()['data']['status'],
                        "reason":response.json()['data']['reason'],
                        }}
            time.sleep(1)

            response_bouncer = requests.get(f"https://api.usebouncer.com/v1/email/verify?email={item}",headers={"x-api-key":'P7ZSHhmEdk6ah4oghUBB4yIg0zHpqvsddK7HhtfI'})
            if response.json()['data'] !=None:
                if response_bouncer.status_code == 200:
                    result[f"{item}"]['usebouncer'] = {
                        "status":response_bouncer.json()['status'],
                        "reason":response_bouncer.json()['reason'],
                        }
            else:
                result[item] = {
                        "usebouncer" :{
                        "status":response.json()['status'],
                        "reason":response.json()['reason'],
                        }}
            
    except Exception as e:
        pass



import json
with open('result_final_all.json', 'w') as fp:
    json.dump(result, fp)