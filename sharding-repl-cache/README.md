### Задание 2. Настройка шардирования с репликацикей mongo-db

В данном задании я релизовал кластер редиса: 3 ноды, replication factor 3.
Запуск кластера выполняется через контейнер redis-cluster-init и скрипт [text](init-scripts/redis/init-cluster.sh)


Также я доработал pymongo_api для работы с RedisCluster. Приложение запускается и возвращает закешированные данные 

Итоговые контейнеры

![Результат запуска](screenshots\redis-setup.png)

![Результат запуска](screenshots\cache-hit-miss.png)