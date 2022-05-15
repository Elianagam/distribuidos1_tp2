SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

docker-image:
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./comments_filter_body/Dockerfile -t "comments_filter_body:latest" .
	docker build -f ./comments_filter_student/Dockerfile -t "comments_filter_student:latest" .
	docker build -f ./posts_filter_columns/Dockerfile -t "posts_filter_columns:latest" .
	docker build -f ./posts_sum_score/Dockerfile -t "posts_sum_score:latest" .
	docker build -f ./posts_avg_score/Dockerfile -t "posts_avg_score:latest" .
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