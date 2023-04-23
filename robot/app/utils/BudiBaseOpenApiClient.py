import http.client
import json
import os
from dotenv import load_dotenv

load_dotenv()  # 读取 .env 文件
BUDI_BASE_URL = os.getenv("BUDI_BASE_URL")
BUDI_BASE_KEY = os.getenv("BUDI_BASE_KEY")


class ApplicationClient:

    @staticmethod
    def create(app_name, app_url):
        conn = http.client.HTTPSConnection(BUDI_BASE_URL)
        payload = json.dumps({
            "name": app_name,
            "url": app_url
        })
        headers = {
            'x-budibase-app-id': 'sit',
            'Content-Type': 'application/json',
            'x-budibase-api-key': BUDI_BASE_KEY
        }
        conn.request("POST", "/api/public/v1/applications", body=payload, headers=headers)
        res = conn.getresponse()
        print(res.status)
        print(res.reason)
        print(res.read().decode())
        data = res.read()
        print(data.decode("utf-8"))
        conn.close()
