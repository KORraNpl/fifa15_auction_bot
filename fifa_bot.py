# coding=utf-8
import fut
import time
import random

user = ''		# your username
password = ''	# your password
answer = ''		# your answer for secret question
platform = ''	# pc/ps3/xbox360
code = ''		# your verification code that you get when logging in for the first time from new device

waitMin = 300	# minimum time in s before refreshing data (too frequent refreshes results in logging out)
waitMax = 500	# maximum time in s before refreshing data

ffut = fut.Core(user, password, answer, platform, code) # creating object

tradepile_size = ffut.tradepile_size
watchlist_size = ffut.watchlist_size


def message(msg="Ping."): # default function for printing out current watchlist status and amount of coins
    if msg == "Ping.":
        msg = msg + "\tWatchlist: " + str(len(ffut.watchlist())) + "\tCoins: " + str(ffut.credits)
    print time.strftime("%Y-%m-%d %H:%M:%S ") + msg


def cleartradepile(): # function for clearing tradepile if any player is sold
    items = ffut.tradepile()
    for item in items:
        if item['tradeState'] == u'closed': 
            ffut.tradepileDelete(item['tradeId'])
            #message("Player sold for %i, card removed." % item['currentBid'])


def clearwatchlist(): # function for managing watchlist
    items = ffut.watchlist()
    free_slots = tradepile_size - len(ffut.tradepile())
    for item in items:
        if item['tradeState'] == u'closed' and item['bidState'] == u'highest' and free_slots > 0:
            ffut.sendToTradepile(item['tradeId'], item['id'])
            #message("Player moved to trade pile.")
            free_slots -= 1
        elif item['tradeState'] == u'closed' and item['bidState'] == u'outbid':
            ffut.watchlistDelete(item['tradeId'])
            #message("Outbid player removed from watch list.")


def relisttradepile(): # function for re-listing auctions (expired or new)
    items = ffut.tradepile()
    for item in items:
        if item['tradeState'] == u'expired':
            ffut.sell(item['id'], item['startingBid'], item['buyNowPrice'], 3600)
            #message("Player put on transfer list for: %i." % int(item['startingBid']))
        elif item['tradeState'] is None:
            ffut.sell(item['id'], int(item['lastSalePrice']) + 100, int(item['lastSalePrice']) + 150)
            #message("New player put on transfer list for: %i." % (int(item['lastSalePrice']) + 100))


def buyplayers(): # function for buying new players, WIP
    items = ffut.searchAuctions('player', 'silver', max_price=150)
    for item in items:
        free_slots = watchlist_size - len(ffut.watchlist_size)
        if (item['rating'] >= 78) and (item['currentBid'] == 0) and (free_slots > 0) and (ffut.credits >= 150):
            fut.bid(item['tradeId'], 150)
            message("Bid for player.")


while True:
    wait = random.randint(waitMin, waitMax)

    try:
        cleartradepile()
        clearwatchlist()
        #buyplayers()
        relisttradepile()
        message()
        time.sleep(wait)
        ffut.keepalive()
    except fut.exceptions.InternalServerError:
        message("InternalServerError")
        time.sleep(10)
