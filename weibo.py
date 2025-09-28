import requests
import time
from tqdm import trange


class Weibo:
    def __init__(self, cookie, uid):
        self.cookie = cookie
        self.uid = uid
        self.base_url = "https://weibo.com"
        self.cookie_dict = self._parse_cookie(cookie)
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "client-version": "v2.47.119",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "server-version": "v2025.09.26.2",
            "x-requested-with": "XMLHttpRequest",
            "x-xsrf-token": self.cookie_dict.get("XSRF-TOKEN", ""),
            "cookie": self.cookie,
            "referer": f"{self.base_url}/u/{self.uid}",
        }

    def _parse_cookie(self, cookies_str):
        cookies_dict = {}
        cookies_list = cookies_str.split(";")

        for cookie in cookies_list:
            cookie = cookie.strip()
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies_dict[key.strip()] = value.strip()

        return cookies_dict

    # 0: 所有人可见 1: 仅自己可见 2: 好友圈可见 10: 仅粉丝可见
    def modify_visible(self, post_id, visible):
        url = f"{self.base_url}/ajax/statuses/modifyVisible"

        if post_id["visible"] == visible:
            return {"ok": 1, "message": "无需修改"}

        data = {"ids": post_id["id"], "visible": visible}
        response = requests.post(url, headers=self.headers, json=data)
        time.sleep(1)
        return response.json()

    def get_blog(self, page=1):
        url = f"{self.base_url}/ajax/statuses/mymblog?uid={self.uid}&page={page}&feature=0"

        response = requests.get(url, headers=self.headers)
        return response.json()


uid = ""
cookies = ""
w = Weibo(cookies, uid)

since_id = None
ids = []
page = 1

while True:
    res = w.get_blog(page=page)

    data = res.get("data", {})
    weibos = data.get("list", [])
    since_id = data.get("since_id")

    if since_id:
        ids.extend([{"id": i["idstr"], "visible": i["visible"]["type"]} for i in weibos])
        print(f"第 {page} 页获取完成, since_id={since_id}")
        page += 1
    else:
        # 最后一页
        ids.extend([{"id": i["idstr"], "visible": i["visible"]["type"]} for i in weibos])
        print(f"第 {page} 页获取完成, since_id={since_id}")
        break

print(f"共获取到 {len(ids)} 条微博")

for i in trange(len(ids), desc="修改中"):
    res = w.modify_visible(ids[i], 1)

    if res.get("ok") != 1:
        print(f"{i} 修改失败，原因：{res.get('message')}")
