import logging

from comments_filter_student import CommentsFilterStudent
from common.utils import initialize_log, initialize_config


def main():
    try:
        config_params = initialize_config(["QUEUE_RECV", "QUEUE_SEND", "RECV_WORKERS", "WORKER_KEY"])
        initialize_log()

        logging.info("Server configuration: {}".format(config_params))

        recver = CommentsFilterStudent(
            config_params["QUEUE_RECV"],
            config_params["QUEUE_SEND"],
            int(config_params["RECV_WORKERS"])
            int(config_params["WORKER_KEY"])
        )
        recver.start()
    except Exception as e:
        logging.info(f"Close Connection")


if __name__ == "__main__":
    main()