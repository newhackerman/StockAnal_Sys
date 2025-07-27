# -*- coding: utf-8 -*-
import requests as req
import pandas as pd

def get_A_kline(stockcode):
    stockcode = str(stockcode)

    if len(stockcode) < 6:
        stockcode = stockcode.rjust(6, '0')
    stockdf = pd.DataFrame()
    stockquotelist = []
    market = 0
    if 'HK' in str(stockcode):
        market = 116
    else:
        if stockcode[0:2] == '60' or stockcode[0:2] == '68':
            market = 1
        else:
            market = 0
        # market=1
        # fqt=1 前复权 0，不复权
    response = None
    url =f'https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={market}.{stockcode}&ut=&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=550&_='
    # url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid={market}.{stockcode}&ut=&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt={nday}&_='
    try:
        response = req.get(url=url, timeout=5)
    except BaseException as b:
        count = 0
        while True:
            count = count + 1
            if count >= 3:
                break
            try:
                response = req.get(url=url, timeout=5)
                if response.status_code != 200:
                    continue
                else:
                    break
            except BaseException as c:
                continue
    if response is None:
        return pd.DataFrame()
    if response.status_code != 200:
        return pd.DataFrame()  # 后续需要用到定时任务，重试会导致线程超时，崩溃

    jsontext = response.json()['data']
    if jsontext is None:
        return pd.DataFrame()
    name = jsontext['name']
    jsontext = jsontext['klines']
    # print(jsontext)
    for data in jsontext:
        data = str(data).split(',')
        # acc_unit_nav = data['acc_unit_nav']#单位净值
        date = data[0]
        code = stockcode
        # name=name
        open = round(float(data[1]), 3)
        close = round(float(data[2]), 3)
        high = round(float(data[3]), 3)
        low = round(float(data[4]), 3)
        vol = round(float(data[5]), 0)  # 股
        amount = data[6]
        zdf = round(float(data[7]), 2)
        zf = round(float(data[8]), 2)  # 振幅
        chg = round(float(data[9]), 3)
        hsl = round(float(data[10]), 3)

        if vol == '-':
            vol = 0
            continue
        else:
            vol = vol
        if amount == '-':
            amount = 0
        else:
            amount = round(float(amount) / 100000000, 2)  # 成交额亿
        tmpdict = {
            'code': code,
            'name': name,
            'zdf': zdf,
            'close': close,
            'open': open,
            'low': low,
            'high': high,
            'chg': chg,
            'vol': vol,
            'hsl': hsl,
            'amount': amount,
            'date': date,
            'market': market,
        }
        # print(tmpdict)
        stockquotelist.append(tmpdict)
    # print(stockquotelist)

    stockdf = pd.DataFrame(stockquotelist)
    # print('取到的数据为：',stockqoutepd.head())
    if stockdf.empty:
        return pd.DataFrame()
    # columns = stockdf.columns
    # for column in columns:
    # stockdf[column][stockdf[column] == '-'] = 0  # 将-换成0
    stockdf.drop_duplicates(keep='first', inplace=True)
    stockdf.sort_values(by='date', ascending=True, inplace=True)
    return stockdf

def getHK_kline(stockcode, start_date=None, end_date=None):
    pddata = pd.DataFrame()
    datalist = []
    result = ''
    if str(stockcode).strip() == '' or str(stockcode).isalpha():
        return None
    market = 'hk'

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
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stockcode},day,{start_date},{end_date},550,qfq'
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

def getUSA_kline(stockcode, start_date=None, end_date=None):
    pddata = pd.DataFrame()
    datalist = []
    result = ''
    if stockcode is None or str(stockcode).strip() == '':
        return None
    market = 'us'
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
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{stockcode}.OQ,day,{start_date},{end_date},550,qfq'
    # print(url)
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

def get_quote(stockcode,start_date='2021-02-01', end_date='2025-05-12', market='A'):
    if market=='A':
        return get_A_kline(stockcode)
    elif market=='us':
        return getUSA_kline(stockcode,start_date=start_date, end_date=end_date)
    elif market=='hk':
        return getHK_kline(stockcode,start_date=start_date, end_date=end_date)
    else:
        return pd.dataFrame()
    return pd.dataFrame()

if __name__ == '__main__':
    # print(get_stock_kline('600059',550))
    # insertallstockklinetoDB() #全量kline入库，一个月同步一次即可
    # todayklinetodb() #收盘后执行
    # df =  get_quote('300159', market='A')
    df = get_quote('AAPL', start_date='2021-02-01', end_date='2025-05-12',market='us')
    # df=getHK_kline('00981',550)
    print(df)
