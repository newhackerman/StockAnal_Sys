# -*- coding: utf-8 -*-
import requests as req
import pandas as pd
import time
import concurrent.futures

#从腾讯获取港股日线
def getHK_kline(stockcode, days=500):
    pddata = pd.DataFrame()
    datalist = []
    result = ''
    if str(stockcode).strip() == '' or str(stockcode).isalpha():
        return None
    market = 'hk'
    lastday = tradeday.getlastTradeday()
    beginday = tradeday.getlastNtradeday(days)
    '''
    // 1. https://web.ifzq.gtimg.cn/appstock/app/fqkline/get 固定访问链接
    // 2. param=代码,日k，开始日期，结束日期，获取多少个交易日，前复权
    // 	2.1 usAAPL.OQ 股票代码，这里是us是美股，AAPL是苹果，“.OQ”是美股拼接后缀，其他不需要拼接
    // 	2.2. 500代表获取多少个交易日，500实际查出来的是501条数据，多一条
    // 	2.3. qfq前复权
    // 美股，苹果【usAAPL】，需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=usAAPL.OQ,day,2020-3-1,2021-3-1,500,qfq
    // 上海，茅台【sh600519】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh600519,day,2020-3-1,2021-3-1,500,qfq
    // 港股，小米【hk01810】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk01810,day,2020-3-1,2021-3-1,500,qfq
    '''
    # url = f'https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?param={market}{stockcode},day,,,{days},qfq'
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stockcode},day,{beginday},{lastday},{days},qfq'
    # print(url)
    try:
        result = req.get(url)
        # print(result.json())
    except BaseException as b:
        print(f'从腾讯获取{stockcode}日线数据异常', b)
        return None
    # print(result.json())
    try:
        result = result.json()['data'][str(market) + str(stockcode)]['day']
        # print(result)
    except BaseException as c:
        try:
            result = result.json()['data'][str(market) + str(stockcode)]['qfqday']
        except BaseException as d:
            return None
    try:
        for data in result:
            tmpdict = {'date': data[0],
                       'open': data[1],
                       'close': data[2],
                       'high': data[3],
                       'low': data[4],
                       'vol': int(str(data[5]).split('.')[0])
                       # 'Vol': int(str(data[8]).split('.')[0])
                       }
            datalist.append(tmpdict)
        pddata = pd.DataFrame(datalist)
        if pddata.empty:
            return pddata
        try:
            pddata['close'] = pddata['close'].astype(float)
        except ValueError as e:
            print(f"无法将 'close' 列转换为浮点数: {e}")
            return pddata

            # 计算涨跌幅
        pddata['zdf'] = pddata['close'].pct_change() * 100
        pddata['zdf'] = pddata['zdf'].round(2)
        pddata.fillna(0, inplace=True)
    except BaseException as b:
        print('解释从腾讯获取的日线数据出错', b)
    return pddata
#从腾讯取A股数据 （无成交额）
def getA_kline(stockcode, days=500,**kwargs):
    pddata = pd.DataFrame()
    datalist = []
    result = ''
    stockdf = pd.DataFrame()
    stockquotelist = []
    if len(stockcode) < 6:
        stockcode = stockcode.rjust(6, '0')
    market = 'sz'
    if stockcode[0:2] == '60' or stockcode[0:2] == '68':
        market = 'sh'
    elif stockcode[0:2] == '00' or stockcode[0:2] == '30':
        market = 'sz'
    elif  stockcode[0:] == '4' or stockcode[0:1] == '8':
        market = 'bj'
    if kwargs:
        for k,v in kwargs.items():
            if k==market:
                if v==str(0):
                    market='sz'
                elif v==str(1):
                    market=='sh'
    lastday = tradeday.getlastTradeday()
    beginday = tradeday.getlastNtradeday(days)
    '''
    // 1. https://web.ifzq.gtimg.cn/appstock/app/fqkline/get 固定访问链接
    // 2. param=代码,日k，开始日期，结束日期，获取多少个交易日，前复权
    // 	2.1 usAAPL.OQ 股票代码，这里是us是美股，AAPL是苹果，“.OQ”是美股拼接后缀，其他不需要拼接
    // 	2.2. 500代表获取多少个交易日，500实际查出来的是501条数据，多一条
    // 	2.3. qfq前复权
    // 美股，苹果【usAAPL】，需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=usAAPL.OQ,day,2020-3-1,2021-3-1,500,qfq
    // 上海，茅台【sh600519】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh600519,day,2020-3-1,2021-3-1,500,qfq
    // 港股，小米【hk01810】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk01810,day,2020-3-1,2021-3-1,500,qfq
    '''
    # url = f'https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?param={market}{stockcode},day,,,{days},qfq'
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stockcode},day,{beginday},{lastday},{days},qfq'
    # print(url)
    try:
        result = req.get(url)
        # print(result.json())
    except BaseException as b:
        print(f'从腾讯获取{stockcode}日线数据异常', b)
        return pd.DataFrame()
    try:
        result = result.json()['data'][str(market) + str(stockcode)]['day']
    except BaseException as c:
        try:
            result = result.json()['data'][str(market) + str(stockcode)]['qfqday']
        except BaseException as d:
            return pd.DataFrame()
    try:
        for data in result:
            tmpdict = {'date': data[0],
                       'open': data[1],
                       'close': data[2],
                       'high': data[3],
                       'low': data[4],
                       'vol': int(str(data[5]).split('.')[0])
                       # 'Vol': int(str(data[8]).split('.')[0])
                       }
            datalist.append(tmpdict)
        pddata = pd.DataFrame(datalist)
        if pddata.empty:
            return pddata
        try:
            pddata['close'] = pddata['close'].astype(float)
            pddata['vol'] = pddata['vol'].astype(int)
        except ValueError as e:
            print(f"无法将 'close' 列转换为浮点数: {e}")
            return pddata

            # 计算涨跌幅
        pddata['zdf'] = pddata['close'].pct_change() * 100
        pddata['zdf'] = pddata['zdf'].round(2)

        pddata.fillna(0, inplace=True)
    except BaseException as b:
        print('解释从腾讯获取的日线数据出错', b)
    return pddata
#从腾讯取USA股数据
def getUSA_kline(stockcode, days=500):
    pddata = pd.DataFrame()
    datalist = []
    result = ''
    if stockcode is None or str(stockcode).strip() == '':
        return None
    market = 'us'
    lastday = tradeday.getlastTradeday()

    day1 = str(int(lastday[8:]) + 1)
    # print(day1)
    lastday = str(lastday[0:8]) + day1
    beginday = tradeday.getlastNtradeday(days)
    '''
    // 1. https://web.ifzq.gtimg.cn/appstock/app/fqkline/get 固定访问链接
    // 2. param=代码,日k，开始日期，结束日期，获取多少个交易日，前复权
    // 	2.1 usAAPL.OQ 股票代码，这里是us是美股，AAPL是苹果，“.OQ”是美股拼接后缀，其他不需要拼接
    // 	2.2. 500代表获取多少个交易日，500实际查出来的是501条数据，多一条
    // 	2.3. qfq前复权
    // 美股，苹果【usAAPL】，需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=usAAPL.OQ,day,2020-3-1,2021-3-1,500,qfq
    // 上海，茅台【sh600519】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh600519,day,2020-3-1,2021-3-1,500,qfq
    // 港股，小米【hk01810】，不需要拼接“.OQ”
    https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=hk01810,day,2020-3-1,2021-3-1,500,qfq
    '''
    # url = f'https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get?param={market}{stockcode},day,,,{days},qfq'
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stockcode}.OQ,day,{beginday},{lastday},{days},qfq'
    print(url)
    try:
        result = req.get(url)
        # print(result.json())
    except BaseException as b:
        print(f'从腾讯获取{stockcode}日线数据异常', b)
        return pddata
    # print(result.json())
    try:
        result = result.json()['data'][str(market) + str(stockcode) + '.OQ']['day']
        # print(result)
    except BaseException as c:
        try:
            result = result.json()['data'][str(market) + str(stockcode)]['qfqday']
        except BaseException as d:
            return pddata
    try:
        for data in result:
            tmpdict = {'date': data[0],
                       'open': data[1],
                       'close': data[2],
                       'high': data[3],
                       'low': data[4],
                       'vol': int(str(data[5]).split('.')[0])
                       # 'Vol': int(str(data[8]).split('.')[0])
                       }
            datalist.append(tmpdict)
        pddata = pd.DataFrame(datalist)
        if pddata.empty:
            return pddata
        try:
            pddata['close'] = pddata['close'].astype(float)
        except ValueError as e:
            print(f"无法将 'close' 列转换为浮点数: {e}")
            return pddata

            # 计算涨跌幅
        pddata['zdf'] = pddata['close'].pct_change() * 100
        pddata['zdf'] = pddata['zdf'].round(2)
        pddata.fillna(0, inplace=True)
    except BaseException as b:
        print('解释从腾讯获取的日线数据出错', b)
    return pddata


if __name__ == '__main__':
    # client = quotes.Quotes.factory(market='std', multithread=True, heartbeat=True, timeout=15)
    # df=getm_kline('159526',550,market='0',period='240')
    # print( df)
    # print(df.columns)
    # insertallstockklinetoDB() #全量kline入库，一个月同步一次即可
    # todayklinetodb() #收盘后执行
    df = getUSA_kline('AAPL', 550)
    # df=get_stock_kline('688211',550)
    # df=get_stock_finance('688211')
    # liutongguben=df['liutongguben'].values[-1]
    # print(liutongguben)
    # print(df)
    # print(df.columns)
    # update_liutongguben()
   
    # print(df)
