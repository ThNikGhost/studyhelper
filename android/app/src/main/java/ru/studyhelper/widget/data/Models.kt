package ru.studyhelper.widget.data

import org.json.JSONObject

/** Return null instead of "null" string or empty string. */
private fun JSONObject.optStringOrNull(key: String): String? {
    if (isNull(key)) return null
    val value = optString(key, "")
    return value.ifEmpty { null }
}

/**
 * Single lesson item from /today API response.
 */
data class TodayLessonItem(
    val subject: String,
    val timeStart: String,
    val timeEnd: String,
    val location: String?,
    val teacher: String?,
    val lessonType: String,
) {
    companion object {
        fun fromJson(json: JSONObject): TodayLessonItem = TodayLessonItem(
            subject = json.getString("subject"),
            timeStart = json.getString("time_start"),
            timeEnd = json.getString("time_end"),
            location = json.optStringOrNull("location"),
            teacher = json.optStringOrNull("teacher"),
            lessonType = json.getString("lesson_type"),
        )
    }
}

/**
 * Full /today API response.
 */
data class TodayScheduleResponse(
    val date: String,
    val lessons: List<TodayLessonItem>,
    val nextLessonFromFuture: TodayLessonItem?,
    val nextLessonDate: String?,
    val cachedAt: String,
) {
    companion object {
        fun fromJson(json: JSONObject): TodayScheduleResponse {
            val lessonsArray = json.getJSONArray("lessons")
            val lessons = (0 until lessonsArray.length()).map { i ->
                TodayLessonItem.fromJson(lessonsArray.getJSONObject(i))
            }

            val futureLesson = if (!json.isNull("next_lesson_from_future")) {
                TodayLessonItem.fromJson(json.getJSONObject("next_lesson_from_future"))
            } else {
                null
            }

            return TodayScheduleResponse(
                date = json.getString("date"),
                lessons = lessons,
                nextLessonFromFuture = futureLesson,
                nextLessonDate = json.optStringOrNull("next_lesson_date"),
                cachedAt = json.getString("cached_at"),
            )
        }
    }
}

/**
 * What the widget should display. Sealed class for exhaustive when().
 */
sealed class WidgetDisplayData {
    /** API key not configured. */
    data object NoKey : WidgetDisplayData()

    /** Could not fetch data and no cache available. */
    data object NoData : WidgetDisplayData()

    /** No upcoming lessons in the next 7 days. */
    data object NoLessons : WidgetDisplayData()

    /** Next lesson to display. */
    data class Lesson(
        val subject: String,
        val timeStart: String,
        val timeEnd: String,
        val location: String?,
        val teacher: String?,
        val lessonType: String,
        val minutesUntil: Int?,
        val isToday: Boolean,
        val futureDate: String?,
    ) : WidgetDisplayData()
}
