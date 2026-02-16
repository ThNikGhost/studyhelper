package ru.studyhelper.widget.data

import android.content.Context
import android.util.Log
import org.json.JSONObject
import java.util.Calendar

/**
 * Repository that fetches schedule data, manages cache, and finds the next lesson.
 * Logic mirrors frontend/public/scriptable-widget.js.
 */
object WidgetRepository {

    private const val TAG = "SH_Repository"

    /**
     * Get what the widget should display.
     * Fetches from API, falls back to cache, then computes the next lesson.
     */
    fun getNextLesson(context: Context): WidgetDisplayData {
        val apiKey = PrefsManager.getApiKey(context)
            ?: return WidgetDisplayData.NoKey

        // Try network fetch
        val json = ApiClient.fetchTodaySchedule(apiKey)
        if (json != null) {
            PrefsManager.saveCache(context, json)
        }

        // Use fresh data or cached
        val rawJson = json ?: PrefsManager.getCache(context)
            ?: return WidgetDisplayData.NoData

        return try {
            val response = TodayScheduleResponse.fromJson(JSONObject(rawJson))
            findNextLesson(response)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to parse schedule JSON", e)
            WidgetDisplayData.NoData
        }
    }

    /**
     * Find the next upcoming lesson from the schedule response.
     * Logic matches scriptable-widget.js findNextLesson().
     */
    private fun findNextLesson(data: TodayScheduleResponse): WidgetDisplayData {
        val now = Calendar.getInstance()
        val todayStr = String.format(
            "%04d-%02d-%02d",
            now.get(Calendar.YEAR),
            now.get(Calendar.MONTH) + 1,
            now.get(Calendar.DAY_OF_MONTH),
        )
        val currentMinutes = now.get(Calendar.HOUR_OF_DAY) * 60 + now.get(Calendar.MINUTE)

        // If data date is today, find the next upcoming lesson
        if (data.date == todayStr && data.lessons.isNotEmpty()) {
            for (lesson in data.lessons) {
                val lessonMinutes = parseTime(lesson.timeStart)
                if (lessonMinutes > currentMinutes) {
                    return WidgetDisplayData.Lesson(
                        subject = lesson.subject,
                        timeStart = lesson.timeStart,
                        timeEnd = lesson.timeEnd,
                        location = lesson.location,
                        teacher = lesson.teacher,
                        lessonType = lesson.lessonType,
                        minutesUntil = lessonMinutes - currentMinutes,
                        isToday = true,
                        futureDate = null,
                    )
                }
            }
        }

        // All today's lessons passed or different date — show future lesson
        val futureLes = data.nextLessonFromFuture
        if (futureLes != null) {
            return WidgetDisplayData.Lesson(
                subject = futureLes.subject,
                timeStart = futureLes.timeStart,
                timeEnd = futureLes.timeEnd,
                location = futureLes.location,
                teacher = futureLes.teacher,
                lessonType = futureLes.lessonType,
                minutesUntil = null,
                isToday = false,
                futureDate = data.nextLessonDate,
            )
        }

        return WidgetDisplayData.NoLessons
    }

    /**
     * Parse "HH:MM" time string to minutes since midnight.
     */
    private fun parseTime(time: String): Int {
        val parts = time.split(":")
        return parts[0].toInt() * 60 + parts[1].toInt()
    }
}
