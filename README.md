# Distribuidos1_tp2

## Script docker-compose

```
python3 docker_compose.py <num_filters> <num_reducers> <chunksize>
```

Ejemplo
```
python3 docker_compose.py 2 2 200
```

## Run docker-compose

```
make docker-compose-down
make docker-client-image
make docker-image
make docker-compose-up
make docker-compose-logs
```