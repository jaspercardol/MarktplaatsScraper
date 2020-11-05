from NotificationService import NotificationService
from Scraper import Scraper
from FileWatcher import FileWatcher
import time
import json

import sys
import getopt

def main(args):
    CONFIG = getCommandLineConfig(args)
    print("_________________________________")
    print("     Marktplaats Scraper ")
    print(" ")
    print(" by jaspercardol")
    print("_________________________________")
    print(" ")
    print("Configuration:")
    print("Scanning interval: {}".format(CONFIG['scanning_interval']))
    print("Pushover API Token: {}".format(CONFIG['pushover_api_token']))
    print("Pushover User Key: {}".format(CONFIG['pushover_user_key']))
    print(" ")
    notifier = NotificationService(CONFIG['pushover_api_token'],CONFIG['pushover_user_key'])
    fileWatcher = FileWatcher()
    print("Initial file scan found {} queries.".format(len(fileWatcher.getFiles())))
    scraper = Scraper(CONFIG['webdriverpath'])
    try:
        while True:
            files = fileWatcher.getFiles()
            for file in files:
                query = files[file]['query']
                filepath = files[file]['listing_filepath']
                check_for_updates(filepath,query,scraper, notifier)
            time.sleep(CONFIG['scanning_interval'])
    except KeyboardInterrupt:
        exit()
def getConfig():
    with open('config.json',"r") as json_file:
        config = json.load(json_file)
        json_file.close()
    return config

def getCommandLineConfig(argv):
    CONFIG = {}
    try:
        opts, args = getopt.getopt(argv,'a:u:i:w:')
    except getop.GetoptError:
        print("Opt error!")   
    for opt, arg in opts:
        print(arg)
        if "a" in opt:
            CONFIG['pushover_api_token'] = arg
        if "u" in opt:
            CONFIG['pushover_user_key'] = arg
        if "i" in opt:
            CONFIG['scanning_interval'] = int(arg)
        if "w" in opt:
            CONFIG['webdriverpath'] = arg
    return CONFIG

def check_for_updates(filename, url, scraper, notifier):
    listings = scraper.Scrape(url)
    new_listings = scraper.CompareListingsToSavedListings(listings,filename)
    print("Found {} new listings for {}".format(len(new_listings),filename))
    for new_listing in new_listings:
        data = new_listings[new_listing]
        title = 'New listing found: ' + data['title']
        message = data['description'] + "(" + data['price'] + ")"
        link = data['url']
        link_title = 'Open in browser'
        notifier.Notify(title,message,link,link_title)
        print(data['title'] + ': Notification sent through Pushover')
        print('Link: ' + data['url'])
        print(' ')
    scraper.SaveListings(listings, filename)

if __name__ == "__main__":
   main(sys.argv[1:])
