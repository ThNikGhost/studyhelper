import { describe, it, expect } from 'vitest'
import { AxiosError, type AxiosResponse } from 'axios'
import { getErrorMessage } from '../errorUtils'

function makeAxiosError(
  status?: number,
  detail?: unknown,
  code?: string,
): AxiosError {
  const error = new AxiosError(
    'Request failed',
    code ?? 'ERR_BAD_REQUEST',
    undefined,
    undefined,
    status
      ? ({
          status,
          data: detail !== undefined ? { detail } : {},
        } as AxiosResponse)
      : undefined,
  )
  return error
}

describe('getErrorMessage', () => {
  it('returns detail string from AxiosError response', () => {
    const err = makeAxiosError(400, 'Custom error message')
    expect(getErrorMessage(err)).toBe('Custom error message')
  })

  it('returns mapped message for 401 status', () => {
    const err = makeAxiosError(401)
    expect(getErrorMessage(err)).toBe('Неверный email или пароль')
  })

  it('returns mapped message for 429 status', () => {
    const err = makeAxiosError(429)
    expect(getErrorMessage(err)).toBe('Слишком много запросов. Попробуйте позже')
  })

  it('returns mapped message for 403 status', () => {
    const err = makeAxiosError(403)
    expect(getErrorMessage(err)).toBe('Доступ запрещён')
  })

  it('returns mapped message for 404 status', () => {
    const err = makeAxiosError(404)
    expect(getErrorMessage(err)).toBe('Не найдено')
  })

  it('returns mapped message for 409 status', () => {
    const err = makeAxiosError(409)
    expect(getErrorMessage(err)).toBe('Такой пользователь уже существует')
  })

  it('returns mapped message for 500 status', () => {
    const err = makeAxiosError(500)
    expect(getErrorMessage(err)).toBe('Внутренняя ошибка сервера')
  })

  it('returns network error message for ERR_NETWORK', () => {
    const err = makeAxiosError(undefined, undefined, 'ERR_NETWORK')
    expect(getErrorMessage(err)).toBe(
      'Ошибка сети. Проверьте подключение к интернету',
    )
  })

  it('prefers detail string over HTTP status mapping', () => {
    const err = makeAxiosError(401, 'Token expired')
    expect(getErrorMessage(err)).toBe('Token expired')
  })

  it('ignores non-string detail and falls back to status mapping', () => {
    const err = makeAxiosError(422, { msg: 'validation' })
    expect(getErrorMessage(err)).toBe('Ошибка валидации данных')
  })

  it('returns error.message for regular Error', () => {
    const err = new Error('Something broke')
    expect(getErrorMessage(err)).toBe('Something broke')
  })

  it('returns default fallback for unknown error types', () => {
    expect(getErrorMessage('some string')).toBe('Произошла ошибка')
    expect(getErrorMessage(42)).toBe('Произошла ошибка')
    expect(getErrorMessage(null)).toBe('Произошла ошибка')
  })

  it('returns custom fallback when provided', () => {
    expect(getErrorMessage('unknown', 'Ошибка входа')).toBe('Ошибка входа')
  })
})
