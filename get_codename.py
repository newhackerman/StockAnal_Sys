# -*- coding: utf-8 -*-
import pandas as pd
allstockinfo=pd.read_csv(u'./data/ALL_STOCK_LIST.csv',sep=',',encoding='utf8')
codename=dict(zip(allstockinfo['code'].to_list(),allstockinfo['name'].to_list()))#提取个股代码与名称
def get_codename(data, *kwords):
    if data is None:
        return None
    if len(kwords) > 0:  # 指定是找名称或代码
        retname = kwords[0]
        retdata = ''
        if retname == 'name':
            for key,value in codename.items():
                if data ==key or data == value:
                    retdata = value
                    return retdata
        if retname == 'code':
            for key, value in codename.items():
                if data == key or data == value:
                    retdata = key
                    return retdata
        return retdata
    stockcode = ''
    for key, value in codename.items():
        if data == key or data == value:
            stockcode = key
            return stockcode
    if stockcode == '':
        return None
    else:
        return stockcode
if __name__ == '__main__':
    print(get_codename('长电科技','code'))
    print(get_codename('00981', 'name'))

