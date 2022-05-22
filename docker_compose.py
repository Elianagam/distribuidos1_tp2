import sys

INIT_DOCKER = """version: '3'
services:
  rabbitmq:
    build:
      context: ./rabbitmq
      dockerfile: Dockerfile
    ports:
      - 15672:15672
      - 5672:5672

  client:
    container_name: client
    image: client:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - CHUNKSIZE={}
      - FILE_COMMETS=comments.csv
      - FILE_POSTS=posts.csv
      - COMMETS_QUEUE=comments_queue 
      - POSTS_QUEUE=posts_queue

  <COMMENTS_FILTER_COLUMNS>
  <COMMENTS_FILTER_STUDENTS>
  <POST_FILTER_SCORE_GTE_AVG>
  <POST_REDUCE_AVG_SENTIMETS>

  posts_max_avg_sentiment:
    container_name: posts_max_avg_sentiment
    image: posts_max_avg_sentiment:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    volumes:
      - ./posts_max_avg_sentiment/:/
    environment:
      - QUEUE_RECV=post_sentiments_queue
      - QUEUE_SEND=post_avg_sentiments_queue

  <POSTS_FILTER_COLUMNS>

  posts_avg_score:
    container_name: posts_avg_score
    image: posts_avg_score:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV=posts_for_avg_queue
      - QUEUE_SEND=posts_avg_score_queue

  join_comments_with_posts:
    container_name: join_comments_with_posts
    image: join_comments_with_posts:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV_COMMENTS=comments_filter_queue
      - QUEUE_RECV_POSTS=posts_for_join_queue
      - QUEUE_SEND_STUDENTS=cmt_pst_join_st_queue
      - QUEUE_SEND_SENTIMENTS=cmt_pst_join_se_queue
      - CHUNKSIZE={}
"""

COMENTS_FILTERS = """
  comments_filter_columns_{}:
    container_name: comments_filter_columns_{}
    image: comments_filter_columns:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV=comments_queue
      - QUEUE_SEND=comments_filter_queue
"""

FILTER_STUDENTS = """
  comments_filter_student_{}:
    container_name: comments_filter_student_{}
    image: comments_filter_student:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV=cmt_pst_join_st_queue
      - QUEUE_SEND=posts_student_queue
"""

FILTER_SCORE_STUDENTS = """
  posts_filter_score_gte_avg_{}:
    container_name: posts_filter_score_gte_avg_{}
    image: posts_filter_score_gte_avg:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV_AVG=posts_avg_score_queue
      - QUEUE_RECV_STUDENTS=posts_student_queue
      - QUEUE_SEND=student_url_queue
      - CHUNKSIZE={}
"""

POSTS_FILTER = """
  posts_filter_columns_{}:
    container_name: posts_filter_columns_{}
    image: posts_filter_columns:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV=posts_queue
      - QUEUE_SEND_JOIN=posts_for_join_queue
      - QUEUE_SEND_AVG=posts_for_avg_queue
"""

REDUCE_SENTIMETS = """
  posts_reduce_avg_sentiment_{}:
    container_name: posts_reduce_avg_sentiment_{}
    image: posts_avg_sentiment:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - QUEUE_RECV=cmt_pst_join_se_queue
      - QUEUE_SEND=post_sentiments_queue
"""

def main():
    filters = int(sys.argv[1])
    filter_exchange = int(sys.argv[2])
    chunksize = int(sys.argv[3])

    filters_c = ""
    filters_p = ""
    for i in range(1,filters+1):
        filters_c += COMENTS_FILTERS.format(i, i)
        filters_p += POSTS_FILTER.format(i, i)
    
    filters_s = ""
    filters_ss = ""
    reduce_se = ""
    for x in range(1,filter_exchange+1):
        filters_s += FILTER_STUDENTS.format(x, x)
        filters_ss += FILTER_SCORE_STUDENTS.format(x, x, chunksize)
        reduce_se += REDUCE_SENTIMETS.format(x,x)

    compose = INIT_DOCKER.format(chunksize, chunksize) \
                  .replace("<COMMENTS_FILTER_COLUMNS>", filters_c) \
                  .replace("<COMMENTS_FILTER_STUDENTS>", filters_s) \
                  .replace("<POST_FILTER_SCORE_GTE_AVG>", filters_ss) \
                  .replace("<POSTS_FILTER_COLUMNS>", filters_p) \
                  .replace("<POST_REDUCE_AVG_SENTIMETS>", reduce_se) \

    with open("docker-compose.yaml", "w") as compose_file:
        compose_file.write(compose)

if __name__ == "__main__":
    main()