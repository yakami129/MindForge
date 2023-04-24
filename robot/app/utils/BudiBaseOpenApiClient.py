import json
import logging
import os

import requests
from dotenv import load_dotenv
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

load_dotenv()  # 读取 .env 文件
BUDI_BASE_URL = os.getenv("BUDI_BASE_URL")
BUDI_BASE_KEY = os.getenv("BUDI_BASE_KEY")


class ApplicationClient:

    @staticmethod
    def create(app_name, app_url):
        url = BUDI_BASE_URL + "/api/public/v1/applications"
        data = {
            "name": app_name,
            "url": app_url
        }
        headers = {
            'x-budibase-app-id': 'sit',
            'Content-Type': 'application/json',
            'x-budibase-api-key': BUDI_BASE_KEY
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
        return response.json()


class TableClient:

    @staticmethod
    def create(app_id, schema_obj):
        url = BUDI_BASE_URL + "/api/public/v1/tables"
        data = {"name": schema_obj.get("schema")}
        schema = {
            "Auto ID": {
                "name": "Auto ID",
                "type": "number",
                "subtype": "autoID",
                "icon": "ri-magic-line",
                "autocolumn": True,
                "constraints": {
                    "type": "number",
                    "presence": False,
                    "numericality": {
                        "greaterThanOrEqualTo": "",
                        "lessThanOrEqualTo": ""
                    }
                }
            },
            "Created By": {
                "name": "Created By",
                "type": "link",
                "subtype": "createdBy",
                "icon": "ri-magic-line",
                "autocolumn": True,
                "constraints": {
                    "type": "array",
                    "presence": False
                },
                "tableId": "ta_users",
                "fieldName": schema_obj.get("schema") + "-Created By"
            },
            "Created At": {
                "name": "Created At",
                "type": "datetime",
                "subtype": "createdAt",
                "icon": "ri-magic-line",
                "autocolumn": True,
                "constraints": {
                    "type": "string",
                    "length": {},
                    "presence": False,
                    "datetime": {
                        "latest": "",
                        "earliest": ""
                    }
                }
            },
            "Updated By": {
                "name": "Updated By",
                "type": "link",
                "subtype": "updatedBy",
                "icon": "ri-magic-line",
                "autocolumn": True,
                "constraints": {
                    "type": "array",
                    "presence": False
                },
                "tableId": "ta_users",
                "fieldName": schema_obj.get("schema") + "-Updated By"
            },
            "Updated At": {
                "name": "Updated At",
                "type": "datetime",
                "subtype": "updatedAt",
                "icon": "ri-magic-line",
                "autocolumn": True,
                "constraints": {
                    "type": "string",
                    "length": {},
                    "presence": False,
                    "datetime": {
                        "latest": "",
                        "earliest": ""
                    }
                }
            }
        }

        ## TODO 暂时都使用文本类型
        for column in schema_obj.get("columns"):
            schema_column = {
                "type": "string",
                "constraints": {
                    "type": "string",
                    "length": {
                        "maximum": 1000
                    },
                    "presence": False
                },
                "name": column.get("name")
            }
            schema[column.get("name")] = schema_column

        data["schema"] = schema
        body = json.dumps(data)
        print(body)

        headers = {
            'x-budibase-app-id': app_id,
            'Content-Type': 'application/json',
            'x-budibase-api-key': BUDI_BASE_KEY
        }

        response = requests.request("POST", url, headers=headers, data=body)
        return response.json()
