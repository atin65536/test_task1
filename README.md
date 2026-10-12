## Установка

### Подготовка локального окружения
```bash
sudo apt install make curl
```

### Установка пакетного менеджера для локальной разработки
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Установка docker с docker-compose-plugin
```http request
https://docs.docker.com/engine/install/
```

## Запуск окружений
При запуске окружения очищаются все результаты работы прошлого запуска

### Окружение по-умолчанию (90% успеха обработки платежа)
```bash
make up
```

### 100% успеха обработки платежа
```bash
make up-processor-success
```

### 0% успеха обработки платежа
```bash
make up-processor-error
```

## Предварительно подготовленные запросы

### Полностью корректные запросы
```bash
make create-normal-1  # Idempotency-Key: normal-1
make create-normal-2  # Idempotency-Key: normal-2
```

### Запрос с некорректным `webhook_url`
```bash
make create-invalid-webhook  # Idempotency-Key: invalid-webhook
```

### Swagger playground
```http request
http://localhost:8080/docs
```
