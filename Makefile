SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

docker-image:
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./comments_filter_columns/Dockerfile -t "comments_filter_columns:latest" .
	docker build -f ./comments_filter_student/Dockerfile -t "comments_filter_student:latest" .

	#docker build -f ./comments_groupby_url/Dockerfile -t "comments_groupby_url:latest" .
	docker build -f ./posts_avg_sentiment/Dockerfile -t "posts_avg_sentiment:latest" .
	docker build -f ./posts_max_avg_sentiment/Dockerfile -t "posts_max_avg_sentiment:latest" .

	docker build -f ./posts_filter_columns/Dockerfile -t "posts_filter_columns:latest" .
	docker build -f ./posts_avg_score/Dockerfile -t "posts_avg_score:latest" .
	docker build -f ./join_comments_with_posts/Dockerfile -t "join_comments_with_posts:latest" .
.PHONY: docker-image

docker-compose-up:
	docker-compose -f docker-compose.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	docker-compose -f docker-compose.yaml stop -t 1
	docker-compose -f docker-compose.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker-compose -f docker-compose.yaml logs -f
.PHONY: docker-compose-logs