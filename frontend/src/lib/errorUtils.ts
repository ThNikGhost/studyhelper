import { AxiosError } from 'axios'

const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: 'Неверный запрос',
  401: 'Неверный email или пароль',
  403: 'Доступ запрещён',
  404: 'Не найдено',
  409: 'Такой пользователь уже существует',
  422: 'Ошибка валидации данных',
  429: 'Слишком много запросов. Попробуйте позже',
  500: 'Внутренняя ошибка сервера',
}

export function getErrorMessage(err: unknown, fallback = 'Произошла ошибка'): string {
  if (err instanceof AxiosError) {
    // Try to get detail from response body
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }

    // Fall back to HTTP status code mapping
    const status = err.response?.status
    if (status && HTTP_ERROR_MESSAGES[status]) {
      return HTTP_ERROR_MESSAGES[status]
    }

    // Network error
    if (err.code === 'ERR_NETWORK') {
      return 'Ошибка сети. Проверьте подключение к интернету'
    }
  }

  if (err instanceof Error) {
    return err.message
  }

  return fallback
}
