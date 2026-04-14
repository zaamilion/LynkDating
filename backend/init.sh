#!/bin/bash

# Функция ожидания, пока Kafka станет доступной
wait_for_kafka() {
    echo "Ожидание Kafka..."
    while ! timeout 5 bash -c "echo > /dev/tcp/kafka/9092"; do
        echo "Kafka ещё не готова. Жду 5 секунд..."
        sleep 5
    done
    echo "Kafka доступна!"
}

# Создаем топики
create_topics() {
    echo "Создаю топики..."
    kafka-topics --bootstrap-server kafka:9092 \
      --create --topic  friends\
      --partitions 3 --replication-factor 1 \
      --config retention.ms=86400000 \
      --config cleanup.policy=compact
    kafka-topics --bootstrap-server kafka:9092 \
      --create --topic  matches\
      --partitions 3 --replication-factor 1 \
      --config retention.ms=86400000 \
      --config cleanup.policy=compact

    echo "Все топики созданы!"
}

# Основная логика
wait_for_kafka
create_topics