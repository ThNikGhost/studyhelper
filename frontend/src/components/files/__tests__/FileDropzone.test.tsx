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

    expect(screen.getByText(/Перетащите файлы/)).toBeInTheDocument()
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

  it('allows selecting multiple files', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file1 = new window.File(['hello'], 'notes.pdf', { type: 'application/pdf' })
    const file2 = new window.File(['world'], 'slides.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file1, file2] } })

    expect(screen.getByText('notes.pdf')).toBeInTheDocument()
    expect(screen.getByText('slides.pdf')).toBeInTheDocument()
    expect(screen.getByText('Загрузить (2)')).toBeInTheDocument()
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

  it('calls onUpload with file array', async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined)
    renderDropzone({ onUpload })

    const input = screen.getByTestId('file-input')
    const file = new window.File(['test'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file] } })

    fireEvent.click(screen.getByText('Загрузить'))

    await vi.waitFor(() => {
      expect(onUpload).toHaveBeenCalledWith([file], expect.any(String), null)
    })
  })

  it('can remove individual file from queue', () => {
    renderDropzone()

    const input = screen.getByTestId('file-input')
    const file1 = new window.File(['hello'], 'notes.pdf', { type: 'application/pdf' })
    const file2 = new window.File(['world'], 'slides.pdf', { type: 'application/pdf' })
    fireEvent.change(input, { target: { files: [file1, file2] } })

    expect(screen.getByText('notes.pdf')).toBeInTheDocument()
    expect(screen.getByText('slides.pdf')).toBeInTheDocument()

    fireEvent.click(screen.getByLabelText('Убрать файл notes.pdf'))

    expect(screen.queryByText('notes.pdf')).not.toBeInTheDocument()
    expect(screen.getByText('slides.pdf')).toBeInTheDocument()
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

    fireEvent.click(screen.getByLabelText('Убрать файл test.pdf'))
    expect(screen.queryByText('test.pdf')).not.toBeInTheDocument()
  })
})
