---
description: Проверить состояние удалённого сервера
---

# Check Server

Проверь состояние облачного сервера.

## Что проверить

1. **Подключись по SSH** к серверу

2. **Проверь системные ресурсы**:
   ```bash
   df -h
   free -h
   uptime
   ```

3. **Проверь сервисы**:
   ```bash
   sudo systemctl status [project]
   sudo systemctl status postgresql
   sudo systemctl status nginx
   ```

4. **Проверь логи** (последние ошибки):
   ```bash
   sudo journalctl -u [project] -p err -n 20
   sudo tail -n 50 /var/log/nginx/error.log
   ```

5. **Сформируй отчёт**:
   - Общее состояние: ОК / Есть проблемы
   - Ресурсы: диск, память, CPU
   - Статус сервисов
   - Последние ошибки (если есть)
