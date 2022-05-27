import logging
import signal
import os

from configparser import ConfigParser
from posts_avg_score import PostsAvgScore

def initialize_log():
    """
    Python custom logging initialization
    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level='INFO',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    #config.read("config.ini")

    config_params = {}
    try:
        config_params["QUEUE_RECV"] = config["DEFAULT"]['QUEUE_RECV']
        config_params["QUEUE_SEND"] = config["DEFAULT"]['QUEUE_SEND']
        config_params["RECV_WORKERS"] = int(config["DEFAULT"]['RECV_WORKERS'])
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

        recver = PostsAvgScore(
            config_params["QUEUE_RECV"],
            config_params["QUEUE_SEND"],
            config_params["RECV_WORKERS"]
        )
        recver.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"[MAIN_COMMENTS] Stop event is set")


if __name__ == "__main__":
    main()