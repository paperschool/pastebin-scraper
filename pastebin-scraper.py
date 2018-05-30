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
    if(len(paste) == 1):
        Log(4,"Scrape ["+addr+link+"]...")
        return str(paste[0]).encode("utf-8")
    else :
        Log(2,"Scrape ["+addr+link+"]...")
        return str(addr+link)

def makeHeader(addr):
    header = "\n"
    header += "-"*20
    header += "\n"
    header += "Title   : Performing Request\n"
    header += "Time    : "+Now()+"\n"
    header += "Address : "+addr+"\n"
    return header

# method to perform a structued log
def Log(type,msg):

    if  (type == 1): typeStr = bcolors.OKBLUE  + "LOG"     + bcolors.ENDC
    elif(type == 2): typeStr = bcolors.FAIL    + "ERROR"   + bcolors.ENDC
    elif(type == 3): typeStr = bcolors.WARNING + "WARNING" + bcolors.ENDC
    elif(type == 4): typeStr = bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC
    else :           typeStr = bcolors.OKBLUE  + "LOG"     + bcolors.ENDC

    print("[\033[92m %s \033[0m] : %-7s : %s" % (Now(),typeStr,msg))


def Save(filename,content):
    with open(filename, 'a') as f:
        f.write(str(content))

def Now():
    return datetime.datetime.now().strftime('%d-%m-%Y:%H-%M-%S')

def NowString():
    return datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')

def Sleep(time,msg=None):
    if(msg) : Log(1,msg)
    else    : Log(1,bcolors.OKGREEN+"Sleeping : "+str(time)+"s"+ bcolors.ENDC)
    sleep(time)

def init():

    # file name for save data
    filename = "Scrape-"+NowString()+".txt"

    Save(filename,"Starting Scrape : "+Now()+"\n")

    # list of archive page links
    archivelinks = fetchLinks(addr)

    if(len(archivelinks) == 0): Save(filename,"Scrape Failed : API Limit Hit ")

    for i in range(len(archivelinks)):
        Save(filename," %-3s : id : %s \n" % (str(i),archivelinks[i]))

    # list of scraped text
    scrapes = []

    if(len(archivelinks) > 0):
        for i in archivelinks:

            Sleep(2+random.uniform(0.1,0.5))

            Save(filename,makeHeader(addr+i))

            scrape = fetchPaste(addr,i)

            Save(filename,scrape)

            scrapes.append(scrape);


init()
