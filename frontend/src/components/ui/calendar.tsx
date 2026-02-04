import * as React from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { DayPicker } from 'react-day-picker'
import { ru } from 'date-fns/locale'

import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'
import { Button } from '@/components/ui/button'

export type CalendarProps = React.ComponentProps<typeof DayPicker> & {
  onTodayClick?: () => void
  showTodayButton?: boolean
}

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  onTodayClick,
  showTodayButton = true,
  ...props
}: CalendarProps) {
  return (
    <div className="flex flex-col">
      <DayPicker
        showOutsideDays={showOutsideDays}
        className={cn('p-3', className)}
        locale={ru}
        classNames={{
          months: 'flex flex-col sm:flex-row gap-2',
          month: 'flex flex-col gap-4 relative',
          month_caption: 'flex justify-center pt-1 relative items-center w-full',
          caption_label: 'text-sm font-medium',
          nav: 'absolute inset-x-0 top-4 flex justify-between items-center px-1 z-10',
          button_previous: cn(
            buttonVariants({ variant: 'outline' }),
            'h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100'
          ),
          button_next: cn(
            buttonVariants({ variant: 'outline' }),
            'h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100'
          ),
          month_grid: 'w-full border-collapse',
          weekdays: 'flex',
          weekday: 'text-muted-foreground rounded-md w-9 font-normal text-[0.8rem] text-center',
          week: 'flex w-full mt-2',
          day: 'h-9 w-9 text-center text-sm p-0 relative',
          day_button: cn(
            buttonVariants({ variant: 'ghost' }),
            'h-9 w-9 p-0 font-normal aria-selected:opacity-100 hover:bg-accent hover:text-accent-foreground'
          ),
          selected: 'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground',
          today: 'ring-2 ring-primary ring-offset-1',
          outside: 'text-muted-foreground opacity-50',
          disabled: 'text-muted-foreground opacity-50',
          hidden: 'invisible',
          ...classNames,
        }}
        components={{
          Chevron: ({ orientation }) => {
            if (orientation === 'left') {
              return <ChevronLeft className="h-4 w-4" />
            }
            return <ChevronRight className="h-4 w-4" />
          },
        }}
        {...props}
      />
      {showTodayButton && onTodayClick && (
        <div className="px-3 pb-3 pt-0">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={onTodayClick}
          >
            Сегодня
          </Button>
        </div>
      )}
    </div>
  )
}
Calendar.displayName = 'Calendar'

export { Calendar }
