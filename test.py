import requests

url = 'http://www.cjs.com.cn/information/index.html?type=%E5%A4%A7%E7%9B%98%E5%88%86%E6%9E%90&canShare=0'

datas = {
    # 'categories': '大盘分析',
    'categories': '早盘风向标',

}
response = requests.post(url, data=datas, timeout=5)
print(response.text)
