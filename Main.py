# this module will essentially kick off both threads responsible for properly scraping pastebin
import os
from time import sleep
from lxml import html
import requests
import sqlite3
import threading
import Fetch
import Scrape
import atexit
import KeyCheck
import Log

# constants for file and database interactivity
DATABASE_PATH = 'Database/'
DATABASE_NAME = 'master'
DATABASE_TABLE_NAME = 'tblPastes'
SCRAPE_PATH = 'Scrape/'


# database object
db = None

# this method will fetch a connection to the database
def dbConn():
    return sqlite3.connect(DATABASE_PATH+DATABASE_NAME)


def databaseTest():

    db = dbConn()
    c  = db.cursor()

    c.execute('''
        INSERT INTO '''+DATABASE_TABLE_NAME+'''
        (link,title,type,createDate,fetchDate,complete)
        VALUES (?,?,?,?,?,?)''',
        ("000000","TestTitle","TestType","TestDate","0000-00-00 00:00:00",False)
    )

    c.execute('''SELECT * FROM tblPastes''')

    rows = c.fetchall()

    for row in rows:
        print('{0},{1},{2},{3},{4},{5}'.format(row[0],row[1],row[2],row[3],row[4],row[5]))

    db.commit()

    db.close()

    return

# this method will ensure the database for scraping exists
def databaseSetup():

    Log.Log(3,"Checking Database ...")

    # Creates or opens a file called mydb with a SQLite3 DB
    db = sqlite3.connect(DATABASE_PATH+DATABASE_NAME)

    # Get a cursor object
    cursor = db.cursor()

    # creating unique ID table
    cursor.execute(''' CREATE TABLE IF NOT EXISTS '''+DATABASE_TABLE_NAME+''' (
            link TEXT NOT NULL,
            title TEXT,
            type TEXT,
            createDate TEXT,
            fetchDate DATETIME,
            complete BOOLEAN,
            content TEXT,
            UNIQUE(link)
        )''')

    # commits changes
    db.commit()

    # closing connection
    db.close()

    Log.Log(4,"Database Connection Successful...")

    return

# this method will ensure all folders are set up correctly
def folderSetup():
    # checking if folder exists for both database storage and scrape entries
    # and if not it will create it
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(SCRAPE_PATH),  exist_ok=True)

    # with open('Scrapes/'+fname, 'a') as f:
    #     f.write(str(content))

def launchFetchHandler(timeout):
    # object responsible for routine scraping of pastebin ID's
    fileHandler = Fetch.FetchHandler(timeout,DATABASE_PATH+DATABASE_NAME,DATABASE_TABLE_NAME)

    # launching fetch handler thread object
    fetchThread = threading.Thread(target = fileHandler.fetch, args = ())
    fetchThread.start()

    return fileHandler

def launchScrapeHandler(timeout):

    scrapeHandler = Scrape.ScrapeHandler(timeout,DATABASE_PATH+DATABASE_NAME,DATABASE_TABLE_NAME,SCRAPE_PATH)

    # launching fetch handler thread object
    scrapeHandler = threading.Thread(target = scrapeHandler.fetch, args = ())
    scrapeHandler.start()

    return scrapeHandler

def checkAccess():

    # request header properties like (user agent) text
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    }

    # html request for given page
    page = requests.get('https://www.pastebin.com/',headers=headers)

    # storing node tree from html request
    tree = html.fromstring(page.content)

    access = (len(tree.xpath('//*[@id="error"]')) > 0) or (tree.xpath('/html/head/title/text()')[0] == 'Pastebin.com - Access Denied Warning')

    if(access):
        Log.Log(2," Access Denied - IP Block...");
        Log.Log(1,"Page : ")
        Log.Log(1,page.content)


    return access


# method invoked on program termination request
def exit_handler():
    if( fh is not None) : fh.terminate()
    if( sh is not None) : sh.terminate()

    Log.Log(4,"Closing Scraper...")

# references to fetch and scrape handlers ( running in other threads )
fh = None
sh = None

exited = False

def main():

    # setting up folder environment
    folderSetup()
    # setting up databsae connectivity
    databaseSetup()

    # performing initial scrape access check
    while(checkAccess()):
        Log.Log(2,"Sleeping 10 Minutes...")
        sleep(60*10)

    # creating fetch handler
    fh = launchFetchHandler(60)

    # creating scrape handler
    sh = launchScrapeHandler(0.8)

    while not exited:
        k = KeyCheck.getkey().decode()
        Log.Log(1,"Key Pressed - "+k)


if __name__ == "__main__":
    main()

atexit.register(exit_handler)
