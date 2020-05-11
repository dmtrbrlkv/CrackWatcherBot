import requests
import datetime
import dateutil.parser, dateutil.tz
import time
import logging

from http import HTTPStatus

URL = "https://api.crackwatch.com/api/games?&sort_by=crack_date&is_cracked=true"
URL_AAA = "https://api.crackwatch.com/api/games?&sort_by=crack_date&is_cracked=true&is_aaa=true"

LAST_CHECK_DATE = datetime.datetime.now(dateutil.tz.tzlocal())


class GameInfo:
    def __init__(self, title, id, is_AAA, crack_date, image, image_poster, url, groups):
        self.title = title
        self.id = id
        self.is_AAA = is_AAA
        self.crack_date = crack_date
        self.image = image
        self.image_poster = image_poster
        self.url = url
        self.groups = groups

    @classmethod
    def from_data(cls, data):
        title = data["title"]
        id = data["_id"]
        is_AAA = data["isAAA"]
        crack_date = dateutil.parser.parse(data["crackDate"])
        image = data["image"]
        image_poster = data["imagePoster"]
        url = data["url"]
        groups = ", ".join(data["groups"])
        return GameInfo(title, id, is_AAA, crack_date, image, image_poster, url, groups)

    def __str__(self):
        return f"Title: {self.title}, crack date: {self.crack_date}, AAA: {self.is_AAA}"

    __repr__ = __str__


class CrackWatch:
    def __init__(self, url=None, url_AAA=None, last_date=None):
        if url is None:
            url = URL
        if url_AAA is None:
            url_AAA = URL_AAA
        if last_date is None:
            last_date = LAST_CHECK_DATE

        self.url = url
        self.url_AAA = url_AAA
        self.last_check_date = last_date
        self.last_game_infos = None

    def load_data(self, is_AAA=False):
        for _ in range(5):
            response = requests.get(self.url_AAA if is_AAA else self.url)
            if response.status_code == HTTPStatus.OK:
                break
            logging.info(f"{response.status_code} from {self.url_AAA if is_AAA else self.url}")
            time.sleep(5)
            response = None

        if response is None:
            return None

        data = response.json()

        return data

    def last_cracked_n(self, is_AAA=False, n=30):
        data = self.load_data(is_AAA)
        if data is None:
            return None

        game_infos = []
        for game_data in data:
            game_info = GameInfo.from_data(game_data)

            game_infos.append(game_info)
            if len(game_infos) == n:
                break

        return game_infos

    def load_new_cracked(self):
        data = self.load_data()
        if data is None:
            return False

        game_infos = []
        for game_data in data:
            game_info = GameInfo.from_data(game_data)
            if game_info.crack_date < self.last_check_date:
                break

            game_infos.append(game_info)

        self.last_game_infos = game_infos
        self.update_check_date()
        return True

    def update_check_date(self, date=None):
        if date is None:
            date = datetime.datetime.now(dateutil.tz.tzlocal())
        self.last_check_date = date


    def new_cracked(self, is_AAA=False):
        game_infos = self.last_game_infos
        if game_infos is None:
            return None

        res = []

        if not is_AAA:
            res.extend(game_infos)
            return res



        for game_info in game_infos:
            if not game_info.is_AAA:
                continue
            res.append(game_info)

        return res


