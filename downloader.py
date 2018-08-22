import os
import logging
import json
import glob

from os import path

import youtube_dl

youtube_dl_logger = logging.getLogger('YoutubeDL')

SERIALIZABLE_TYPES = [str, list, dict, int, float, complex, bool, type(None)]
YOTUBE_DL_OPTIONS = {
    'format': 'bestaudio/best',
    'logger': youtube_dl_logger,
    'writeinfojson': True,
    'writethumbnail': True,
    'write_all_thumbnails': True,
    'writesubtitles': True,
    'allsubtitles': True,
    'writeautomaticsub': True,
    'no_color': True,
}


def serialize_prawn_model(model):
    result = {}

    for key, value in dict(vars(model)).items():
        if type(value) in SERIALIZABLE_TYPES:
            result[key] = value
        else:
            result[key] = str(value)

    return result


class Downloader:
    def __init__(self, config):
        self.queue = []
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.output_dir = path.expandvars(path.expanduser(config['output_dir']))

    def download(self, submission):
        keys = {
            'subreddit': submission.subreddit.display_name,
            'submission_id': submission.id
        }
        output_dir = self.output_dir.format(**keys)
        result = {
            'output_dir': output_dir,
        }

        if not path.isdir(output_dir):
            os.makedirs(output_dir)

        self.logger.debug("Downloading submission {} with id {} to {}".format(repr(submission.title), submission.id, output_dir))
        self.dump_submission_as_json(submission, output_dir)

        ydl_options = YOTUBE_DL_OPTIONS.copy()
        ydl_options['outtmpl'] = path.join(output_dir, 'media', '%(title)s.%(ext)s')

        try:
            self.logger.debug("Trying to fetch media from submission url {}".format(submission.url))
            ydl = youtube_dl.YoutubeDL(ydl_options)
            ydl.download([submission.url])

            media_files = glob.glob(path.join(output_dir, 'media', '**'), recursive=True)
            result['media_files'] = media_files
        except Exception as e:
            self.logger.error("Media download failed: {}".format(str(e)))
            return None

        return result

    def dump_submission_as_json(self, submission, output_dir):
        submission_json_path = path.join(output_dir, 'submission.json')

        self.logger.debug("Saving submission to {}".format(submission_json_path))
        with open(submission_json_path, 'w') as f:
            json.dump(serialize_prawn_model(submission), f)

        comments_json_path = path.join(output_dir, 'comments.json')

        self.logger.debug("Saving comments to {}".format(comments_json_path))
        with open(comments_json_path, 'w') as f:
            json.dump([serialize_prawn_model(comment) for comment in list(submission.comments)], f)
