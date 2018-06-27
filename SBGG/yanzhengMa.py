import json

import requests
from urllib.parse import urlencode


myHearder = {
     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3964.2 Safari/537.36",
     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


imageListData = []

def req_imageInterface(num):
    data = {
        'pageNum' : num * 20,
        'id' : 'e48b921463def14b0163f9b1edc7065e',
        'flag' : 1
    }
    if num == 0:
        data['pageNum'] = 1
    url = 'http://sbgg.saic.gov.cn:9080/tmann/annInfoView/imageView.html?'
    param = urlencode(data)
    allUrl = url + param
    response = requests.get(allUrl,headers = myHearder)
    global imageListData
    if response.status_code == 200:
        print(response.text)
        result = json.loads(response.text)
        l1 = result['imaglist']
        imageListData = imageListData + l1
    else:
        print('Flase')
    pass


def filterAll_FileDatas():
    datas = []
    with open('AllDataNew.json', 'r') as f:
        str = f.read()
        datas = json.loads(str)

    list2 = list(set(datas))
    list2.sort(key=datas.index)

    jsonStr = json.dumps(list2)
    with open('AllDataFilter.json', 'a') as wr:
        str2 = wr.write(jsonStr)

    print('结束')


def saveAllDataJson():
    for i in range(0, 190):
        req_imageInterface(i)
    jsonStr = json.dumps(imageListData)
    with open('AllDataNew.json', 'a') as  f:
        f.write(jsonStr)
    print('结束')


def downImages():
    dowDatas = []
    with open('AllDataNew.json', 'r') as downF:
        downStr = downF.read()
        dowDatas = json.loads(downStr)

    for i, val in enumerate(dowDatas):
        ir = requests.get(val,headers = myHearder)
        if ir.status_code == 200:
            fileName = '/Users/raohao/Desktop/sbggImages/' + str(i+1) + '.jpg'
            sz = open(fileName, 'wb').write(ir.content)
            print('下载成功')
        else:
            print('下载失败')


def main():
    saveAllDataJson()
    filterAll_FileDatas()
    # downImages()


if __name__ == '__main__':
    main()







