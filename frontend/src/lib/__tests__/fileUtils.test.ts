import { describe, it, expect } from 'vitest'
import { formatFileSize, getFileIcon, isAllowedFileType } from '../fileUtils'
import { FileText, FileSpreadsheet, Presentation, Image, File } from 'lucide-react'

describe('formatFileSize', () => {
  it('formats 0 bytes', () => {
    expect(formatFileSize(0)).toBe('0 B')
  })

  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('formats kilobytes', () => {
    expect(formatFileSize(1024)).toBe('1 KB')
  })

  it('formats kilobytes with decimal', () => {
    expect(formatFileSize(1536)).toBe('1.5 KB')
  })

  it('formats megabytes', () => {
    expect(formatFileSize(1024 * 1024)).toBe('1 MB')
  })

  it('formats megabytes with decimal', () => {
    expect(formatFileSize(2.5 * 1024 * 1024)).toBe('2.5 MB')
  })

  it('formats gigabytes', () => {
    expect(formatFileSize(1024 * 1024 * 1024)).toBe('1 GB')
  })

  it('formats large values in GB', () => {
    expect(formatFileSize(5.3 * 1024 * 1024 * 1024)).toBe('5.3 GB')
  })
})

describe('getFileIcon', () => {
  it('returns FileText for PDF', () => {
    expect(getFileIcon('application/pdf')).toBe(FileText)
  })

  it('returns Image for images', () => {
    expect(getFileIcon('image/png')).toBe(Image)
    expect(getFileIcon('image/jpeg')).toBe(Image)
    expect(getFileIcon('image/gif')).toBe(Image)
  })

  it('returns FileSpreadsheet for Excel', () => {
    expect(getFileIcon('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')).toBe(FileSpreadsheet)
    expect(getFileIcon('application/vnd.ms-excel')).toBe(FileSpreadsheet)
  })

  it('returns Presentation for PowerPoint', () => {
    expect(getFileIcon('application/vnd.openxmlformats-officedocument.presentationml.presentation')).toBe(Presentation)
    expect(getFileIcon('application/vnd.ms-powerpoint')).toBe(Presentation)
  })

  it('returns FileText for Word', () => {
    expect(getFileIcon('application/msword')).toBe(FileText)
    expect(getFileIcon('application/vnd.openxmlformats-officedocument.wordprocessingml.document')).toBe(FileText)
  })

  it('returns generic File for unknown types', () => {
    expect(getFileIcon('application/octet-stream')).toBe(File)
  })
})

describe('isAllowedFileType', () => {
  it('accepts PDF by MIME type', () => {
    const file = new window.File(['test'], 'doc.pdf', { type: 'application/pdf' })
    expect(isAllowedFileType(file)).toBe(true)
  })

  it('accepts PNG by MIME type', () => {
    const file = new window.File(['test'], 'img.png', { type: 'image/png' })
    expect(isAllowedFileType(file)).toBe(true)
  })

  it('accepts DOCX by MIME type', () => {
    const file = new window.File(['test'], 'doc.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    expect(isAllowedFileType(file)).toBe(true)
  })

  it('rejects EXE by MIME type', () => {
    const file = new window.File(['test'], 'app.exe', { type: 'application/x-msdownload' })
    expect(isAllowedFileType(file)).toBe(false)
  })

  it('accepts by extension when MIME is empty', () => {
    const file = new window.File(['test'], 'doc.pdf', { type: '' })
    expect(isAllowedFileType(file)).toBe(true)
  })

  it('rejects unknown extension and type', () => {
    const file = new window.File(['test'], 'file.xyz', { type: '' })
    expect(isAllowedFileType(file)).toBe(false)
  })
})
