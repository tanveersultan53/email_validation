
# Python program to read
# json file
  
  
import json
  




f = open("result_final_all.json")
data = json.load(f)

status_count = {
}


status_count_bouncer = {

}
# "lionfish": {
#             "status": "undeliverable",
#             "reason": "5.7.606 Access denied, banned sending IP [182.185.200.160]. To request removal from this list please visit https://sender.office.com/ and follow the directions. For more information please go to  http://go.microsoft.com/fwlink/?LinkID=526655 AS(1430) [VE1EUR02FT038.eop-EUR02.prod.protection.outlook.com]"
#         }

for key, value in data.items():
    for inner_key,inner_value in value['lionfish'].items():
        if inner_key == 'status':
            if inner_value in status_count.keys():
                status_count[data[key]['lionfish'][inner_key]] +=1
            else:
                status_count[data[key]['lionfish'][inner_key]] = 1

for key, value in data.items():
    for inner_key,inner_value in value['usebouncer'].items():
        if inner_key == 'status':
            if inner_value in status_count_bouncer.keys():
                status_count_bouncer[data[key]['usebouncer'][inner_key]] +=1
            else:
                status_count_bouncer[data[key]['usebouncer'][inner_key]] = 1

print(status_count)

print(status_count_bouncer)
