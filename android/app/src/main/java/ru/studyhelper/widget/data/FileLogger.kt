package ru.studyhelper.widget.data

import android.content.Context
import java.io.File
import java.io.FileWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * File-based logger for widget debugging.
 * Writes to app-specific external directory (accessible via file manager).
 * Rotates log file when it exceeds MAX_SIZE.
 */
object FileLogger {

    private const val LOG_FILE = "widget_log.txt"
    private const val OLD_LOG_FILE = "widget_log_old.txt"
    private const val MAX_SIZE = 500_000L // 500KB

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US)

    /**
     * Log an informational message.
     */
    fun log(context: Context, tag: String, message: String) {
        write(context, "I", tag, message)
    }

    /**
     * Log a warning message.
     */
    fun warn(context: Context, tag: String, message: String) {
        write(context, "W", tag, message)
    }

    /**
     * Log an error with exception details.
     */
    fun error(context: Context, tag: String, message: String, e: Throwable? = null) {
        val fullMessage = if (e != null) {
            "$message: ${e.javaClass.simpleName}: ${e.message}"
        } else {
            message
        }
        write(context, "E", tag, fullMessage)
    }

    /**
     * Get the log file for sharing, or null if it doesn't exist.
     */
    fun getLogFile(context: Context): File? {
        return try {
            val dir = context.getExternalFilesDir(null) ?: return null
            val file = File(dir, LOG_FILE)
            if (file.exists() && file.length() > 0) file else null
        } catch (_: Exception) {
            null
        }
    }

    private fun write(context: Context, level: String, tag: String, message: String) {
        try {
            val dir = context.getExternalFilesDir(null) ?: return
            val file = File(dir, LOG_FILE)

            // Rotate if too large
            if (file.exists() && file.length() > MAX_SIZE) {
                val oldFile = File(dir, OLD_LOG_FILE)
                if (oldFile.exists()) oldFile.delete()
                file.renameTo(oldFile)
            }

            val timestamp = dateFormat.format(Date())
            val line = "$timestamp [$level/$tag] $message\n"

            FileWriter(file, true).use { writer ->
                writer.append(line)
            }
        } catch (_: Exception) {
            // Silently ignore logging errors
        }
    }
}
