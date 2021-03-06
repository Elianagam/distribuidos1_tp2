import logging

from posts_filter_score_gte_avg import PostsFilterScoreGteAvg
from common.utils import initialize_log, initialize_config


def main():
    try:
        config_params = initialize_config(["QUEUE_RECV_AVG", "QUEUE_RECV_STUDENTS",
            "QUEUE_SEND", "CHUNKSIZE"])
        initialize_log()

        logging.info("Server configuration: {}".format(config_params))

        recver = PostsFilterScoreGteAvg(
            config_params["QUEUE_RECV_AVG"],
            config_params["QUEUE_RECV_STUDENTS"],
            config_params["QUEUE_SEND"],
            int(config_params["CHUNKSIZE"])
        )
        recver.start()
    except Exception as e:
        logging.info(f"Close Connection")


if __name__ == "__main__":
    main()