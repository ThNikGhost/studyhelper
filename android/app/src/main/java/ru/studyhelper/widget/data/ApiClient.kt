package ru.studyhelper.widget.data

import android.content.Context
import android.util.Log
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URI

/**
 * HTTP client for StudyHelper Widget API.
 * Uses built-in HttpURLConnection — no third-party dependencies.
 */
object ApiClient {

    private const val TAG = "SH_ApiClient"
    private const val BASE_URL = "https://studyhelper1.ru/api/v1/widget/today"
    private const val TIMEOUT_MS = 10_000

    /**
     * Fetch today schedule JSON from the API.
     *
     * @param context Application context for file logging.
     * @param apiKey Widget API key.
     * @return Raw JSON string, or null on failure.
     */
    fun fetchTodaySchedule(context: Context, apiKey: String): String? {
        var connection: HttpURLConnection? = null
        return try {
            val url = URI("$BASE_URL?api_key=$apiKey").toURL()
            FileLogger.log(context, TAG, "fetchTodaySchedule: GET $BASE_URL")
            connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = TIMEOUT_MS
            connection.setRequestProperty("Accept", "application/json")
            connection.setRequestProperty(
                "User-Agent",
                "StudyHelper-Android/${ru.studyhelper.widget.BuildConfig.VERSION_NAME}",
            )

            val code = connection.responseCode
            FileLogger.log(context, TAG, "fetchTodaySchedule: HTTP $code")
            if (code != 200) {
                Log.w(TAG, "API returned $code")
                FileLogger.warn(context, TAG, "fetchTodaySchedule: non-200 response: $code")
                return null
            }

            val body = BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                reader.readText()
            }
            FileLogger.log(context, TAG, "fetchTodaySchedule: received ${body.length} chars")
            body
        } catch (e: Exception) {
            Log.w(TAG, "Failed to fetch schedule", e)
            FileLogger.error(context, TAG, "fetchTodaySchedule: failed", e)
            null
        } finally {
            connection?.disconnect()
        }
    }
}
