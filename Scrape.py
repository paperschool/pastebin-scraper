# this module will routinely fetch all urls for scraping ensuring only unique id's are found and
# filtering out non actionable urls
from lxml import html
from time import sleep
import requests
import threading
import datetime
import os
import random
import sqlite3
import Log

class ScrapeHandler:

    def __init__(self,timeout,database,tablename,filepath):

        self.timeout = timeout

        self.sleepTimeout = 60*5

        self.currentTimeout = timeout

        self.terminated = False

        self.database = database

        self.tablename = tablename

        self.addr = "https://pastebin.com"

        self.filepath = filepath

        self.filename = 'Scrape '+Log.NowString()

        self.filemax = 0


    def isTerminated(self):
        return self.terminated

    def terminate(self):
        Log.Log(3,"Scrape Handler Terminated...")
        self.terminated = True

    # this method will fetch a connection to the database
    def dbConn(self):
        return sqlite3.connect(self.database)


    def fetch(self):

        # looping while thread has not been terminated
        while not self.isTerminated() :

            # check whether actionable links are available in the database
            self.checkTimeout()

            # fetching actionable link and then scraping its contents, finally
            # storing to a database
            self.scrapeLink(self.selectLink())

            # checking size of file to stop over sized files
            self.checkFileSize()


            # sleep loop to avoid unintentional DOSing
            sleep(self.currentTimeout+random.uniform(0.0,0.3))

    def selectLink(self):

        # establishing database connection and fetching cursor
        db = self.dbConn()
        c = db.cursor()

        # fetching actionable link from database
        c.execute("SELECT * FROM "+self.tablename+" WHERE complete=0 LIMIT 1")

        try :
            # storing link
            link = str(c.fetchone()[0])
        except :
            Log.Log(2,"Link NoneType with - %s " % (c.fetchone()))
            link = None

        # tidying up database interaction
        db.commit()
        db.close()

        return link

    def removeLink(self,link):
        db = self.dbConn()
        c = db.cursor()
        c.execute('DELETE FROM '+self.tablename+' WHERE link=? ',(link,))
        db.commit()
        db.close()

    # this method is for moderating all aspects of the heartbeat, slowing when needed
    def checkTimeout(self):

        # this method counts the number of usable links setting the timeout appropriately
        if(self.countActionableLinks() == 0):
            Log.Log(3,"Completed All Links, Sleeping Till Available...")
            self.currentTimeout = self.sleepTimeout
        else:
            self.currentTimeout = self.timeout


    def countActionableLinks(self):
        db = self.dbConn()
        c = db.cursor()
        c.execute('SELECT COUNT(link) FROM '+self.tablename+' WHERE complete=? ',(0,))

        count = int(c.fetchone()[0])

        db.commit()
        db.close()

        return count


    def scrapeLink(self,link):

        if(not link): return

        # request header properties like (user agent) text
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

        # html request for given paste page
        req = requests.get(self.addr + "/" + link,headers=headers)

        # fetching node tree for paste
        tree = html.fromstring(req.content)

        if(self.checkLimit(tree)):
            self.currentTimeout = self.sleepTimeout
            Log.Log(2,"Paste Scrape Blocked, Sleeping : "+str(self.sleepTimeout)+"s...")
            return
        elif(self.checkRemoved(tree)):
            Log.Log(2,"Paste "+link+" Removed, Ignoring...")
            self.removeLink(link)
            return
        else:
            self.currentTimeout = self.timeout

        # fetching content of paste from "raw-text" area
        paste = tree.xpath('//*[@id="paste_code"]/text()')

        # validating return and returning
        if(len(paste) == 0):
            Log.Log(2,"Scrape ["+self.addr + "/" + link+"]...")
            return str(link)

        # logging successful scrape
        Log.Log(4,"Scrape ["+self.addr + "/" + link+"]...")

        # fetching title of paste
        title = tree.xpath('//*[@id="content_left"]/div[2]/div[3]/div[1]/h1/text()')[0]

        # fetching type of paste
        pasteType = tree.xpath('//*[@id="code_buttons"]/span[2]/a/text()')[0]

        # fetching date of paste
        date = tree.xpath('//*[@id="content_left"]/div[2]/div[3]/div[2]/span/text()')[0]

        db = self.dbConn()
        c = db.cursor()

        # storing scraped data to database
        c.execute(''' UPDATE '''+self.tablename+''' SET title=?, type=?, createDate=?, fetchDate=?, complete=?, content=? WHERE link=? ''',
            (str(title),
            str(type),
            str(date),
            Log.NowString(),
            1,
            str(paste),
            link)
        )

        # saving new header and newly scraped content to composite file
        self.Save(self.filename,self.makeHeader(str(title.encode("utf-8")),date,pasteType,self.addr + "/" + link,link))
        self.Save(self.filename,str(paste[0]).encode("utf-8"))

        db.commit()
        db.close()

    # appending content to file
    def Save(self,fname,content):

        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        with open(self.filepath+fname, 'a') as f:
            f.write(str(content))

    def checkFileSize(self):
        if(int(os.stat(self.filepath+self.filename).st_size) >= 6000000):
            self.filename = 'Scrape '+Log.NowString()
            with open(self.filepath+self.filename, 'a') as f:
                f.write(str(''))

    # checking for api request block
    def checkLimit(self,tree):
        return (len(tree.xpath('//*[@id="error"]')) > 0) or (tree.xpath('/html/head/title/text()')[0] == 'Pastebin.com - Access Denied Warning')

    def checkRemoved(self,tree):
        if(len(tree.xpath('//*[@id="notice"]/text()') > 0):
            return tree.xpath('//*[@id="notice"]/text()')[0] == 'This page is no longer available. It has either expired, been removed by its creator, or removed by one of the Pastebin staff.'
        else :
            Log.Log(4,"Scrape Failed...")
            return True

    # building text header for scraped content
    def makeHeader(self,name,date,pasteType,addr,id):
        header = "\n"
        header += "-"*20
        header += "\n"
        header += "Title      : "+name+"\n"
        header += "Date       : "+date+"\n"
        header += "Fetch Time : "+Log.Now()+"\n"
        header += "Address    : "+addr+"\n"
        header += "ID         : "+id+"\n"
        header += "Type       : "+pasteType+"\n"
        return header
