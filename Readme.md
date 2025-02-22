# Kafka Logger

Сервис для сбора и хранения логов с использованием Apache Kafka.


## Быстрый старт

### Предварительные требования
- Docker
- Docker Compose

### Запуск Kafka
1. Перейдите в директорию с `docker-compose.yml`:
   ```bash
   cd kafka
   ```
2. Запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

3. Создайте топик для логов:
   ```bash
   docker exec kafka /opt/bitnami/kafka/bin/kafka-topics.sh `
     --create `
     --topic app-logs `
     --bootstrap-server kafka:9092 `
     --partitions 1 `
     --replication-factor 1
   ```

**Apache Kafka доступна по пути: http://localhost:8090**


