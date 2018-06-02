# this module will routinely fetch all urls for scraping ensuring only unique id's are found and
# filtering out non actionable urls
from lxml import html
from time import sleep
import requests
import threading
import datetime
import os
import sqlite3
import Log

class FetchHandler:

    def __init__(self,timeout,database,tablename):

        self.timeout = timeout
        self.currentTimeout = timeout
        self.sleepTimeout = 60*10

        self.terminated = False

        self.database = database

        self.tablename = tablename

        self.addr = "https://pastebin.com"


    def isTerminated(self):
        return self.terminated

    def terminate(self):
        Log.Log(3,"Fetch Handler Terminated...")
        self.terminated = True

    # this method will fetch a connection to the database
    def dbConn(self):
        return sqlite3.connect(self.database)


    def fetch(self):

        # looping while thread has not been terminated
        while not self.isTerminated() :

            # fetching links from archive page
            self.storeLinks(self.fetchLinks())
            self.progress()

            # output current list of links in database
            # self.ouputLinks()

            # sleep loop to avoid unintentional DOSing
            sleep(self.currentTimeout)



    # inital fetch
    def fetchLinks(self):

        Log.Log(1,"Fetching Archive List.")

        # request header properties like (user agent) text
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }

        # html request for given page
        page = requests.get(self.addr+'/archive',headers=headers)

        # storing node tree from html request
        tree = html.fromstring(page.content)

        # performing api block check
        if(self.checkLimit(tree)):
            Log.Log(2,"API Request Limit Hit!")
            self.currentTimeout = self.sleepTimeout
            return []
        else :
            self.currentTimeout = self.timeout
            Log.Log(1,"Archive Fetch Successful")

        # html fetching specific component of node tree
        pasteLink = tree.xpath('//*[@class="maintable"]/tr/td/a[1]/@href')

        # removing all non useful id's
        pasteLink = self.sanitise(pasteLink)

        # returning paste bin archive
        return pasteLink

    def storeLinks(self,links):

        # fetching database instance
        db = self.dbConn()

        # fetching database cursor object
        c  = db.cursor()

        # counter to track duplicates
        unique = 0

        # iteraing over fetched link
        for link in links:
            # see if exists
            c.execute('SELECT count(link) FROM '+self.tablename+' WHERE link="'+link+'" ')

            # if not insert
            if( c.fetchone()[0] == 0 ):
                # inserting unique link into table
                c.execute('INSERT INTO '+self.tablename+'(link,complete) VALUES (?,?) ',(link,0))
                unique+=1

        # outputting effort
        if(unique > 0):
            Log.Log(4,"Successfully Stored : " + str(unique) + " New Link/s...")

        if(len(links)-unique > 0):
            Log.Log(2,"Found : " + str(len(links)-unique) + " Duplicate Link/s...")


        db.commit()

        db.close()

        return

    def ouputLinks(self):

        # fetching database instance
        db = self.dbConn()

        # fetching database cursor object
        c  = db.cursor()

        # fetch all paste link table content
        c.execute('SELECT * FROM '+self.tablename+' ')

        index = 0

        for row in c:
            print(' %-5d:  Link: %-10s Completed: %-7s ' % (index,row[0],row[5]) )
            index+=1

        # commiting changes
        db.commit()

        # closing database interaction
        db.close()

    def progress(self):
        db = self.dbConn()
        c  = db.cursor()

        incomplete = c.execute('SELECT COUNT(link) FROM '+self.tablename+' WHERE complete=0').fetchone()[0]
        complete   = c.execute('SELECT COUNT(link) FROM '+self.tablename+' WHERE complete=1').fetchone()[0]

        db.commit()
        db.close()

        Log.Log(1,"Summary - Total : %-5d Complete : %-5d Incomplete : %-5d" % (incomplete+complete,complete,incomplete))


    # checking for api request block
    def checkLimit(self,tree):
        return (len(tree.xpath('//*[@id="error"]')) > 0) or (tree.xpath('/html/head/title/text()')[0] == 'Pastebin.com - Access Denied Warning')

    # this method will strip all non actionable id's ( those which link to further lists )
    # then will further strip of the initial slash
    def sanitise(self,collection):
        return [x[1:] for x in collection if x.count('/') == 1]

    def insert(self):
        return
