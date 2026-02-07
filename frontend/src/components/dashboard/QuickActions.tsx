import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Calendar,
  BookOpen,
  ClipboardList,
  Users,
  GraduationCap,
} from 'lucide-react'
import { Link } from 'react-router-dom'

const menuItems = [
  {
    title: 'Расписание',
    description: 'Просмотр расписания занятий',
    icon: Calendar,
    href: '/schedule',
    color: 'text-blue-500',
  },
  {
    title: 'Предметы',
    description: 'Список предметов семестра',
    icon: BookOpen,
    href: '/subjects',
    color: 'text-green-500',
  },
  {
    title: 'Работы',
    description: 'Задания и дедлайны',
    icon: ClipboardList,
    href: '/works',
    color: 'text-orange-500',
  },
  {
    title: 'Одногруппники',
    description: 'Контакты группы',
    icon: Users,
    href: '/classmates',
    color: 'text-purple-500',
  },
  {
    title: 'Семестры',
    description: 'Управление семестрами',
    icon: GraduationCap,
    href: '/semesters',
    color: 'text-cyan-500',
  },
] as const

export function QuickActions() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {menuItems.map((item) => (
        <Link key={item.href} to={item.href}>
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader className="pb-2">
              <item.icon className={`h-8 w-8 ${item.color}`} />
            </CardHeader>
            <CardContent>
              <CardTitle className="text-lg">{item.title}</CardTitle>
              <CardDescription>{item.description}</CardDescription>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}
