# SingBox Reality Updater

**Automated REALITY node fetcher and configuration generator for Sing‑Box.**

SingBox Reality Updater is a lightweight and reliable automation tool that keeps your Sing‑Box configuration up to date.
It fetches VLESS REALITY nodes, validates them, checks availability, builds a clean `config.json`, and safely restarts the service.

## ✨ Features

- Fetches VLESS REALITY nodes from a remote source
- Strict filtering: `security=reality`, `flow=xtls-rprx-vision`
- TLS‑based availability check
- Parallel node validation (ThreadPoolExecutor)
- Deduplication and node limit control
- Generates a minimal, production‑ready Sing‑Box configuration
- Validates configuration via `sing-box check`
    
- Atomic config replacement
    
- Rotating log system
    
- YAML‑based configuration

## 📦 Requirements

- Python 3.8+
    
- Sing‑Box installed
    
- Systemd
    
- Root privileges
    
- PyYAML package:


    ```bash
    apt install python3-yaml -y
    ```

## 🚀 Usage

```bash
python3 singbox-updater.py
```

## 📄 Logs

```
/var/log/singbox-updater.log
```

## 🧩 Workflow

1. Fetch node list
    
2. Parse REALITY nodes
    
3. Filter and deduplicate
    
4. Check availability
    
5. Build configuration
    
6. Validate with `sing-box check`
    
7. Atomic write
    
8. Restart service
    

## ⚠️ Limitations

- Only TCP REALITY nodes are supported
    
- TLS handshake does not guarantee full proxy functionality
    
- DNS servers are static
    
- No fallback URL (optional feature)
    
---

# SingBox Reality Updater

**Автоматическое получение REALITY‑нод и генерация конфига для Sing‑Box.**

SingBox Reality Updater — это лёгкий и надёжный инструмент, который полностью автоматизирует обновление VLESS REALITY‑нод для Sing‑Box.
Скрипт загружает список нод, фильтрует их, проверяет доступность, формирует корректный `config.json` и безопасно перезапускает сервис.

## ✨ Возможности

- Загрузка списка VLESS REALITY‑нод из внешнего источника
    
- Строгая фильтрация: `security=reality`, `flow=xtls-rprx-vision`
    
- Проверка доступности через TLS‑рукопожатие
    
- Параллельная проверка нод (ThreadPoolExecutor)
    
- Дедупликация и ограничение количества нод
    
- Генерация минимального и чистого конфига Sing‑Box
    
- Проверка через `sing-box check` перед применением
    
- Атомарная запись в `/etc/sing-box/config.json`
    
- Логирование с ротацией
    
- YAML‑конфигурация для всех параметров
    

## 📦 Требования

- Python 3.8+
    
- Sing‑Box установлен в системе
    
- Systemd
    
- Права root
    
- Пакет PyYAML:
    

    ```bash
    apt install python3-yaml -y
    ```

## 🚀 Запуск

```bash
python3 singbox-updater.py
```

## 📄 Логи

```
/var/log/singbox-updater.log
```

## 🧩 Как работает

1. Загрузка списка нод
    
2. Парсинг только REALITY
    
3. Фильтрация и дедупликация
    
4. Проверка доступности
    
5. Генерация конфига
    
6. Проверка через `sing-box check`
    
7. Атомарная запись
    
8. Перезапуск сервиса
    

## ⚠️ Ограничения

- Поддерживается только TCP REALITY
    
- TLS‑проверка не гарантирует 100% работоспособность прокси
    
- DNS‑серверы задаются вручную
    
- Нет fallback‑URL (можно добавить)
    
