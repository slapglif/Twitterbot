import time
import tweepy
from datetime import datetime, timedelta

#
#   CONFIG
#

keywords = [ 'giveaway']
target='fazeclan'



consumer_key='xxxx'.encode('utf-8')
consumer_secret='xxxx'.encode('utf-8')
access_token_key='xxxx-xxxx'.encode('utf-8')
access_token_secret='xxxx'.encode('utf-8')



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

def is_valid_user(id, user):
    if (len(user.description) < 5):
        print('\tIgnored, len(desc) < 5')
        return False

    if (user.followers_count < 20):
        print('\tIgnored, (followers_count=' + str(user.followers_count) + ') < 20')
        return False

    return True

#
#   MAIN PROGRAM
#

def _(callback, fail):
    result = None
    while True:
        try:
            result = callback()
            time.sleep(5)
            break
        except:
            print(fail)
            time.sleep(10)
    return result

_DIE_ = False

for page in tweepy.Cursor(api.followers_ids, screen_name=target).pages():
    time.sleep(5)

    for id in page:
        print('Getting information for user ' + str(id))
        user = _(lambda: api.get_user(id), 'Failed to get info')

        if (is_valid_user(id, user)):
            print('Getting time line for user ' + str(id))
            try:
                timeline = api.user_timeline(user_id=id) # pull their timeline
                rtw = 0
            except:
                print('Unauthorized to view this users time line, skipping')
                continue

            for tweet in timeline:
                for kw in keywords:
                    
                    if kw in tweet.text: 
                        try:
                            api.retweet(tweet.id)
                            print('Retweeted message id ' + str(tweet.id) + ' from user ' + str(id))
                            rtw = rtw + 1
                        except:
                            print('Already retweeted message id ' + str(tweet.id) + ', skipping')
                            rtw = -1
                        time.sleep(5)
                        break # dont check anymore keywords

                if (rtw >= 2 or rtw < 0):
                    break # dont retweet anymore from this user

            if (rtw > 0):
                me = api.me()
                time.sleep(5)

                print('Following primary user ' + str(id))
                _(lambda: api.create_friendship(id), 'Failed to follow user')

                their_followers = _(lambda: api.followers_ids(id), 'Failed to get follower ids')
                for j in range(20):
                    print('Following user ' + str(their_followers[j]) + ' from user ' + str(id))
                    if (me.id != their_followers[j]):
                        _(lambda: api.create_friendship(their_followers[j]), 'Failed to follow user (2)')
                
                check_time = datetime.utcnow() + timedelta(minutes=30)
                while True:
                    me2 = _(lambda: api.me(), 'Failed to get information about self')
                    now_time = datetime.utcnow()

                    if (me2.followers_count > 4250):
                        _DIE_ = True
                        break

                    if (check_time <= now_time):
                        break

                    time_delta = check_time - now_time
                    mins_left = time_delta.total_seconds() / 60.0

                    print('Waiting for follower change... mins left: ' + str(mins_left))
                    time.sleep(5)
                    if (me2.followers_count != me.followers_count):
                       break

            if (_DIE_):
                break

    if (_DIE_):
        break

    print('Sleeping 60s for next page worth fo data...')
    time.sleep(60)
