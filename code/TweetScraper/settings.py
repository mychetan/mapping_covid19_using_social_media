# -*- coding: utf-8 -*-

# !!! # Crawl responsibly by identifying yourself (and your website/e-mail) on the user-agent
USER_AGENT = 'p5'

# settings for spiders
BOT_NAME = 'TweetScraper'
LOG_LEVEL = 'INFO'
DOWNLOAD_HANDLERS = {'s3': None,} # from http://stackoverflow.com/a/31233576/2297751, TODO
DOWNLOAD_DELAY = 3
#CLOSESPIDER_PAGECOUNT = 30

SPIDER_MODULES = ['TweetScraper.spiders']
NEWSPIDER_MODULE = 'TweetScraper.spiders'
ITEM_PIPELINES = {
'TweetScraper.pipelines.SaveToFilePipeline':100,
#'TweetScraper.pipelines.SaveToMongoPipeline':100, # replace `SaveToFilePipeline` with this to use MongoDB
#'TweetScraper.pipelines.SavetoMySQLPipeline':100, # replace `SaveToFilePipeline` with this to use MySQL
}

# settings for where to save data on disk
SAVE_TWEET_PATH = './Data/tweets/'
SAVE_USER_PATH = './Data/users/'

# settings for mongodb
MONGODB_SERVER = "127.0.0.1"
MONGODB_PORT = 27017
MONGODB_DB = "TweetScraper"        # database name to save the crawled data
MONGODB_TWEET_COLLECTION = "tweet" # collection name to save tweets
MONGODB_USER_COLLECTION = "user"   # collection name to save users

#settings for mysql
MYSQL_SERVER = "ga-cc12-s5.database.windows.net"
MYSQL_DB     = "ga_p5"
MYSQL_TABLE  = "tweets" # the table will be created automatically
MYSQL_USER   = "ga"        # MySQL user to use (should have INSERT access granted to the Database/Table
MYSQL_PWD    = "ga_pass"        # MySQL user's password
