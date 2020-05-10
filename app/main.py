import crack_watch
import bot
import dateutil.tz
import json
import time
import logging
from threading import Thread
import psycopg2


class Watcher(Thread):
    def __init__(self, every, subscribe, cursor):
        super().__init__()
        self.every = every
        self.subscribe = subscribe
        self.cursor = cursor

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
            logging.info(f"Watch new cracks")
            cw.load_new_cracked()
            if cw.last_game_infos:
                logging.info(f"Watched {len(cw.last_game_infos)} new cracks")
                self.send_info_to_subscribers(cw.last_game_infos, self.subscribe)
                self.save_last_date(cw.last_check_date)
            else:
                logging.info(f"No new cracks")
            time.sleep(self.every)

    def load_last_date(self):
        self.cursor.execute('SELECT * FROM last_watch')
        date = self.cursor.fetchone()
        return date[0]


    def save_last_date(self, date):
        self.cursor.execute(f"UPDATE last_watch SET date = '{str(date)}'")


def main():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    b = bot.bot
    subscribe = bot.subscribe
    cursor = bot.cursor

    watcher = Watcher(5, subscribe, cursor)
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




