import logging
import signal
import os

from configparser import ConfigParser
from posts_filter_score_gte_avg import PostsFilterScoreGteAvg
from common.logs import initialize_log


def initialize_config():
    config = ConfigParser(os.environ)
    config_params = {}
    try:
        config_params["QUEUE_RECV_AVG"] = config["DEFAULT"]['QUEUE_RECV_AVG']
        config_params["QUEUE_RECV_STUDENTS"] = config["DEFAULT"]['QUEUE_RECV_STUDENTS']
        config_params["QUEUE_SEND"] = config["DEFAULT"]['QUEUE_SEND']
        config_params["CHUNKSIZE"] = int(config["DEFAULT"]['CHUNKSIZE'])
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

        recver = PostsFilterScoreGteAvg(
            config_params["QUEUE_RECV_AVG"],
            config_params["QUEUE_RECV_STUDENTS"],
            config_params["QUEUE_SEND"],
            config_params["CHUNKSIZE"]
        )
        recver.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"[MAIN_COMMENTS] Stop event is set")


if __name__ == "__main__":
    main()