import time

import praw

import youtube
import cache

VERSION = "v0.0.2"


class Bot:
    reddit: praw.Reddit

    def __init__(self, bot_name="test-bot", version=VERSION, user_agent=None):
        if not user_agent or user_agent is None or user_agent == "":
            user_agent = f"{bot_name}/{version} by u/brice_v-dev-bot"

        self.reddit = praw.Reddit(bot_name, user_agent=user_agent, ratelimit_seconds=10)

    def login(self) -> None:
        """login will call reddit.user.me() which will force authentication and print out a message if successful"""
        print(f"Logged in as {self.reddit.user.me()}")
        time.sleep(2)

    def post_video_link_to_subreddit(
        self,
        video_title=None,
        video_link=None,
        subreddit=None,
    ):
        if not video_title or video_title is None or video_title == "":
            raise Exception("post_video_link_to_subreddit: video_title is None")
        if not video_link or video_link is None or video_link == "":
            raise Exception("post_video_link_to_subreddit: video_link is None")
        if not subreddit or subreddit is None or subreddit == "":
            raise Exception("post_video_link_to_subreddit: subreddit is None")
        time.sleep(2)
        self.reddit.subreddit(subreddit).submit(video_title, url=video_link)

    def add_posted_links_by_others(self, subreddit, db: cache.DB):
        if not subreddit or subreddit is None or subreddit == "":
            raise Exception("add_posted_links_by_others: subreddit is None")
        if not db or db is None:
            raise Exception("add_posted_links_by_others: db is None")
        time.sleep(2)
        for submission in self.reddit.subreddit(subreddit).new(limit=120):
            if submission.author == self.reddit.user.me():
                continue
            print(f"found submission from to add to db: {submission_to_s(submission)}")
            url = submission.url
            if "youtu.be" in url:
                split_link = url.split(".be/")[1].split("&")[0]
                url_to_add = f"https://www.youtube.com/watch?v={split_link}"
                db.add_to_posted_on_reddit(url_to_add)
                print(f"added url: {url_to_add}")
            if "youtube.com/watch" in url:
                split_link = url.split("/watch?v=")[1].split("&")[0]
                url_to_add = f"https://www.youtube.com/watch?v={split_link}"
                db.add_to_posted_on_reddit(url_to_add)
                print(f"added url: {url_to_add}")


def submission_to_s(submission) -> str:
    return f"Submission(id={submission.id}, author={submission.author}, title=`{submission.title}`, url={submission.url})"


def start_bot_process(channel_ids_fname=None, subreddit_to_post_to=None):
    if (
        not subreddit_to_post_to
        or subreddit_to_post_to is None
        or subreddit_to_post_to == ""
    ):
        raise Exception("start_bot_process: subreddit_to_post_to is None")
    if not channel_ids_fname or channel_ids_fname is None or channel_ids_fname == "":
        raise Exception("start_bot_process: channel_ids_fname is None")
    cache_db = cache.DB()
    bot = Bot()
    bot.login()
    channel_ids = None
    while True:
        # First make sure we add all other videos that have not been posted by the bot
        bot.add_posted_links_by_others(subreddit=subreddit_to_post_to, db=cache_db)
        with open(channel_ids_fname) as f:
            channel_ids = f.readlines()
            channel_ids = [x.replace("\r", "").replace("\n", "") for x in channel_ids]
        new_videos_added = {channel_id: 0 for channel_id in channel_ids}
        for channel_id in channel_ids:
            channel = youtube.Channel(channel_id=channel_id)
            channel_links = channel.get_all_videos(cache=cache_db)
            for title, link in channel_links:
                if not cache_db.is_posted_to_reddit(link):
                    print(
                        f"posting to '{subreddit_to_post_to}' title={title}, link={link}"
                    )
                    bot.post_video_link_to_subreddit(
                        video_title=title,
                        video_link=link,
                        subreddit=subreddit_to_post_to,
                    )
                    cache_db.add_to_posted_on_reddit(link)
                    new_videos_added[channel_id] += 1
        for channel_id in channel_ids:
            print(
                f"ChannelID ({channel_id}) Processed! New Videos Posted {new_videos_added[channel_id]}"
            )
        print("Sleeping for 24hrs...")
        for i in range(24):
            print(f"Hour {i+1}")
            time.sleep(60 * 60)


def main():
    subreddit_to_post_to = "naptownmusicscene"
    channel_ids_fname = "channel_ids.txt"
    start_bot_process(
        channel_ids_fname=channel_ids_fname, subreddit_to_post_to=subreddit_to_post_to
    )


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
    main()
