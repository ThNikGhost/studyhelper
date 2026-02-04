import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { LogOut, Calendar, BookOpen, ClipboardList, Users, GraduationCap } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { user, logout } = useAuthStore()

  const handleLogout = async () => {
    await logout()
  }

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
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">StudyHelper</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user?.name}
            </span>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">
            Привет, {user?.name}!
          </h2>
          <p className="text-muted-foreground">
            Что будем делать сегодня?
          </p>
        </div>

        {/* Quick actions grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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

        {/* Widgets placeholder */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Текущая пара</CardTitle>
              <CardDescription>Сейчас или следующая</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-sm">
                Загрузите расписание для отображения
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ближайшие дедлайны</CardTitle>
              <CardDescription>На этой неделе</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground text-sm">
                Добавьте работы для отображения дедлайнов
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
