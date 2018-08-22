#!/usr/bin/env python

import os
import shlex
import shutil
import logging
import datetime
import configparser

import praw

from models import Download
from downloader import Downloader
import database

class RedditMirrorer:
    reddit = None

    def __init__(self, config):
        self.config = config
        self.db = database.Database(config['database']['url'])
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        reddit_cfg = config['reddit']
        self.reddit = praw.Reddit(username=reddit_cfg['username'],
                                  password=reddit_cfg['password'],
                                  client_id=reddit_cfg['client_id'],
                                  client_secret=reddit_cfg['client_secret'],
                                  user_agent='python:subreddit mirrorer:v0.1 (by /u/drizz)')

        self.subreddit_name = reddit_cfg.get('subreddit', 'roadcam')
        self.downloader = Downloader(config['download'])

    def find_submission_by_id(self, thing_id):
        download = self.db.session.query(Download) \
                                  .filter_by(thing_id=thing_id) \
                                  .one_or_none()

        return download

    def download_submission(self, submission):
        if self.find_submission_by_id(submission.id) is None:
            return self.downloader.download(submission)

    def start_stream(self):
        subreddit = self.reddit.subreddit(self.subreddit_name)

        for submission in subreddit.stream.submissions():
            result = self.download_submission(submission)

            if result:
                now = datetime.datetime.now()
                download = Download(thing_id=submission.id,
                                    title=submission.title,
                                    url=submission.url,
                                    path=result['output_dir'],
                                    created_at=now,
                                    updated_at=now,
                                    downloaded_at=now)

                self.db.session.add(download)
                self.db.session.commit()

                self.post_download_hook(self, result)
                self.logger.debug("Download successful: {}".format(repr(result)))

    def post_download_hook(self, submission, result):
        rclone_cfg = self.config['rclone']
        rclone_dest_path = rclone_cfg['path']

        if not os.path.isabs(result['output_dir']):
            rclone_dest_path = os.path.join(rclone_dest_path, result['output_dir'])

        rclone_dest = "{}:{}".format(rclone_cfg['remote'], rclone_dest_path)
        rclone_cmd = "/usr/bin/rclone copy -v {} {}".format(shlex.quote(result['output_dir']),
                                                            shlex.quote(rclone_dest))

        self.logger.debug("Running {}".format(rclone_cmd))

        os.system(rclone_cmd)

        self.logger.debug("Removing files from {}".format(result['output_dir']))
        shutil.rmtree(result['output_dir'])

if __name__ == '__main__':
    # Initialize logging.
    logging.basicConfig(level=logging.INFO)

    # Load our config file.
    config = configparser.ConfigParser()
    config.read('config.ini')

    mirrorer = RedditMirrorer(config)
    mirrorer.start_stream()
