# !/usr/bin/python3
# -*- encoding: utf-8 -*-
'''
@Author  :   Harvey
@Software:   TestCase
@Time    :   2023/5/5
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
'''
import requests
import json
import re
import os

reports_path = os.path.dirname(os.path.abspath(os.path.split(os.path.realpath(__file__))[0]))
# reports_path = 
reports_path = reports_path + '/' + 'Config'


class MesSocket():
    def __init__(self):
        self.url = "http://172.20.0.99:9002/MainWebForm.aspx"

    def save_mes_info(self, rk_num):
        """
        发送post请求, 携带sn号需要手动输入
        并将返回数据保存到json文件中
        """
        payload = {"p": "GetAnconaInfo", "cmd": "ATT", "sn": rk_num}
        response = requests.post(self.url, json=payload)
        data = response.json()
        if data['Flag'] == 0:
            server_sn = data["Results"]["server_sn"]
            rk_part_number = data["Results"]["rk_part_number"]
            data["Results"]["rk_customer_part_number"]
            with open(f'{reports_path}/{server_sn}_mes.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(data, indent=4, sort_keys=False) + '\n')
            return (rk_part_number, 200)
            
        else:
            return (data["ErrorMessage"], 404)



    def get_mes_info(self, server_sn):
        with open(f'{reports_path}/{server_sn}_mes.json', 'r', encoding='UTF-8') as f:
            output = eval(f.read())
            print(output)
        return output

    def json_filter(self, data, info):
        for line in data.split('\n'):
            if info in line:
                rst = line.split(':')[1].strip()
                return rst
            
    def get_transit_information(self,rk_num):
        payload = {"cmd": "ATT", "p": "GetNextTestInfo", "sn": rk_num}
        response = requests.post(self.url, json=payload)
        data = response.json()
        if data['Flag'] == 0:
            return data
        else:
            print(data["ErrorMessage"])
            return data["ErrorMessage"]
        
    def send_transit_information(self,terminalName, sn, rst, start_time, end_time):
        url = "http://172.20.0.99:9002/MainWebForm.aspx"
        payload = {
                    "cmd": "ADD",
                    "empNo": "",
                    "terminalName": terminalName,
                    "wo": "",
                    "sn": sn,
                    "csn": "",
                    "kpsn": "",
                    "lotNo": "",
                    "machineNo": "",
                    "toolingNo": "",
                    "cavityNo": "",
                    "result": rst,
                    "defectCode": "",
                    "uut_start": start_time,
                    "uut_stop": end_time,
                    "limits_version": "",
                    "software_name": "",
                    "software_version": ""
                }
        response = requests.post(url, json=payload)
        data = response.json()
        if data['Flag'] == 0:
            return True
        else:
            return False
            print(data["ErrorMessage"])
            
    def save_mes_info123(self, rk_num):
        rk_num = input("please input sn number:")
        data = {
    "Flag": 0,
    "ErrorMessage": "Success",
    "Results": {
        "rk_customer_part_number": "TG88M1S1V5X7.03ZA.C0V1P4U8",
        "rk_part_number": "RK0037030011",
        "server_customer_part_number": "TG88M1S1V5.32.C0V1P0U2",
        "server_sn": "KS00370335A00M",
        "server_product_name": "8082B0000022",
        "jbog_product_name": "ST0037030021",
        "server_tdid": "TD11101003116919",
        "hib_sn": "KS1408700334S0018",
        "hib_part_number": "231A14087003",
        "jbog_customer_part_number": "TB33G1.05ZB.C0V1P4U6",
        "jbog_sn": "KS003703358001",
        "jbog_tdid": "TD11101003116911",
        "ubb_sn": "KS1408800634M0247",
        "oam_sn": [
            {
                "slot": "01",
                "oam_sn": "KS1408400434Q0011",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "02",
                "oam_sn": "KS1408400434Q0017",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "03",
                "oam_sn": "KS1408400434Q0038",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "04",
                "oam_sn": "KS1408400434Q0048",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "05",
                "oam_sn": "KS1408400434Q0082",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "06",
                "oam_sn": "KS1408400434Q0078",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "07",
                "oam_sn": "KS1408400434Q0077",
                "oam_part_no": "231A14084004"
            },
            {
                "slot": "08",
                "oam_sn": "KS1408400434Q0086",
                "oam_part_no": "231A14084004"
            }
        ],
        "sn_80": "HQ31200001Q2034D0124",
        "sn_40": "",
        "nvme_board_sn": "HQ3120M0220003240036,HQ3120M0220003240059"
    }
}
        with open(f'{reports_path}/{rk_num}_mes.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(data, indent=4, sort_keys=False) + '\n')
        return (rk_num, 200)
        

if __name__ == "__main__":
    mes = MesSocket()
    # mes.save_mes_info()
    mes.get_mes_info()
