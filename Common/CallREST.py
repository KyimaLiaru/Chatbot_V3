import requests
from Common.EnumAPI import ApiInfo

# HTTP Header (나중에 암호화? 필요)
headers = {
    "Content-Type": "application/json",
    "argos": "Rnd2550!"
}

# Send HTTP Request to API Servers
def sendRequest(url, method, body=None):
    api_name, path = url.split("/", 1)

    # Send Request
    if method.lower() == "get":
        response = requests.get(url=f"{ApiInfo[api_name].value}{path}", headers=headers)
    elif method.lower() == 'post':
        response = requests.post(url=f"{ApiInfo[api_name].value}{path}", json=body, headers=headers)
    else: # Other methods like Del or Patch could be added later
        raise Exception(None, "Method not supported.")

    # 결과 출력
    if response.status_code == 200:
        data = response.json()
        return data.get('data')
    else:
        status_code = response.status_code
        # message = f"Internal Server Error: {response.json().get('message', '')}"
        message = f"Internal Server Error: {response}"
        raise Exception(status_code, message)

