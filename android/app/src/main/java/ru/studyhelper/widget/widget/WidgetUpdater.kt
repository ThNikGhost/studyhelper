package ru.studyhelper.widget.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.RemoteViews
import androidx.core.content.ContextCompat
import ru.studyhelper.widget.R
import ru.studyhelper.widget.data.FileLogger
import ru.studyhelper.widget.data.LessonBrief
import ru.studyhelper.widget.data.WidgetDisplayData
import ru.studyhelper.widget.data.WidgetRepository
import ru.studyhelper.widget.ui.ConfigActivity

/**
 * Builds RemoteViews for the widget based on current data state and widget size.
 * Supports three sizes: SMALL (2x1), MEDIUM (2x2), LARGE (4x2).
 */
object WidgetUpdater {

    private const val TAG = "SH_WidgetUpdater"

    private val WEEKDAYS_SHORT = arrayOf("Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб")
    private val MONTHS_SHORT = arrayOf(
        "янв", "фев", "мар", "апр", "май", "июн",
        "июл", "авг", "сен", "окт", "ноя", "дек",
    )

    /** Widget size categories based on dp dimensions. */
    enum class WidgetSize { SMALL, MEDIUM, LARGE }

    /**
     * Determine widget size from AppWidgetOptions bundle.
     * Uses MAX_WIDTH/HEIGHT with fallback to MIN_WIDTH/HEIGHT.
     */
    private fun determineSize(options: Bundle?): WidgetSize {
        if (options == null) return WidgetSize.LARGE
        val maxW = options.getInt(AppWidgetManager.OPTION_APPWIDGET_MAX_WIDTH, 0)
        val maxH = options.getInt(AppWidgetManager.OPTION_APPWIDGET_MAX_HEIGHT, 0)
        val w = if (maxW > 0) maxW else options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH, 250)
        val h = if (maxH > 0) maxH else options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 110)
        Log.d(TAG, "Widget dimensions: w=$w, h=$h (maxW=$maxW, maxH=$maxH)")
        return when {
            w >= 250 && h >= 100 -> WidgetSize.LARGE
            h >= 100 -> WidgetSize.MEDIUM
            else -> WidgetSize.SMALL
        }
    }

    /**
     * Update a single widget by ID.
     */
    fun update(context: Context, appWidgetId: Int) {
        FileLogger.log(context, TAG, "update($appWidgetId) start")
        val manager = AppWidgetManager.getInstance(context)
        val options = manager.getAppWidgetOptions(appWidgetId)
        val size = determineSize(options)
        FileLogger.log(context, TAG, "update($appWidgetId) size=$size")
        val data = WidgetRepository.getNextLesson(context)
        FileLogger.log(context, TAG, "update($appWidgetId) data=${data.javaClass.simpleName}")

        val views = when (size) {
            WidgetSize.SMALL -> buildSmallViews(context, data)
            WidgetSize.MEDIUM -> buildMediumViews(context, data)
            WidgetSize.LARGE -> buildLargeViews(context, data)
        }

        // Tap widget -> open ConfigActivity
        val intent = Intent(context, ConfigActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        views.setOnClickPendingIntent(R.id.widgetRoot, pendingIntent)

        // Accessibility
        val description = buildContentDescription(context, data)
        views.setContentDescription(R.id.widgetRoot, description)

        manager.updateAppWidget(appWidgetId, views)
        FileLogger.log(context, TAG, "update($appWidgetId) done")
    }

    /**
     * Update all widget instances.
     */
    fun updateAll(context: Context) {
        val manager = AppWidgetManager.getInstance(context)
        val component = ComponentName(context, ScheduleWidgetProvider::class.java)
        val ids = manager.getAppWidgetIds(component)
        FileLogger.log(context, TAG, "updateAll: ${ids.size} widget(s) found: ${ids.toList()}")
        for (id in ids) {
            update(context, id)
        }
    }

    // ── SMALL (2×1) ────────────────────────────────────────────────────

    private fun buildSmallViews(context: Context, data: WidgetDisplayData): RemoteViews {
        val views = RemoteViews(context.packageName, R.layout.widget_layout_small)
        when (data) {
            is WidgetDisplayData.NoKey -> {
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_key))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setTextViewText(R.id.textLocation, "")
                views.setTextViewText(R.id.textTimeCompact, "")
            }
            is WidgetDisplayData.NoData -> {
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_data))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setTextViewText(R.id.textLocation, "")
                views.setTextViewText(R.id.textTimeCompact, "")
            }
            is WidgetDisplayData.NoLessons -> {
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_lessons))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))
                views.setTextViewText(R.id.textLocation, context.getString(R.string.widget_no_lessons_sub))
                views.setTextViewText(R.id.textTimeCompact, "")
            }
            is WidgetDisplayData.Lesson -> {
                views.setTextViewText(R.id.textSubject, data.subject)
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))
                views.setTextViewText(R.id.textLocation, data.location ?: "")
                views.setTextViewText(R.id.textTimeCompact, data.timeStart)
            }
        }
        return views
    }

    // ── MEDIUM (2×2) ───────────────────────────────────────────────────

    private fun buildMediumViews(context: Context, data: WidgetDisplayData): RemoteViews {
        val views = RemoteViews(context.packageName, R.layout.widget_layout_medium)
        when (data) {
            is WidgetDisplayData.NoKey -> {
                views.setTextViewText(R.id.textHeader, "")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_key))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_tap_to_setup))
                views.setTextColor(R.id.textCountdown, color(context, R.color.widget_time))
                views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
            }
            is WidgetDisplayData.NoData -> {
                views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_data))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setViewVisibility(R.id.textCountdown, View.GONE)
            }
            is WidgetDisplayData.NoLessons -> {
                views.setTextViewText(R.id.textHeader, "STUDYHELPER")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_lessons))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_no_lessons_sub))
                views.setTextColor(R.id.textCountdown, color(context, R.color.widget_muted))
                views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
            }
            is WidgetDisplayData.Lesson -> {
                applyLessonToMedium(context, views, data)
            }
        }
        return views
    }

    private fun applyLessonToMedium(
        context: Context,
        views: RemoteViews,
        data: WidgetDisplayData.Lesson,
    ) {
        views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
        views.setTextViewText(R.id.textSubject, data.subject)
        views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))

        views.setTextViewText(R.id.textType, data.lessonType)
        views.setTextColor(R.id.textType, getLessonTypeColor(context, data.lessonType))
        views.setViewVisibility(R.id.textType, View.VISIBLE)

        val timeStr = "${data.timeStart} – ${data.timeEnd}"
        views.setTextViewText(R.id.textTime, timeStr)
        views.setViewVisibility(R.id.textTime, View.VISIBLE)

        if (data.location != null) {
            views.setTextViewText(R.id.textLocation, data.location)
            views.setViewVisibility(R.id.textLocation, View.VISIBLE)
        } else {
            views.setViewVisibility(R.id.textLocation, View.GONE)
        }

        applyCountdown(context, views, data)
    }

    // ── LARGE (4×2) ────────────────────────────────────────────────────

    private fun buildLargeViews(context: Context, data: WidgetDisplayData): RemoteViews {
        val views = RemoteViews(context.packageName, R.layout.widget_layout)

        // Hide right panel by default
        views.setViewVisibility(R.id.divider, View.GONE)
        views.setViewVisibility(R.id.rightPanel, View.GONE)
        views.setViewVisibility(R.id.slot1Container, View.GONE)
        views.setViewVisibility(R.id.slot2Container, View.GONE)
        views.setViewVisibility(R.id.slot3Container, View.GONE)

        when (data) {
            is WidgetDisplayData.NoKey -> {
                views.setTextViewText(R.id.textHeader, "")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_key))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setTextViewText(R.id.textType, "")
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_tap_to_setup))
                views.setTextColor(R.id.textCountdown, color(context, R.color.widget_time))
                views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
            }
            is WidgetDisplayData.NoData -> {
                views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_data))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_muted))
                views.setTextViewText(R.id.textType, "")
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setViewVisibility(R.id.textCountdown, View.GONE)
            }
            is WidgetDisplayData.NoLessons -> {
                views.setTextViewText(R.id.textHeader, "STUDYHELPER")
                views.setTextViewText(R.id.textSubject, context.getString(R.string.widget_no_lessons))
                views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))
                views.setTextViewText(R.id.textType, "")
                views.setViewVisibility(R.id.textType, View.GONE)
                views.setViewVisibility(R.id.textTime, View.GONE)
                views.setViewVisibility(R.id.textLocation, View.GONE)
                views.setTextViewText(R.id.textCountdown, context.getString(R.string.widget_no_lessons_sub))
                views.setTextColor(R.id.textCountdown, color(context, R.color.widget_muted))
                views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
            }
            is WidgetDisplayData.Lesson -> {
                applyLessonToLarge(context, views, data)
            }
        }
        return views
    }

    private fun applyLessonToLarge(
        context: Context,
        views: RemoteViews,
        data: WidgetDisplayData.Lesson,
    ) {
        // Left panel — same as medium
        views.setTextViewText(R.id.textHeader, context.getString(R.string.widget_header))
        views.setTextViewText(R.id.textSubject, data.subject)
        views.setTextColor(R.id.textSubject, color(context, R.color.widget_subject))

        views.setTextViewText(R.id.textType, data.lessonType)
        views.setTextColor(R.id.textType, getLessonTypeColor(context, data.lessonType))
        views.setViewVisibility(R.id.textType, View.VISIBLE)

        val timeStr = "${data.timeStart} – ${data.timeEnd}"
        views.setTextViewText(R.id.textTime, timeStr)
        views.setViewVisibility(R.id.textTime, View.VISIBLE)

        if (data.location != null) {
            views.setTextViewText(R.id.textLocation, data.location)
            views.setViewVisibility(R.id.textLocation, View.VISIBLE)
        } else {
            views.setViewVisibility(R.id.textLocation, View.GONE)
        }

        applyCountdown(context, views, data)

        // Right panel — remaining lessons
        if (data.remainingLessons.isNotEmpty()) {
            views.setViewVisibility(R.id.divider, View.VISIBLE)
            views.setViewVisibility(R.id.rightPanel, View.VISIBLE)
            fillRemainingSlots(views, data.remainingLessons)
        }
    }

    /** Fill up to 3 remaining lesson slots in the large layout. */
    private fun fillRemainingSlots(views: RemoteViews, lessons: List<LessonBrief>) {
        val slots = listOf(
            Triple(R.id.slot1Container, R.id.slot1Subject, Pair(R.id.slot1Time, R.id.slot1Location)),
            Triple(R.id.slot2Container, R.id.slot2Subject, Pair(R.id.slot2Time, R.id.slot2Location)),
            Triple(R.id.slot3Container, R.id.slot3Subject, Pair(R.id.slot3Time, R.id.slot3Location)),
        )
        for ((index, lesson) in lessons.withIndex()) {
            if (index >= slots.size) break
            val (container, subjectId, timeLocPair) = slots[index]
            views.setViewVisibility(container, View.VISIBLE)
            views.setTextViewText(subjectId, lesson.subject)
            views.setTextViewText(timeLocPair.first, lesson.timeStart)
            views.setTextViewText(timeLocPair.second, lesson.location ?: "")
        }
    }

    // ── Shared helpers ─────────────────────────────────────────────────

    /** Apply countdown or future date to textCountdown view. */
    private fun applyCountdown(
        context: Context,
        views: RemoteViews,
        data: WidgetDisplayData.Lesson,
    ) {
        if (data.isToday && data.minutesUntil != null) {
            views.setTextViewText(R.id.textCountdown, formatMinutesUntil(data.minutesUntil))
            views.setTextColor(R.id.textCountdown, color(context, R.color.widget_countdown_today))
            views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
        } else if (data.futureDate != null) {
            views.setTextViewText(R.id.textCountdown, formatDateShort(data.futureDate))
            views.setTextColor(R.id.textCountdown, color(context, R.color.widget_countdown_future))
            views.setViewVisibility(R.id.textCountdown, View.VISIBLE)
        } else {
            views.setViewVisibility(R.id.textCountdown, View.GONE)
        }
    }

    private fun getLessonTypeColor(context: Context, type: String): Int = when {
        type.contains("Лекция", ignoreCase = true) -> color(context, R.color.type_lecture)
        type.contains("Практ", ignoreCase = true) ||
            type.contains("Семинар", ignoreCase = true) -> color(context, R.color.type_practice)
        type.contains("Лаб", ignoreCase = true) -> color(context, R.color.type_lab)
        else -> color(context, R.color.type_other)
    }

    /** Shorthand for ContextCompat.getColor(). */
    private fun color(context: Context, resId: Int): Int =
        ContextCompat.getColor(context, resId)

    private fun buildContentDescription(context: Context, data: WidgetDisplayData): String =
        when (data) {
            is WidgetDisplayData.NoKey -> context.getString(R.string.widget_no_key)
            is WidgetDisplayData.NoData -> context.getString(R.string.widget_no_data)
            is WidgetDisplayData.NoLessons -> context.getString(R.string.widget_no_lessons)
            is WidgetDisplayData.Lesson -> {
                val loc = data.location?.let { ", $it" } ?: ""
                "${data.subject}, ${data.timeStart} – ${data.timeEnd}$loc"
            }
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
