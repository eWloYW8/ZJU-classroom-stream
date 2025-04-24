import requests
from bs4 import BeautifulSoup
import urllib3
import json
import os

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

class ZJUClassroomSession:
    zjuclassroom_login_url = "https://tgmedia.cmc.zju.edu.cn/index.php?r=auth/login&auType=&tenant_code=112&forward=https%3A%2F%2Fclassroom.zju.edu.cn%2F"
    zjuam_login_url = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fzjuam.zju.edu.cn%2Fcas%2Foauth2.0%2FcallbackAuthorize"
    zjuam_pubkey_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

    def __init__(self, username, password):
        self.session = requests.session()
        zjuam_login_resp=self.session.get(self.zjuclassroom_login_url, allow_redirects=True)
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
        self.session.get("https://classroom.zju.edu.cn",headers=headers)
    
    def get_live_courses(self):
        response = self.session.get("https://classroom.zju.edu.cn/courseapi/v2/course-live/search-live-course-list?sub_live_status=ing").json()["list"]
        return response

    def get_class_info(self, course_id, sub_id):
        response = self.session.get(f"https://classroom.zju.edu.cn/courseapi/v3/portal-home-setting/get-sub-info?course_id={course_id}&sub_id={sub_id}").json()["data"]
        return response
    
    def get_room_and_stream_id(self, course_id, sub_id):
        response = self.session.get(f"https://classroom.zju.edu.cn/courseapi/v3/portal-home-setting/get-sub-info?course_id={course_id}&sub_id={sub_id}").json()["data"]

        if "live_url" not in response:
            room_name = response['room_name']
            for i in response["content"].values():
                if isinstance(i, dict) and "stream_name" in i and i["stream_name"] == "教师流":
                    stream_id = i["stream_id"]
                    return room_name, stream_id

        return response['room_name'], response['live_url']['output']['m3u8'].split('/pgc/')[1].split('.m3u8')[0]
    
    def get_all_room_and_stream_id(self):
        courses = self.get_live_courses()
        res = {}
        for course in courses:
            room, stream_id = self.get_room_and_stream_id(course["id"], course["sub_id"])
            res[room] = stream_id
        return res


if __name__ == "__main__":
    if os.path.exists("stream_db.json"):
        data = json.load(open("stream_db.json", "r", encoding="utf-8"))
    else:
        data = {}
    session = ZJUClassroomSession(os.environ["ZJUAM_USERNAME"], os.environ["ZJUAM_PASSWORD"])
    data.update(session.get_all_room_and_stream_id())
    with open("stream_db.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)