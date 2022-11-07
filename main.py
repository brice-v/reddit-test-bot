import time

import praw

import youtube
import cache

VERSION = "v0.0.1"


class Bot:
    reddit: praw.Reddit

    def __init__(self, bot_name="test-bot", version=VERSION, user_agent=None):
        if not user_agent or user_agent is None:
            user_agent = f"{bot_name}/{version} by u/brice_v-dev-bot"

        self.reddit = praw.Reddit(bot_name, user_agent=user_agent, ratelimit_seconds=10)

    def login(self) -> None:
        """login will call reddit.user.me() which will force authentication and print out a message if successful"""
        print(f"Logged in as {self.reddit.user.me()}")
        time.sleep(2)

    def post_video_link_to_subreddit(
        self, video_title=None, video_link=None, subreddit=None
    ):
        if not video_title or video_title is None:
            raise Exception("video_title is None")
        if not video_link or video_link is None:
            raise Exception("video_link is None")
        if not subreddit or subreddit is None:
            raise Exception("subreddit is None")
        time.sleep(2)
        self.reddit.subreddit(subreddit).submit(video_title, url=video_link)


def main():
    subreddit_to_post_to = "naptownmusicscene"
    channel_ids = None
    cache_db = cache.DB()

    bot = Bot()
    bot.login()

    # This is where we can loop on every 24hrs or something
    with open("channel_ids.txt") as f:
        channel_ids = f.readlines()
        channel_ids = [x.replace("\r", "").replace("\n", "") for x in channel_ids]
    for channel_id in channel_ids:
        channel = youtube.Channel(channel_id=channel_id)
        channel_links = channel.get_all_videos(cache=cache_db)
        for title, link in channel_links:
            if not cache_db.is_posted_to_reddit(link):
                print(f"posting to '{subreddit_to_post_to}' title={title}, link={link}")
                # bot.post_video_link_to_subreddit(
                #     video_title=title, video_link=link, subreddit=subreddit_to_post_to
                # )
                # cache_db.add_to_posted_on_reddit(link)


def just_post_db_videos():
    subreddit_to_post_to = "naptownmusicscene"
    channel_ids = None
    cache_db = cache.DB()

    bot = Bot()
    bot.login()

    with open("channel_ids.txt") as f:
        channel_ids = f.readlines()
        channel_ids = [x.replace("\r", "").replace("\n", "") for x in channel_ids]
    for channel_id in channel_ids:
        channel_links = cache_db.get_all_videos_for_channel(channel_id=channel_id)
        for title, link in channel_links:
            if not cache_db.is_posted_to_reddit(link):
                time.sleep(1)
                print(f"posting to '{subreddit_to_post_to}' title={title}, link={link}")
                bot.post_video_link_to_subreddit(
                    video_title=title, video_link=link, subreddit=subreddit_to_post_to
                )
                cache_db.add_to_posted_on_reddit(link)


if __name__ == "__main__":
    just_post_db_videos()
