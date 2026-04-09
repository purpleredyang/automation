import requests
import uuid
import datetime
from datetime import timedelta

class DiverOutAPIClient:
    def __init__(self, base_url="https://api-dev.diverout.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def login_with_cookie(self, session_id_cookie, cdn_cookie):
        self.session.cookies.set('sessionId', session_id_cookie)
        self.session.cookies.set('Cloud-CDN-Cookie', cdn_cookie)
        self.session.headers.update({
            "User-Agent": "DiverOut-Automated-QA-Client",
            "Content-Type": "application/json"
        })
        print("Cookies 設置完成，API Client 初始化完畢！")

    def test_authentication(self, endpoint_path="/v4/auth/me"):
        url = f"{self.base_url}{endpoint_path}"
        try:
            response = self.session.get(url)
            print(f"Auth Test -> GET {url}")
            print(f"Status Code: {response.status_code}")
            return response.status_code
        except Exception as e:
            print(f"請求失敗: {e}")
            return None

    def create_mock_dive_logs(self, count=50, post_type="scuba"):
        """
        透過 /v1/sync/posts 新增潛水紀錄。
        根據 Repository 內的 APIObject.MyPosts.Post 定義所需的欄位。
        """
        url = f"{self.base_url}/v1/sync/posts"
        success_count = 0
        
        now = datetime.datetime.utcnow()
        
        for i in range(count):
            start_time = now - timedelta(days=i, hours=2)
            end_time = start_time + timedelta(minutes=45)
            
            # format -> "2023-11-20T12:00:00Z"
            iso_start = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            iso_end = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            iso_created = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            payload = {
                "id": str(uuid.uuid4()).upper(),
                "startAt": iso_start,
                "endAt": iso_end,
                "createdAt": iso_created,
                "postType": post_type,
                "maxDepth": 25.5,
                "maxDepthUnit": "m",
                "waterTemperature": 26.5,
                "waterTemperatureUnit": "C",
                "cylinders": [],       # 空陣列即可
                "mediaUrls": [],       # 空陣列即可
                "isDefaultSample": False,
                "weights": [2.0],
                "weightsUnit": "kg",
                "note": f"QA Automation Test Log {i+1}"
            }
            
            resp = self.session.post(url, json=payload)
            if resp.status_code in [200, 201]:
                success_count += 1
            else:
                print(f"寫入失敗 [第 {i+1} 筆] Status: {resp.status_code}, Msg: {resp.text}")
                
        print(f"已成功發布了 {success_count} / {count} 筆假潛水紀錄！")

if __name__ == "__main__":
    client = DiverOutAPIClient()
    
    # User 驗證資料
    SESSION_ID = "s:6bd8b195-624f-4c40-8996-88eda98ac719.Xb0Q8Jt3M/TdeANfVv/4DXXQB90JNezl3kUS9jMLHaM"
    CDN_COOKIE = "URLPrefix=aHR0cHM6Ly9zdGF0aWMtZGV2LmRpdmVyb3V0LmNvbS92aWRlb3Mv:Expires=1775398475:KeyName=static-lb-be-sign-key:Signature=syxIU4eKOsdxLzAn0nacjckz3p8"
    
    client.login_with_cookie(SESSION_ID, CDN_COOKIE)
    
    # 測試驗證
    client.test_authentication()
    
    # 當未來需要造 50 筆資料時，把這行的註解拿掉執行即可：
    # client.create_mock_dive_logs(50, post_type="scuba")
