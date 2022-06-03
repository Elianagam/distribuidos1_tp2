import logging
import signal
import os

from configparser import ConfigParser
from posts_filter_columns import PostsFilterColumns
from common.logs import initialize_log


def initialize_config():
    config = ConfigParser(os.environ)
    config_params = {}
    try:
        config_params["QUEUE_RECV"] = config["DEFAULT"]['QUEUE_RECV']
        config_params["QUEUE_SEND_JOIN"] = config["DEFAULT"]['QUEUE_SEND_JOIN']
        config_params["QUEUE_SEND_AVG"] = config["DEFAULT"]['QUEUE_SEND_AVG']
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

        recver = PostsFilterColumns(
            queue_recv=config_params["QUEUE_RECV"],
            queue_send_to_join=config_params["QUEUE_SEND_JOIN"],
            queue_send_to_avg=config_params["QUEUE_SEND_AVG"]
            )
        recver.start()
    except Exception as e:
        logging.info(f"Close Connection")


if __name__ == "__main__":
    main()