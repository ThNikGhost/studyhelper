package ru.studyhelper.widget.data

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
     * @param apiKey Widget API key.
     * @return Raw JSON string, or null on failure.
     */
    fun fetchTodaySchedule(apiKey: String): String? {
        var connection: HttpURLConnection? = null
        return try {
            val url = URI("$BASE_URL?api_key=$apiKey").toURL()
            connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = TIMEOUT_MS
            connection.setRequestProperty("Accept", "application/json")
            connection.setRequestProperty("User-Agent", "StudyHelper-Android/1.0")

            if (connection.responseCode != 200) {
                Log.w(TAG, "API returned ${connection.responseCode}")
                return null
            }

            BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                reader.readText()
            }
        } catch (e: Exception) {
            Log.w(TAG, "Failed to fetch schedule", e)
            null
        } finally {
            connection?.disconnect()
        }
    }
}
