# Caching videos that we've already pulled and commented

import sqlite3

from config import DB_CACHE_NAME
from model import Video

CREATE_VIDEOS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS videos (
    video_link TEXT PRIMARY KEY,
    video_title TEXT,
    channel_id TEXT,
    UNIQUE(video_link, video_title, channel_id)
);"""
CREATE_POSTED_ON_REDDIT_SQL = """
CREATE TABLE IF NOT EXISTS posted_on_reddit (
    video_link TEXT PRIMARY KEY
);"""

INSERT_NEW_ROW_SQL = (
    "INSERT INTO videos (video_link, video_title, channel_id) VALUES (?, ?, ?);"
)
INSERT_INTO_POSTED_TO_REDDIT_SQL = (
    "INSERT INTO posted_on_reddit (video_link) VALUES (?);"
)

EXISTS_SQL = (
    "SELECT * FROM videos where video_link=? AND video_title=? AND channel_id=?;"
)

IS_POSTED_SQL = "SELECT * FROM posted_on_reddit where video_link=?;"

ALL_VIDEOS_PER_CHANNEL_SQL = (
    "SELECT video_link, video_title FROM videos where channel_id=?;"
)


class DB:
    db: sqlite3.Connection

    def __init__(self):
        self.db = sqlite3.connect(DB_CACHE_NAME)
        self._create_tables()

    def _create_tables(self):
        self.db.execute(CREATE_VIDEOS_TABLE_SQL)
        self.db.execute(CREATE_POSTED_ON_REDDIT_SQL)
        self.db.commit()

    def _add(self, video_link=None, video_title=None, channel_id=None):
        if not video_link or video_link is None or video_link == "":
            raise Exception("_add: video_link is None")
        if not video_title or video_title is None or video_title == "":
            raise Exception("_add: video_title is None")
        if not channel_id or channel_id is None or channel_id == "":
            raise Exception("_add: channel_id is None")
        try:
            self.db.execute(INSERT_NEW_ROW_SQL, (video_link, video_title, channel_id))
            self.db.commit()
        except Exception as e:
            print(f"_add: db add issue: error={e}")

    def exists(self, video_link=None, video_title=None, channel_id=None) -> bool:
        if not video_link or video_link is None or video_link == "":
            raise Exception("exists: video_link is None")
        if not video_title or video_title is None or video_title == "":
            raise Exception("exists: video_title is None")
        if not channel_id or channel_id is None or channel_id == "":
            raise Exception("exists: channel_id is None")
        cur = self.db.cursor()
        cur.execute(EXISTS_SQL, (video_link, video_title, channel_id))
        rows = cur.fetchall()
        # Technically this should always return 1
        return len(rows) >= 1

    def get_all_videos_for_channel(self, channel_id=None) -> list[Video]:
        if not channel_id or channel_id is None or channel_id == "":
            raise Exception("get_all_videos_for_channel: channel_id is None")
        cur = self.db.cursor()
        cur.execute(ALL_VIDEOS_PER_CHANNEL_SQL, (channel_id,))
        rows = cur.fetchall()
        return [Video(row[1], row[0]) for row in rows]

    def add_all_videos_for_channel(self, channel_id, videos: list[Video]):
        if not channel_id or channel_id is None or channel_id == "":
            raise Exception("add_all_videos_for_channel: channel_id is None")
        for video in videos:
            print(f"Channel={channel_id}, adding video={video}")
            self._add(
                video_link=video.link, video_title=video.title, channel_id=channel_id
            )

    def is_posted_to_reddit(self, video_link) -> bool:
        if not video_link or video_link is None or video_link == "":
            raise Exception("is_posted_to_reddit: video_link is None")
        cur = self.db.cursor()
        cur.execute(IS_POSTED_SQL, (video_link,))
        rows = cur.fetchall()
        # Technically this should always return 1
        return len(rows) >= 1

    def add_to_posted_on_reddit(self, video_link):
        if not video_link or video_link is None or video_link == "":
            raise Exception("is_posted_to_reddit: video_link is None")
        try:
            self.db.execute(INSERT_INTO_POSTED_TO_REDDIT_SQL, (video_link,))
            self.db.commit()
        except Exception as e:
            print(f"add_to_posted_on_reddit: db add issue: error={e}")
