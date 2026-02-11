import { useQuery } from '@tanstack/react-query'
import { Settings, Dumbbell, Users, Building2, Check } from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useSettingsStore } from '@/stores/settingsStore'
import { scheduleService } from '@/services/scheduleService'
import { getSubgroupsFromWeek } from '@/lib/subgroupFilter'
import { getPeTeachersFromWeek } from '@/lib/peTeacherFilter'

export default function SettingsPage() {
  const { subgroup, peTeacher, setSubgroup, setPeTeacher } = useSettingsStore()

  // Fetch schedule to get available subgroups and PE teachers
  const { data: weekSchedule } = useQuery({
    queryKey: ['schedule', 'week'],
    queryFn: () => scheduleService.getWeekSchedule(),
    staleTime: 1000 * 60 * 5,
  })

  const availableSubgroups = weekSchedule ? getSubgroupsFromWeek(weekSchedule) : []
  const availablePeTeachers = weekSchedule ? getPeTeachersFromWeek(weekSchedule) : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Settings className="h-8 w-8 text-gray-500" />
        <div>
          <h1 className="text-2xl font-bold">Настройки</h1>
          <p className="text-muted-foreground">Персональные настройки приложения</p>
        </div>
      </div>

      {/* Subgroup Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-500" />
            <CardTitle>Подгруппа</CardTitle>
          </div>
          <CardDescription>
            Фильтрует расписание по вашей подгруппе. Общие занятия (без подгруппы) отображаются всегда.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              variant={subgroup === null ? 'default' : 'outline'}
              onClick={() => setSubgroup(null)}
              className="gap-2"
            >
              {subgroup === null && <Check className="h-4 w-4" />}
              Все подгруппы
            </Button>
            {availableSubgroups.length > 0 ? (
              availableSubgroups.map((sg) => (
                <Button
                  key={sg}
                  variant={subgroup === sg ? 'default' : 'outline'}
                  onClick={() => setSubgroup(sg)}
                  className="gap-2"
                >
                  {subgroup === sg && <Check className="h-4 w-4" />}
                  {sg} подгруппа
                </Button>
              ))
            ) : (
              <>
                <Button
                  variant={subgroup === 1 ? 'default' : 'outline'}
                  onClick={() => setSubgroup(1)}
                  className="gap-2"
                >
                  {subgroup === 1 && <Check className="h-4 w-4" />}
                  1 подгруппа
                </Button>
                <Button
                  variant={subgroup === 2 ? 'default' : 'outline'}
                  onClick={() => setSubgroup(2)}
                  className="gap-2"
                >
                  {subgroup === 2 && <Check className="h-4 w-4" />}
                  2 подгруппа
                </Button>
              </>
            )}
          </div>
          {subgroup !== null && (
            <p className="mt-3 text-sm text-muted-foreground">
              Выбрана {subgroup} подгруппа. Занятия для других подгрупп будут помечены значком "!".
            </p>
          )}
        </CardContent>
      </Card>

      {/* PE Teacher Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Dumbbell className="h-5 w-5 text-green-500" />
            <CardTitle>Физкультура</CardTitle>
          </div>
          <CardDescription>
            Выберите вашего преподавателя для занятий по физкультуре.
            В расписании несколько преподавателей на одно время — выберите своего.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {availablePeTeachers.length > 0 ? (
            <div className="space-y-2">
              <Button
                variant={peTeacher === null ? 'default' : 'outline'}
                onClick={() => setPeTeacher(null)}
                className="w-full justify-start gap-2"
              >
                {peTeacher === null && <Check className="h-4 w-4" />}
                Показать всех преподавателей
              </Button>
              {availablePeTeachers.map((teacher) => (
                <Button
                  key={teacher}
                  variant={peTeacher === teacher ? 'default' : 'outline'}
                  onClick={() => setPeTeacher(teacher)}
                  className="w-full justify-start gap-2"
                >
                  {peTeacher === teacher && <Check className="h-4 w-4" />}
                  <span className="truncate">{teacher}</span>
                </Button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Преподаватели физкультуры будут доступны после загрузки расписания.
            </p>
          )}
          {peTeacher && (
            <p className="mt-3 text-sm text-muted-foreground">
              Выбран: {peTeacher}
            </p>
          )}
        </CardContent>
      </Card>

      {/* OmSU Integration Section (placeholder) */}
      <Card className="opacity-60">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-purple-500" />
            <CardTitle>Личный кабинет ОмГУ</CardTitle>
          </div>
          <CardDescription>
            Интеграция с личным кабинетом ОмГУ для автоматического отслеживания успеваемости.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="omsu-login">Логин</Label>
              <Input
                id="omsu-login"
                placeholder="your.login"
                disabled
                className="max-w-sm"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="omsu-password">Пароль</Label>
              <Input
                id="omsu-password"
                type="password"
                placeholder="••••••••"
                disabled
                className="max-w-sm"
              />
            </div>
            <p className="text-sm text-amber-600 dark:text-amber-400">
              🚧 Интеграция с ЛК ОмГУ — скоро
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Navigation back */}
      <div className="pt-4">
        <Link to="/">
          <Button variant="outline">← На главную</Button>
        </Link>
      </div>
    </div>
  )
}
