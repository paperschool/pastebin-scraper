from lxml import html
from time import sleep
import os
import datetime
import requests
import random


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class timeout:
    SECOND = 1
    HALFSECOND = 0.5
    TENTHSECOND = 0.01
    HUNDRETHSECOND = 0.001

# webaddress
addr = "https://pastebin.com"

# request header properties like (user agent) text
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

# default file name for save data
filename = ""

# inital fetch
def fetchLinks(addr):

    Log(1,"Fetching Archive List.")


    # html request for given page
    page = requests.get(addr+'/archive',headers=headers)

    # storing node tree from html request
    tree = html.fromstring(page.content)

    # performing api block check
    if(checkLimit(tree)):
        Log(2,"API Request Limit Hit!")
        return []
    else :
        Log(1,"Archive Fetch Successful")

    # html fetching specific component of node tree
    pasteLink = tree.xpath('//*[@class="maintable"]/tr/td/a[1]/@href')

    # returning paste bin archive
    return pasteLink

# checking for api request block
def checkLimit(tree):
    return len(tree.xpath('//*[@id="error"]')) > 0

# performing fetch for specific paste
def fetchPaste(addr,link):

    # html request for given paste page
    req = requests.get(addr+link,headers=headers)

    # fetching node tree for paste
    tree = html.fromstring(req.content)

    # fetching content of paste from "raw-text" area
    paste = tree.xpath('//*[@id="paste_code"]/text()')

    # validating return and returning
    if(len(paste) == 0):
        Log(2,"Scrape ["+addr+link+"]...")
        return str(addr+link)

    # logging successful scrape
    Log(4,"Scrape ["+addr+link+"]...")

    # fetching title of paste
    title = tree.xpath('//*[@id="content_left"]/div[2]/div[3]/div[1]/h1/text()')[0]

    # fetching type of paste
    pasteType = tree.xpath('//*[@id="code_buttons"]/span[2]/a/text()')[0]

    # fetching date of paste
    date = tree.xpath('//*[@id="content_left"]/div[2]/div[3]/div[2]/span/text()')[0]

    # saving new header and newly scraped content to composite file
    Save(filename,makeHeader(title,date,pasteType,addr+link,link))
    Save(filename,str(paste[0]).encode("utf-8"))

    # returning content string
    return str(paste[0]).encode("utf-8")

# building text header for scraped content
def makeHeader(name,date,pasteType,addr,id):
    header = "\n"
    header += "-"*20
    header += "\n"
    header += "Title      : "+name+"\n"
    header += "Date       : "+date+"\n"
    header += "Fetch Time : "+Now()+"\n"
    header += "Address    : "+addr+"\n"
    header += "ID         : "+id+"\n"
    header += "Type       : "+pasteType+"\n"
    return header

# method to perform a structued log
def Log(type,msg):
    # type checking for output and coloration
    if  (type == 1):
        typeStr = "LOG"
        typeCol = bcolors.OKBLUE
    elif(type == 2):
        typeStr = "ERROR"
        typeCol = bcolors.FAIL
    elif(type == 3):
        typeStr = "WARNING"
        typeCol = bcolors.WARNING
    elif(type == 4):
        typeStr = "SUCCESS"
        typeCol = bcolors.OKGREEN
    else :
        typeStr = "LOG"
        typeCol = bcolors.OKBLUE

    # printing lof to terminal
    print("[\033[92m %s \033[0m]  %s%-7s%s : %s" % (Now(),typeCol,typeStr,bcolors.ENDC,msg))

# appending content to file
def Save(fname,content):
    with open(fname, 'a') as f:
        f.write(str(content))

# Timenow string
def Now():
    return datetime.datetime.now().strftime('%d-%m-%Y:%H-%M-%S')

# Time now string filename safe
def NowString():
    return datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

# thread sleep function including sleep
def Sleep(time,msg=None):
    if(msg) : Log(1,msg)
    else    : Log(1,bcolors.OKGREEN+"Sleeping : "+str(time)+"s"+ bcolors.ENDC)
    sleep(time)

# file name for save data
filename = "Scrape-"+NowString()+".txt"

def init():

    Save(filename,"Starting Scrape : "+Now()+"\n")

    # list of archive page links
    archivelinks = fetchLinks(addr)

    # checking pastebin list of id's
    if(len(archivelinks) == 0):
        Save(filename,"Scrape Failed : API Limit Hit ")
        return

    # appending id's individually to file as list
    for i in range(len(archivelinks)):
        Save(filename," %-3s : id : %s \n" % (str(i),archivelinks[i]))

    # list of scraped text
    scrapes = []

    # iterating over pastebin links
    for i in archivelinks:
        # sleeping before attempting next fetch
        Sleep(2+random.uniform(0.1,0.5))
        # attempting sub fetch on scraped id
        scrape = fetchPaste(addr,i)
        # storing scrape content inside array
        scrapes.append(scrape);

init()
