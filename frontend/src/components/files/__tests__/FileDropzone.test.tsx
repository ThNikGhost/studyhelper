import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FileDropzone } from '../FileDropzone'
import type { Subject } from '@/types/subject'

const testSubjects: Subject[] = [
  {
    id: 1,
    name: 'Математика',
    short_name: 'Матем',
    description: null,
    semester_id: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
]

function renderDropzone(props: Partial<Parameters<typeof FileDropzone>[0]> = {}) {
  const defaultProps = {
    subjects: testSubjects,
    onUpload: vi.fn().mockResolvedValue(undefined),
    disabled: false,
    uploadProgress: null,
    ...props,
  }
  return render(<FileDropzone {...defaultProps} />)
}

describe('FileDropzone', () => {
  it('renders dropzone area', () => {
    renderDropzone()

    expect(screen.getByText(/Перетащите файл/)).toBeInTheDocument()
    expect(screen.getByText(/до 50 MB/)).toBeInTheDocument()
  })

  it('shows file preview after selection', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file = new window.File(['hello'], 'notes.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByText('notes.pdf')).toBeInTheDocument()
    expect(screen.getByText('5 B')).toBeInTheDocument()
  })

  it('shows category and subject selects after file selection', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file = new window.File(['test'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByLabelText('Категория файла')).toBeInTheDocument()
    expect(screen.getByLabelText('Предмет')).toBeInTheDocument()
    expect(screen.getByText('Загрузить')).toBeInTheDocument()
  })

  it('rejects invalid file type', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file = new window.File(['test'], 'virus.exe', { type: 'application/x-msdownload' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByRole('alert')).toHaveTextContent(/Недопустимый тип файла/)
  })

  it('rejects oversized file', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    // Simulate 51 MB file object (we only check .size property)
    const file = new window.File(['x'], 'big.pdf', { type: 'application/pdf' })
    Object.defineProperty(file, 'size', { value: 51 * 1024 * 1024 })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByRole('alert')).toHaveTextContent(/слишком большой/)
  })

  it('shows upload progress bar', () => {
    renderDropzone({ uploadProgress: 45 })

    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '45')
    expect(screen.getByText('Загрузка...')).toBeInTheDocument()
  })

  it('is disabled when offline', () => {
    renderDropzone({ disabled: true })

    const dropzone = screen.getByTestId('dropzone')
    expect(dropzone.className).toContain('opacity-50')
  })

  it('clears selected file when X is clicked', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file = new window.File(['test'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file] } })

    expect(screen.getByText('test.pdf')).toBeInTheDocument()

    fireEvent.click(screen.getByLabelText('Убрать файл'))
    expect(screen.queryByText('test.pdf')).not.toBeInTheDocument()
  })
})
