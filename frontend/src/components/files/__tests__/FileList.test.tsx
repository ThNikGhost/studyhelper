import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { FileList } from '../FileList'
import { testFiles } from '@/test/mocks/handlers'
import { fileService } from '@/services/fileService'

vi.mock('@/services/fileService', () => ({
  fileService: {
    downloadFile: vi.fn(),
    openFile: vi.fn(),
    updateFileCategory: vi.fn(),
  },
}))

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>)
}

describe('FileList', () => {
  it('renders file list', () => {
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Лекция_01.pdf')).toBeInTheDocument()
    expect(screen.getByText('Задачник.docx')).toBeInTheDocument()
    expect(screen.getByText('Шпаргалка.png')).toBeInTheDocument()
  })

  it('shows empty state when no files', () => {
    renderWithClient(<FileList files={[]} onDelete={vi.fn()} />)

    expect(screen.getByText('Файлов пока нет')).toBeInTheDocument()
  })

  it('displays file size', () => {
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('2 MB')).toBeInTheDocument()
    expect(screen.getByText('512 KB')).toBeInTheDocument()
  })

  it('displays category badge', () => {
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Лекция')).toBeInTheDocument()
    expect(screen.getByText('Задачник')).toBeInTheDocument()
    expect(screen.getByText('Шпаргалка')).toBeInTheDocument()
  })

  it('displays subject name when available', () => {
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Физика')).toBeInTheDocument()
  })

  it('calls downloadFile when download button is clicked', async () => {
    vi.mocked(fileService.downloadFile).mockResolvedValue()
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    const downloadButtons = screen.getAllByLabelText(/Скачать/)
    expect(downloadButtons).toHaveLength(3)

    fireEvent.click(downloadButtons[0])

    await waitFor(() => {
      expect(fileService.downloadFile).toHaveBeenCalledWith(
        testFiles[0].id,
        testFiles[0].filename,
      )
    })
  })

  it('shows error toast on download failure', async () => {
    const { toast } = await import('sonner')
    vi.mocked(fileService.downloadFile).mockRejectedValue(new Error('Network error'))
    renderWithClient(<FileList files={testFiles} onDelete={vi.fn()} />)

    const downloadButtons = screen.getAllByLabelText(/Скачать/)
    fireEvent.click(downloadButtons[0])

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled()
    })
  })

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = vi.fn()
    renderWithClient(<FileList files={testFiles} onDelete={onDelete} />)

    const deleteButtons = screen.getAllByLabelText(/Удалить/)
    fireEvent.click(deleteButtons[0])

    expect(onDelete).toHaveBeenCalledWith(testFiles[0])
  })
})
