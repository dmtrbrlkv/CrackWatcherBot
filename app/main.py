import crack_watch
import bot
import dateutil.tz
import json
import time
import logging
from threading import Thread


class Watcher(Thread):
    def __init__(self, every, subscribe):
        super().__init__()
        self.every = every
        self.subscribe = subscribe

    @staticmethod
    def send_info_to_subscribers(game_infos, subscribe):
        for game_info in game_infos:
            for id, is_AAA in subscribe.items():
                if not is_AAA or (is_AAA and game_info.is_AAA):
                    bot.send_game_info(id, game_info)
                    logging.info(f"Send crack info {game_info.title} to {id}")

    def run(self):
        last_date = self.load_last_date()
        cw = crack_watch.CrackWatch(last_date=last_date)

        while True:
            cw.load_new_cracked()
            logging.info(f"Watch {len(cw.last_game_infos)} new cracks")
            if cw.last_game_infos:
                self.send_info_to_subscribers(cw.last_game_infos, self.subscribe)
                self.save_last_date(cw.last_check_date)
            time.sleep(self.every)

    @staticmethod
    def load_last_date():
        with open("app/config.json") as f:
            config = json.load(f)
        date = dateutil.parser.parse(config["last_date"])
        return date

    @staticmethod
    def save_last_date(date):
        with open("app/config.json") as f:
            config = json.load(f)
        config["last_date"] = str(date)
        with open("app/config.json", mode="w") as f:
            json.dump(config, f)


def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    b = bot.bot

    subscribe = bot.subscribe
    watcher = Watcher(5*60, subscribe)
    watcher.start()

    #
    # game_infos = cw.new_cracked()
    # print(game_infos)
    #
    # cw.load_new_cracked()
    # game_infos = cw.new_cracked()
    # print(game_infos)
    #
    # cw.load_new_cracked()
    # game_infos = cw.new_cracked()
    # print(game_infos)
    #
    # # save_last_date(cw.last_check_date)

    b.polling()


if __name__ == "__main__":
    main()




