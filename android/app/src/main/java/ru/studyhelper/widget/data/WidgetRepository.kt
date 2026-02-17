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
        if (apiKey == null) {
            FileLogger.log(context, TAG, "getNextLesson: no API key")
            return WidgetDisplayData.NoKey
        }

        // Try network fetch
        FileLogger.log(context, TAG, "getNextLesson: fetching from API")
        val json = ApiClient.fetchTodaySchedule(context, apiKey)
        if (json != null) {
            PrefsManager.saveCache(context, json)
            FileLogger.log(context, TAG, "getNextLesson: API success, cached ${json.length} chars")
        } else {
            FileLogger.warn(context, TAG, "getNextLesson: API returned null, using cache")
        }

        // Use fresh data or cached
        val rawJson = json ?: PrefsManager.getCache(context)
        if (rawJson == null) {
            FileLogger.warn(context, TAG, "getNextLesson: no data (API failed + no cache)")
            return WidgetDisplayData.NoData
        }

        return try {
            val response = TodayScheduleResponse.fromJson(JSONObject(rawJson))
            FileLogger.log(
                context, TAG,
                "getNextLesson: parsed response date=${response.date}, " +
                    "lessons=${response.lessons.size}, " +
                    "nextDate=${response.nextLessonDate}",
            )
            val result = findNextLesson(response)
            FileLogger.log(context, TAG, "getNextLesson: result=${result.javaClass.simpleName}")
            result
        } catch (e: Exception) {
            Log.w(TAG, "Failed to parse schedule JSON", e)
            FileLogger.error(context, TAG, "getNextLesson: JSON parse failed", e)
            WidgetDisplayData.NoData
        }
    }

    /**
     * Get widget display data from cache only, ignoring TTL.
     * Used for resize operations to avoid network requests.
     */
    fun getNextLessonFromCache(context: Context): WidgetDisplayData {
        val apiKey = PrefsManager.getApiKey(context)
        if (apiKey == null) return WidgetDisplayData.NoKey

        val rawJson = PrefsManager.getCacheIgnoringTtl(context)
        if (rawJson == null) return WidgetDisplayData.NoData

        return try {
            val response = TodayScheduleResponse.fromJson(JSONObject(rawJson))
            findNextLesson(response)
        } catch (e: Exception) {
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
            for ((index, lesson) in data.lessons.withIndex()) {
                val lessonMinutes = parseTime(lesson.timeStart)
                if (lessonMinutes < 0) continue // skip unparseable time
                if (lessonMinutes > currentMinutes) {
                    val remaining = data.lessons
                        .drop(index + 1)
                        .take(3)
                        .map { LessonBrief(it.subject, it.timeStart, it.location, it.lessonType) }
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
                        remainingLessons = remaining,
                    )
                }
            }
        }

        // All today's lessons passed or different date — show future lesson
        val futureLes = data.nextLessonFromFuture
        if (futureLes != null) {
            val remaining = data.nextDayRemaining
                .take(3)
                .map { LessonBrief(it.subject, it.timeStart, it.location, it.lessonType) }
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
                remainingLessons = remaining,
            )
        }

        return WidgetDisplayData.NoLessons
    }

    /**
     * Parse "HH:MM" time string to minutes since midnight.
     *
     * @return Minutes since midnight, or -1 if parsing fails.
     */
    private fun parseTime(time: String): Int {
        return try {
            val parts = time.split(":")
            parts[0].toInt() * 60 + parts[1].toInt()
        } catch (e: Exception) {
            Log.w(TAG, "Failed to parse time: $time", e)
            -1
        }
    }
}
