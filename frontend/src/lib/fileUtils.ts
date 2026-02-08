import {
  FileText,
  FileSpreadsheet,
  Presentation,
  Image,
  File,
  type LucideIcon,
} from 'lucide-react'

export const MAX_FILE_SIZE_MB = 50
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

export const ALLOWED_EXTENSIONS = [
  'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
  'jpg', 'jpeg', 'png', 'gif', 'webp',
]

const ALLOWED_MIME_TYPES = new Set([
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
])

/** Format file size in human-readable form. */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const k = 1024
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  const index = Math.min(i, units.length - 1)
  const value = bytes / Math.pow(k, index)
  return `${value % 1 === 0 ? value : value.toFixed(1)} ${units[index]}`
}

/** Get lucide-react icon component by MIME type. */
export function getFileIcon(mimeType: string): LucideIcon {
  if (mimeType === 'application/pdf') return FileText
  if (mimeType.startsWith('image/')) return Image
  if (
    mimeType.includes('spreadsheet') ||
    mimeType.includes('excel') ||
    mimeType === 'application/vnd.ms-excel'
  ) {
    return FileSpreadsheet
  }
  if (
    mimeType.includes('presentation') ||
    mimeType.includes('powerpoint') ||
    mimeType === 'application/vnd.ms-powerpoint'
  ) {
    return Presentation
  }
  if (
    mimeType.includes('word') ||
    mimeType === 'application/msword'
  ) {
    return FileText
  }
  return File
}

/** Check if a File object has an allowed type. */
export function isAllowedFileType(file: File): boolean {
  // Check MIME type
  if (file.type && ALLOWED_MIME_TYPES.has(file.type)) return true

  // Fallback: check extension
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext && ALLOWED_EXTENSIONS.includes(ext)) return true

  return false
}
