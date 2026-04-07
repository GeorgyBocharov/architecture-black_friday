## Задание 4. Настройка шардирования с репликацикей mongo-db + Redis Cluster

В данном задании я релизовал кластер редиса: 3 ноды, replication factor 3.
Запуск кластера выполняется через контейнер redis-cluster-init и скрипт [text](init-scripts/redis/init-cluster.sh)


Также я доработал pymongo_api для работы с RedisCluster. Приложение запускается и возвращает закешированные данные 

### Процесс запуска
Считаем, что мы находимся в директории *sharding-repl-cache*

#### 1. Запуск всех сервисов

```bash
docker-compose up -d
```

#### 2. Наполнение базы пользователями (коллекция users)
```bash
./scripts/mongo-insert-users.sh
```

#### 3. Проверка сервиса
```bash
curl localhost:8080
```

![Результат запуска](screenshots\service-status.png)

#### 4. Запрос пользователей (ожидаем загрукзу 3 секунды)
```bash
curl localhost:8080/users/users
```


#### 5. Повторный запрос пользователей (ожидаем быструю загрукзу за счет кеша)
```bash
curl localhost:8080/users/users
```

![Результат запуска](screenshots\cache-hit-miss.png)

### Итоговые контейнеры

![Результат запуска](screenshots\redis-setup.png)