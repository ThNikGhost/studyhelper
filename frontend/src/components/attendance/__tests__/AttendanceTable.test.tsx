import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { AttendanceTable } from '../AttendanceTable'
import type { AttendanceEntry } from '@/types/attendance'

const testEntries: AttendanceEntry[] = [
  {
    id: 1,
    lesson_date: '2026-02-05',
    subject_name: 'Математический анализ',
    lesson_type: 'lecture',
    start_time: '10:30:00',
    end_time: '12:05:00',
    teacher_name: 'Иванов И.И.',
    room: '301',
    subject_id: 1,
    is_absent: false,
    absence_id: null,
  },
  {
    id: 2,
    lesson_date: '2026-02-05',
    subject_name: 'Физика',
    lesson_type: 'lecture',
    start_time: '08:30:00',
    end_time: '10:05:00',
    teacher_name: 'Петров П.П.',
    room: '201',
    subject_id: 2,
    is_absent: true,
    absence_id: 10,
  },
]

describe('AttendanceTable', () => {
  it('renders entries', () => {
    render(<AttendanceTable entries={testEntries} onToggle={() => {}} />)

    expect(screen.getByText('Математический анализ')).toBeInTheDocument()
    expect(screen.getByText('Физика')).toBeInTheDocument()
  })

  it('renders dates', () => {
    render(<AttendanceTable entries={testEntries} onToggle={() => {}} />)

    expect(screen.getAllByText('2026-02-05')).toHaveLength(2)
  })

  it('shows "Был" for present entries', () => {
    render(<AttendanceTable entries={testEntries} onToggle={() => {}} />)

    expect(screen.getByText('Был')).toBeInTheDocument()
  })

  it('shows "Н/Б" for absent entries', () => {
    render(<AttendanceTable entries={testEntries} onToggle={() => {}} />)

    expect(screen.getByText('Н/Б')).toBeInTheDocument()
  })

  it('calls onToggle when clicking present button', () => {
    const onToggle = vi.fn()
    render(<AttendanceTable entries={testEntries} onToggle={onToggle} />)

    const presentBtn = screen.getByLabelText(/Отметить пропуск на Математический анализ/)
    fireEvent.click(presentBtn)

    expect(onToggle).toHaveBeenCalledWith(1, false)
  })

  it('calls onToggle when clicking absent button', () => {
    const onToggle = vi.fn()
    render(<AttendanceTable entries={testEntries} onToggle={onToggle} />)

    const absentBtn = screen.getByLabelText(/Отметить присутствие на Физика/)
    fireEvent.click(absentBtn)

    expect(onToggle).toHaveBeenCalledWith(2, true)
  })

  it('shows empty message when no entries', () => {
    render(<AttendanceTable entries={[]} onToggle={() => {}} />)

    expect(screen.getByText('Нет прошедших занятий')).toBeInTheDocument()
  })
})
