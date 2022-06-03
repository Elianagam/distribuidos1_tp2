import logging
import signal
import os

from configparser import ConfigParser
from comments_filter_columns import CommentsFilterColumns
from common.logs import initialize_log


def initialize_config():
    config = ConfigParser(os.environ)
    config_params = {}
    try:
        config_params["QUEUE_RECV"] = config["DEFAULT"]['QUEUE_RECV']
        config_params["QUEUE_SEND"] = config["DEFAULT"]['QUEUE_SEND']
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

        recver = CommentsFilterColumns(config_params["QUEUE_RECV"], config_params["QUEUE_SEND"])
        recver.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"[MAIN_COMMENTS] Stop event is set")
    except Exception as e:
        logging.error(f"[FILTER COMMENTS] ERROR {e}")


if __name__ == "__main__":
    main()