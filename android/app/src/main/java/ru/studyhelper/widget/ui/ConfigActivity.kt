package ru.studyhelper.widget.ui

import android.appwidget.AppWidgetManager
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import ru.studyhelper.widget.R
import ru.studyhelper.widget.data.FileLogger
import ru.studyhelper.widget.data.PrefsManager
import ru.studyhelper.widget.widget.WidgetRefreshWorker
import ru.studyhelper.widget.widget.WidgetUpdater
import java.util.concurrent.Executors

/**
 * Configuration screen shown when adding a widget or launched from app icon.
 * Allows the user to enter/update their API key.
 */
class ConfigActivity : AppCompatActivity() {

    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID
    private val executor = Executors.newSingleThreadExecutor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Default result: cancelled (user backs out without saving)
        setResult(RESULT_CANCELED)

        // Get widget ID if launched from widget config
        appWidgetId = intent.getIntExtra(
            AppWidgetManager.EXTRA_APPWIDGET_ID,
            AppWidgetManager.INVALID_APPWIDGET_ID,
        )

        FileLogger.log(
            applicationContext, TAG,
            "onCreate: appWidgetId=$appWidgetId, action=${intent.action}",
        )

        setContentView(R.layout.activity_config)

        val editApiKey = findViewById<EditText>(R.id.editApiKey)
        val btnSave = findViewById<Button>(R.id.btnSave)
        val textStatus = findViewById<TextView>(R.id.textStatus)
        val textShareLogs = findViewById<TextView>(R.id.textShareLogs)

        // Pre-fill existing key if available
        PrefsManager.getApiKey(this)?.let { existingKey ->
            editApiKey.setText(existingKey)
        }

        // Share logs button
        textShareLogs.setOnClickListener { shareLogs() }

        btnSave.setOnClickListener {
            val apiKey = editApiKey.text.toString().trim()
            if (apiKey.isEmpty()) {
                textStatus.text = getString(R.string.config_error_empty)
                textStatus.setTextColor(ContextCompat.getColor(this, R.color.config_error))
                textStatus.visibility = View.VISIBLE
                return@setOnClickListener
            }

            // Save key
            PrefsManager.saveApiKey(this, apiKey)
            FileLogger.log(applicationContext, TAG, "API key saved, starting widget update")

            // Show loading state
            btnSave.isEnabled = false
            textStatus.text = getString(R.string.config_loading)
            textStatus.setTextColor(
                ContextCompat.getColor(this, R.color.config_text_secondary),
            )
            textStatus.visibility = View.VISIBLE

            // Fetch data and update widget in background
            val context = applicationContext
            val widgetId = appWidgetId
            executor.execute {
                try {
                    // Update all existing widgets
                    WidgetUpdater.updateAll(context)
                    FileLogger.log(context, TAG, "updateAll completed")

                    // Also update the specific new widget being configured
                    if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                        WidgetUpdater.update(context, widgetId)
                        FileLogger.log(context, TAG, "update($widgetId) completed")
                    }
                } catch (e: Exception) {
                    FileLogger.error(context, TAG, "Widget update failed", e)
                }

                runOnUiThread {
                    // Schedule periodic updates
                    WidgetRefreshWorker.enqueue(context)

                    textStatus.text = getString(R.string.config_success)
                    textStatus.setTextColor(
                        ContextCompat.getColor(this, R.color.widget_countdown_today),
                    )

                    // If launched from widget config, return OK
                    if (widgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                        val resultValue = Intent().apply {
                            putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, widgetId)
                        }
                        setResult(RESULT_OK, resultValue)
                        FileLogger.log(context, TAG, "setResult(RESULT_OK, widgetId=$widgetId)")
                    }

                    // Close after brief delay
                    btnSave.postDelayed({
                        FileLogger.log(context, TAG, "finish()")
                        finish()
                    }, 800)
                }
            }
        }
    }

    private fun shareLogs() {
        val logFile = FileLogger.getLogFile(applicationContext)
        if (logFile == null) {
            val textStatus = findViewById<TextView>(R.id.textStatus)
            textStatus.text = getString(R.string.config_no_logs)
            textStatus.setTextColor(
                ContextCompat.getColor(this, R.color.config_text_secondary),
            )
            textStatus.visibility = View.VISIBLE
            return
        }

        try {
            val uri = FileProvider.getUriForFile(
                this,
                "${applicationInfo.packageName}.fileprovider",
                logFile,
            )
            val shareIntent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            startActivity(Intent.createChooser(shareIntent, getString(R.string.config_share_logs)))
        } catch (e: Exception) {
            FileLogger.error(applicationContext, TAG, "Share logs failed", e)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdownNow()
    }

    companion object {
        private const val TAG = "ConfigActivity"
    }
}
