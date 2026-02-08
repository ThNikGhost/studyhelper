import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FileList } from '../FileList'
import { testFiles } from '@/test/mocks/handlers'

describe('FileList', () => {
  it('renders file list', () => {
    render(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Лекция_01.pdf')).toBeInTheDocument()
    expect(screen.getByText('Задачник.docx')).toBeInTheDocument()
    expect(screen.getByText('Шпаргалка.png')).toBeInTheDocument()
  })

  it('shows empty state when no files', () => {
    render(<FileList files={[]} onDelete={vi.fn()} />)

    expect(screen.getByText('Файлов пока нет')).toBeInTheDocument()
  })

  it('displays file size', () => {
    render(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('2 MB')).toBeInTheDocument()
    expect(screen.getByText('512 KB')).toBeInTheDocument()
  })

  it('displays category badge', () => {
    render(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Лекция')).toBeInTheDocument()
    expect(screen.getByText('Задачник')).toBeInTheDocument()
    expect(screen.getByText('Шпаргалка')).toBeInTheDocument()
  })

  it('displays subject name when available', () => {
    render(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Физика')).toBeInTheDocument()
  })

  it('has download link for each file', () => {
    render(<FileList files={testFiles} onDelete={vi.fn()} />)

    const downloadLinks = screen.getAllByLabelText(/Скачать/)
    expect(downloadLinks).toHaveLength(3)
    expect(downloadLinks[0]).toHaveAttribute('href', '/api/v1/files/1/download')
  })

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = vi.fn()
    render(<FileList files={testFiles} onDelete={onDelete} />)

    const deleteButtons = screen.getAllByLabelText(/Удалить/)
    fireEvent.click(deleteButtons[0])

    expect(onDelete).toHaveBeenCalledWith(testFiles[0])
  })
})
