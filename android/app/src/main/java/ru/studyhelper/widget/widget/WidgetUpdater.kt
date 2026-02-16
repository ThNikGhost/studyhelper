package ru.studyhelper.widget.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.view.View
import android.widget.RemoteViews
import ru.studyhelper.widget.R
import ru.studyhelper.widget.data.WidgetDisplayData
import ru.studyhelper.widget.data.WidgetRepository
import ru.studyhelper.widget.ui.ConfigActivity

/**
 * Builds RemoteViews for the widget based on current data state.
 */
object WidgetUpdater {

    private val WEEKDAYS_SHORT = arrayOf("Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб")
    private val MONTHS_SHORT = arrayOf(
        "янв", "фев", "мар", "апр", "май", "июн",
        "июл", "авг", "сен", "окт", "ноя", "дек",
    )

    /**
     * Update a single widget by ID.
     */
    fun update(context: Context, appWidgetId: Int) {
        val data = WidgetRepository.getNextLesson(context)
        val views = buildRemoteViews(context, data)

        // Tap widget → open ConfigActivity
        val intent = Intent(context, ConfigActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        views.setOnClickPendingIntent(R.id.widgetRoot, pendingIntent)

        AppWidgetManager.getInstance(context).updateAppWidget(appWidgetId, views)
    }

    /**
     * Update all widget instances.
     */
    fun updateAll(context: Context) {
        val manager = AppWidgetManager.getInstance(context)
        val component = ComponentName(context, ScheduleWidgetProvider::class.java)
        val ids = manager.getAppWidgetIds(component)
        for (id in ids) {
            update(context, id)
        }
    }

    private fun buildRemoteViews(context: Context, data: WidgetDisplayData): RemoteViews {
        val views = RemoteViews(context.packageName, R.layout.widget_layout)

        when (data) {
            is WidgetDisplayData.NoKey -> {
                views.setTextViewText(R.id.textHeader, "")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_key))
                views.setTextViewText(R.id.textType, "")
                views.setTextViewText(R.id.textTime, "")
                views.setTextViewText(R.id.textLocation, "")
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_tap_to_setup))
                views.setTextColor(R.id.textSubject, 0xFF8b8ba7.toInt())
                views.setTextColor(R.id.textCountdown, 0xFF6c9eff.toInt())
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
            }

            is WidgetDisplayData.NoData -> {
                views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_data))
                views.setTextViewText(R.id.textType, "")
                views.setTextViewText(R.id.textTime, "")
                views.setTextViewText(R.id.textLocation, "")
                views.setTextViewText(R.id.textCountdown, "")
                views.setTextColor(R.id.textSubject, 0xFF8b8ba7.toInt())
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setViewVisibility(R.id.textCountdown, View.GONE)
            }

            is WidgetDisplayData.NoLessons -> {
                views.setTextViewText(R.id.textHeader, "STUDYHELPER")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_lessons))
                views.setTextViewText(R.id.textType, "")
                views.setTextViewText(R.id.textTime, "")
                views.setTextViewText(R.id.textLocation, "")
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_no_lessons_sub))
                views.setTextColor(R.id.textSubject, 0xFFFFFFFF.toInt())
                views.setTextColor(R.id.textCountdown, 0xFF8b8ba7.toInt())
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
            }

            is WidgetDisplayData.Lesson -> {
                views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
                views.setTextViewText(R.id.textSubject, data.subject)
                views.setTextColor(R.id.textSubject, 0xFFFFFFFF.toInt())

                // Lesson type with color
                views.setTextViewText(R.id.textType, data.lessonType)
                views.setTextColor(R.id.textType, getLessonTypeColor(data.lessonType))
                views.setViewVisibility(R.id.textType, View.VISIBLE)

                // Time
                val timeStr = "${data.timeStart} – ${data.timeEnd}"
                views.setTextViewText(R.id.textTime, timeStr)
                views.setViewVisibility(R.id.textTime, View.VISIBLE)

                // Location
                if (data.location != null) {
                    views.setTextViewText(R.id.textLocation, data.location)
                    views.setViewVisibility(R.id.textLocation, View.VISIBLE)
                } else {
                    views.setViewVisibility(R.id.textLocation, View.GONE)
                }

                // Countdown or future date
                if (data.isToday && data.minutesUntil != null) {
                    views.setTextViewText(R.id.textCountdown, formatMinutesUntil(data.minutesUntil))
                    views.setTextColor(R.id.textCountdown, 0xFF4ade80.toInt()) // green
                    views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
                } else if (data.futureDate != null) {
                    views.setTextViewText(R.id.textCountdown, formatDateShort(data.futureDate))
                    views.setTextColor(R.id.textCountdown, 0xFFfbbf24.toInt()) // yellow
                    views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
                } else {
                    views.setViewVisibility(R.id.textCountdown, View.GONE)
                }
            }
        }

        return views
    }

    private fun getLessonTypeColor(type: String): Int = when {
        type.contains("Лекция", ignoreCase = true) -> 0xFF6c9eff.toInt()
        type.contains("Практ", ignoreCase = true) ||
            type.contains("Семинар", ignoreCase = true) -> 0xFF4ade80.toInt()
        type.contains("Лаб", ignoreCase = true) -> 0xFFc084fc.toInt()
        else -> 0xFFfbbf24.toInt()
    }

    private fun formatMinutesUntil(minutes: Int): String {
        if (minutes <= 0) return "Сейчас"
        if (minutes < 60) return "через $minutes мин"
        val hours = minutes / 60
        val mins = minutes % 60
        return if (mins > 0) "через $hours ч $mins мин" else "через $hours ч"
    }

    private fun formatDateShort(dateStr: String): String {
        return try {
            val parts = dateStr.split("-")
            val year = parts[0].toInt()
            val month = parts[1].toInt() - 1
            val day = parts[2].toInt()

            val cal = java.util.Calendar.getInstance()
            cal.set(year, month, day)
            val wd = WEEKDAYS_SHORT[cal.get(java.util.Calendar.DAY_OF_WEEK) - 1]
            val mon = MONTHS_SHORT[month]
            "$wd, $day $mon"
        } catch (_: Exception) {
            dateStr
        }
    }
}
