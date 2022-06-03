import logging
import signal
import os

from configparser import ConfigParser
from join_comments_with_posts import JoinCommentsWithPosts
from common.logs import initialize_log


def initialize_config():
    config = ConfigParser(os.environ)
    config_params = {}
    try:
        config_params["QUEUE_RECV_COMMENTS"] = config["DEFAULT"]['QUEUE_RECV_COMMENTS']
        config_params["QUEUE_RECV_POSTS"] = config["DEFAULT"]['QUEUE_RECV_POSTS']
        config_params["QUEUE_SEND_STUDENTS"] = config["DEFAULT"]['QUEUE_SEND_STUDENTS']
        config_params["QUEUE_SEND_SENTIMENTS"] = config["DEFAULT"]['QUEUE_SEND_SENTIMENTS']
        config_params["CHUNKSIZE"] = int(config["DEFAULT"]['CHUNKSIZE'])
        config_params["RECV_WORKERS"] = int(config["DEFAULT"]['RECV_WORKERS'])
        config_params["SEND_WORKERS"] = int(config["DEFAULT"]['SEND_WORKERS'])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))
    return config_params


def main():
    try:
        config_params = initialize_config()
        initialize_log()

        logging.info("Server configuration: {}".format(config_params))

        recver = JoinCommentsWithPosts(
            queue_recv_comments=config_params["QUEUE_RECV_COMMENTS"],
            queue_recv_post=config_params["QUEUE_RECV_POSTS"],
            queue_send_students=config_params["QUEUE_SEND_STUDENTS"],
            queue_send_sentiments=config_params["QUEUE_SEND_SENTIMENTS"],
            chunksize=config_params["CHUNKSIZE"],
            recv_workers=config_params["RECV_WORKERS"],
            send_workers=config_params["SEND_WORKERS"]
            )
        recver.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"[MAIN_COMMENTS] Stop event is set")


if __name__ == "__main__":
    main()