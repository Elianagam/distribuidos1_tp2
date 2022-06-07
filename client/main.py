import logging
import os

from client import Client
from common.utils import initialize_log, initialize_config


def main():
    try:
        config_params = initialize_config(["FILE_COMMETS", "FILE_POSTS", "CHUNKSIZE",
            "POSTS_QUEUE", "COMMETS_QUEUE", "SEND_WORKERS_COMMENTS", "SEND_WORKERS_POSTS",
            "STUDENTS_QUEUE", "AVG_QUEUE", "IMAGE_QUEUE"])
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