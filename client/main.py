import logging
import signal
import os

from configparser import ConfigParser
from client import Client

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
        config_params["FILE_COMMETS"] = config["DEFAULT"]['FILE_COMMETS']
        config_params["FILE_POSTS"] = config["DEFAULT"]['FILE_POSTS']
        config_params["CHUNKSIZE"] = int(config["DEFAULT"]['CHUNKSIZE'])
        config_params["POSTS_QUEUE"] = config["DEFAULT"]['POSTS_QUEUE']
        config_params["COMMETS_QUEUE"] = config["DEFAULT"]['COMMETS_QUEUE']
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    try:
        config_params = initialize_config()
        initialize_log()

        logging.debug("Client configuration: {}".format(config_params))

        client = Client(
            config_params["COMMETS_QUEUE"],
            config_params["POSTS_QUEUE"],
            config_params["FILE_COMMETS"],
            config_params["FILE_POSTS"],
            config_params["CHUNKSIZE"]
        )
        client.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info(f"[MAIN_CLIENT] Stop event is set")


if __name__ == "__main__":
    main()