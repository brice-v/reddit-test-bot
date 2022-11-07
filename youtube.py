# Interacting with Youtube API

import sys
import time
from typing import Optional

import requests

from icecream import ic

from model import Video
from config import YOUTUBE_API_KEY
from cache import DB

YOUTUBE_API_SLEEP = 5


class Channel:
    video_links_and_titles: list[Video]
    next_page_token: Optional[str]
    channel_id: str

    def __init__(self, channel_id):
        if not channel_id or channel_id is None or channel_id == "":
            raise Exception("channel_id is None")
        self.channel_id = channel_id
        self.next_page_token = None
        self.video_links_and_titles = []

    def get_all_videos(self, cache: Optional[DB] = None) -> list[Video]:
        self._get_videos_from_channel(next_page_token=self.next_page_token)
        if cache:
            # Check if the first row returned exists, if so its already been added and in the DB
            if self.video_links_and_titles:
                top_video = self.video_links_and_titles[0]
                if cache.exists(top_video.link, top_video.title, self.channel_id):
                    return cache.get_all_videos_for_channel(self.channel_id)
        while self.next_page_token is not None:
            self._get_videos_from_channel(next_page_token=self.next_page_token)
        if cache:
            cache.add_all_videos_for_channel(
                self.channel_id, self.video_links_and_titles
            )
        return self.video_links_and_titles

    def _get_videos_from_channel(self, next_page_token=None):
        next_page_token_str = (
            "" if next_page_token is None else f"&page_token={next_page_token}"
        )
        url = f"https://www.googleapis.com/youtube/v3/search?channelId={self.channel_id}&order=date&part=snippet&type=video&maxResult=50{next_page_token_str}&key={YOUTUBE_API_KEY}"
        print(
            f"(before calling youtube api) Sleeping for {YOUTUBE_API_SLEEP} seconds..."
        )

        time.sleep(YOUTUBE_API_SLEEP)
        response = requests.get(url)
        if response.status_code == 200 and "application/json" in response.headers.get(
            "Content-Type", ""
        ):
            respObj = response.json()
            # ic(respObj)
            self.next_page_token = respObj.get("nextPageToken", None)
            # ic(respObj["items"][0]["id"]["videoId"])
            video_id = ""
            video_title = ""
            for idx in range(len(respObj["items"])):
                video_id = respObj["items"][idx]["id"]["videoId"]
                video_title = respObj["items"][idx]["snippet"]["title"]
                if video_id == "":
                    raise Exception("_get_videos_from_channel: video_id is ''")
                if video_title == "":
                    raise Exception("_get_videos_from_channel: video_title is ''")
                self.video_links_and_titles.append(
                    Video(video_title, f"https://www.youtube.com/watch?v={video_id}")
                )
        else:
            print("Youtube is mad at me, killing process...")
            if response.status_code == 403:
                ic(response.json())
            sys.exit(1)
