### Задание 2. Настройка шардирования с репликацикей mongo-db

В данном задании я релизовал шардирование с репликацикей mongo-db

## Описание docker-compose
В докер-компоуз файле я завел: 
1) 3 реплики для configSrv 
2) 3 реплики для shard1
3) 3 реплики для shard2
4) 3 реплики для mongo_router

Итоговые контейнеры

![Результат запуска](screenshots\mongo-containers.png)

![Результат запуска](screenshots\mongo-script-results.png)