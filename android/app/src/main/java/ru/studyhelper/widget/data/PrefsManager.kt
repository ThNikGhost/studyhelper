package ru.studyhelper.widget.data

import android.content.Context
import android.content.SharedPreferences

/**
 * Manages SharedPreferences for API key and cached schedule data.
 */
object PrefsManager {

    private const val PREFS_NAME = "studyhelper_widget"
    private const val KEY_API_KEY = "api_key"
    private const val KEY_CACHE_JSON = "cache_json"
    private const val KEY_CACHE_TIME = "cache_time"
    private const val CACHE_TTL_MS = 24 * 60 * 60 * 1000L // 24 hours

    private fun prefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun saveApiKey(context: Context, apiKey: String) {
        prefs(context).edit().putString(KEY_API_KEY, apiKey).apply()
    }

    fun getApiKey(context: Context): String? =
        prefs(context).getString(KEY_API_KEY, null)?.takeIf { it.isNotBlank() }

    fun saveCache(context: Context, json: String) {
        prefs(context).edit()
            .putString(KEY_CACHE_JSON, json)
            .putLong(KEY_CACHE_TIME, System.currentTimeMillis())
            .apply()
    }

    fun getCache(context: Context): String? {
        if (!isCacheValid(context)) return null
        return prefs(context).getString(KEY_CACHE_JSON, null)
    }

    fun isCacheValid(context: Context): Boolean {
        val cacheTime = prefs(context).getLong(KEY_CACHE_TIME, 0)
        if (cacheTime == 0L) return false
        return System.currentTimeMillis() - cacheTime < CACHE_TTL_MS
    }
}
