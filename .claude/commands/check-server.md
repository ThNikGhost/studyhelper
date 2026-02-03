# Check Server

Проверь состояние облачного сервера.

## Что проверить

1. **Подключись по SSH** к серверу

2. **Проверь системные ресурсы**:
   ```bash
   # Место на диске
   df -h
   
   # Память
   free -h
   
   # Загрузка CPU
   uptime
   ```

3. **Проверь сервисы**:
   ```bash
   # Статус приложения
   sudo systemctl status [project]
   
   # Статус PostgreSQL
   sudo systemctl status postgresql
   
   # Статус nginx (если используется)
   sudo systemctl status nginx
   ```

4. **Проверь логи** (последние ошибки):
   ```bash
   # Логи приложения
   sudo journalctl -u [project] -p err -n 20
   
   # Логи nginx
   sudo tail -n 50 /var/log/nginx/error.log
   ```

5. **Сформируй отчёт**:
   - Общее состояние: ОК / Есть проблемы
   - Ресурсы: диск, память, CPU
   - Статус сервисов
   - Последние ошибки (если есть)
