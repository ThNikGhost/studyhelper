import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressBar } from '../progress-bar'

describe('ProgressBar', () => {
  it('renders progressbar with correct aria attributes', () => {
    render(<ProgressBar value={50} />)

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveAttribute('aria-valuenow', '50')
    expect(bar).toHaveAttribute('aria-valuemin', '0')
    expect(bar).toHaveAttribute('aria-valuemax', '100')
  })

  it('renders with 0% width at value 0', () => {
    render(<ProgressBar value={0} />)

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveStyle({ width: '0%' })
  })

  it('renders with 100% width at value 100', () => {
    render(<ProgressBar value={100} />)

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveStyle({ width: '100%' })
  })

  it('clamps value above 100 to 100', () => {
    render(<ProgressBar value={150} />)

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveAttribute('aria-valuenow', '100')
    expect(bar).toHaveStyle({ width: '100%' })
  })

  it('clamps negative value to 0', () => {
    render(<ProgressBar value={-10} />)

    const bar = screen.getByRole('progressbar')
    expect(bar).toHaveAttribute('aria-valuenow', '0')
    expect(bar).toHaveStyle({ width: '0%' })
  })

  it('shows label when showLabel is true', () => {
    render(<ProgressBar value={42} showLabel />)

    expect(screen.getByText('42%')).toBeInTheDocument()
  })

  it('does not show label by default', () => {
    render(<ProgressBar value={42} />)

    expect(screen.queryByText('42%')).not.toBeInTheDocument()
  })

  it('applies custom color class to the fill bar', () => {
    render(<ProgressBar value={50} color="bg-green-500" />)

    const bar = screen.getByRole('progressbar')
    expect(bar.className).toContain('bg-green-500')
  })
})
