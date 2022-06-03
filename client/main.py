import logging
import signal
import os

from configparser import ConfigParser
from client import Client
from common.logs import initialize_log


def initialize_config():
    config = ConfigParser(os.environ)
    config_params = {}
    try:
        config_params["FILE_COMMETS"] = config["DEFAULT"]['FILE_COMMETS']
        config_params["FILE_POSTS"] = config["DEFAULT"]['FILE_POSTS']
        config_params["CHUNKSIZE"] = int(config["DEFAULT"]['CHUNKSIZE'])
        config_params["POSTS_QUEUE"] = config["DEFAULT"]['POSTS_QUEUE']
        config_params["COMMETS_QUEUE"] = config["DEFAULT"]['COMMETS_QUEUE']
        config_params["SEND_WORKERS_COMMENTS"] = int(config["DEFAULT"]['SEND_WORKERS_COMMENTS'])
        config_params["SEND_WORKERS_POSTS"] = int(config["DEFAULT"]['SEND_WORKERS_POSTS'])

        config_params["STUDENTS_QUEUE"] = config["DEFAULT"]['STUDENTS_QUEUE']
        config_params["AVG_QUEUE"] = config["DEFAULT"]['AVG_QUEUE']
        config_params["IMAGE_QUEUE"] = config["DEFAULT"]['IMAGE_QUEUE']
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
        try:
            print(os.listdir("data"))
        except:
            pass
        client = Client(
            config_params["COMMETS_QUEUE"],
            config_params["POSTS_QUEUE"],
            config_params["FILE_COMMETS"],
            config_params["FILE_POSTS"],
            config_params["CHUNKSIZE"],
            config_params["SEND_WORKERS_COMMENTS"],
            config_params["SEND_WORKERS_POSTS"],
            config_params["STUDENTS_QUEUE"],
            config_params["AVG_QUEUE"],
            config_params["IMAGE_QUEUE"],
        )
        client.start()
    except Exception as e:
        logging.info(f"Close Connection")


if __name__ == "__main__":
    main()