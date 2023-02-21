import json
import pandas as pd
from pandas.io.excel import ExcelWriter
import os
import re

def clear_st(st):
    if 'corrupted' in st:
        return st
    regex = re.compile('[a-z,&,\s]')
    b = re.findall(regex, st)
    n = ''.join(b)
    return n

def form_database():
    with open(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\data.json') as f:
        data = json.load(f)
    bronx = pd.DataFrame()
    kh = 0
    staten = pd.DataFrame()
    manhattan = pd.DataFrame()
    brooklyn = pd.DataFrame()
    queens = pd.DataFrame()
    dat = ['bronx', 'queens', 'brooklyn', 'manhattan', 'staten']
    lis_pad = [bronx, queens, brooklyn, manhattan, staten]
    for key in list(data.keys()):
        inter = pd.DataFrame()
        for da in dat:
            if da in key.lower():
                col = key.lower().replace(da, '')
                res = []
                for b in list(data[key].keys()):
                    res = res + data[key][b]['text']
                if len(res) == 0:
                    res=['empty']
                inter['ind'] = res
                inter['ind'] = inter['ind'].str.strip().str.lower()
                clear = lambda x: clear_st(x)
                inter['ind'] = inter['ind'].apply(clear)
                inter[col] = 1
                inter = inter.set_index(['ind'])
                ind = dat.index(da)
                lis_pad[ind] = lis_pad[ind].join(inter, how='outer')
    i = 0
    with ExcelWriter(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\database.xlsx',
                     mode="a" if os.path.exists(r'C:\Users\Миша\PycharmProjects\pythonProject4\database\database.xlsx')
                     else "w", if_sheet_exists = 'replace') as writer:
        for lis in lis_pad:
            print(dat[i])
            lis = lis.fillna(0)
            lis.to_excel(writer, sheet_name=dat[i])
            i+=1