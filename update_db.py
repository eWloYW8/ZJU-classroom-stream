import requests
from bs4 import BeautifulSoup
import urllib3
import json
import os
import traceback
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

class ZJUClassroomSession:
    zjuclassroom_login_url = "https://tgmedia.cmc.zju.edu.cn/index.php?r=auth/login&auType=cmc&tenant_code=112&forward=https%3A%2F%2Fclassroom.zju.edu.cn%2F"
    zjuam_login_url = "https://zjuam.zju.edu.cn/cas/login"
    zjuam_pubkey_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    def __init__(self, username, password):
        self.session = requests.session()
        zjuam_login_resp=self.session.get(self.zjuam_login_url, allow_redirects=True)
        zjuam_pubkey_resp=self.session.get(self.zjuam_pubkey_url)
        password_bytes = bytes(password, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(zjuam_pubkey_resp.json()["exponent"], 16)
        M_int = int(zjuam_pubkey_resp.json()["modulus"], 16)
        result_int = pow(password_int, e_int, M_int)
        encrypt_password=hex(result_int)[2:].rjust(128, '0')
        zjuam_login_data={
            'username': username,
            'password': encrypt_password,
            '_eventId': 'submit',
            'execution': BeautifulSoup(zjuam_login_resp.text,"html.parser").find("input",attrs={'name':'execution'})['value'],
            'authcode': '',
        }
        zjuam_login_resp=self.session.post(self.zjuam_login_url,headers=headers,data=zjuam_login_data,verify=False,allow_redirects=True)
        self.session.get(self.zjuclassroom_login_url,headers=headers,allow_redirects=True)
    
    def get_live_courses(self):
        response = self.session.get("https://classroom.zju.edu.cn/courseapi/v2/course-live/search-live-course-list?sub_live_status=ing").json()["list"]
        return response

    def get_class_info(self, course_id, sub_id):
        response = self.session.get(f"https://classroom.zju.edu.cn/courseapi/v3/portal-home-setting/get-sub-info?course_id={course_id}&sub_id={sub_id}").json()["data"]
        return response
    
    def get_room_and_stream_id(self, course_id, sub_id):
        response = self.session.get(f"https://classroom.zju.edu.cn/courseapi/v3/portal-home-setting/get-sub-info?course_id={course_id}&sub_id={sub_id}").json()["data"]

        if "live_url" in response:
            return response['room_name'], response['live_url']['output']['m3u8'].split('/pgc/')[1].split('.m3u8')[0]
        else:
            room_name = response['room_name']
            for i in response["content"].values():
                if isinstance(i, dict) and "stream_name" in i and i["stream_name"] == "教师流":
                    stream_id = i["stream_id"]
                    return room_name, stream_id
            
            response = self.session.get(f"https://yjapi.cmc.zju.edu.cn/courseapi/index.php/v2/meta/getscreenstream?sub_id={sub_id}",headers=headers).json()["result"]["data"]

            for i in response:
                if "教师" in i["stream_name"]:
                    stream_id = i['stream_m3u8'].split('/pgc/')[1].split('.m3u8')[0]
                    return room_name, stream_id

        raise Exception("No stream found")

    
    def get_all_room_and_stream_id(self):
        courses = self.get_live_courses()
        res = {}

        def fetch_room_and_stream(course):
            try:
                room, stream_id = self.get_room_and_stream_id(course["id"], course["sub_id"])
                res[room] = stream_id
                print(f"[GET] Room: {room}, Stream ID: {stream_id}")
            except:
                print("Error: ", course)
                traceback.print_exc()

        with ThreadPoolExecutor() as executor:
            executor.map(fetch_room_and_stream, courses)

        return res


if __name__ == "__main__":
    if os.path.exists("./public/stream_db.json"):
        data = json.load(open("./public/stream_db.json", "r", encoding="utf-8"))
    else:
        data = {}
    print("Original data:" + str(data))
    session = ZJUClassroomSession(os.environ["ZJUAM_USERNAME"], os.environ["ZJUAM_PASSWORD"])
    new_data = session.get_all_room_and_stream_id()
    print("New data:" + str(new_data))
    data.update(new_data)
    print("Updated data:" + str(data))
    with open("./public/stream_db.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
