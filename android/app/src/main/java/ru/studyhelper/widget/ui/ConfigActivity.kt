package ru.studyhelper.widget.ui

import android.appwidget.AppWidgetManager
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import ru.studyhelper.widget.R
import ru.studyhelper.widget.data.PrefsManager
import ru.studyhelper.widget.widget.ScheduleWidgetProvider
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

        setContentView(R.layout.activity_config)

        val editApiKey = findViewById<EditText>(R.id.editApiKey)
        val btnSave = findViewById<Button>(R.id.btnSave)
        val textStatus = findViewById<TextView>(R.id.textStatus)

        // Pre-fill existing key if available
        PrefsManager.getApiKey(this)?.let { existingKey ->
            editApiKey.setText(existingKey)
        }

        btnSave.setOnClickListener {
            val apiKey = editApiKey.text.toString().trim()
            if (apiKey.isEmpty()) {
                textStatus.text = getString(R.string.config_error_empty)
                textStatus.setTextColor(0xFFFF6B6B.toInt())
                textStatus.visibility = View.VISIBLE
                return@setOnClickListener
            }

            // Save key
            PrefsManager.saveApiKey(this, apiKey)

            // Show loading state
            btnSave.isEnabled = false
            textStatus.text = getString(R.string.config_loading)
            textStatus.setTextColor(0xFF8b8ba7.toInt())
            textStatus.visibility = View.VISIBLE

            // Fetch data and update widget in background
            val context = applicationContext
            executor.execute {
                WidgetUpdater.updateAll(context)

                runOnUiThread {
                    // Schedule periodic updates
                    WidgetRefreshWorker.enqueue(context)

                    textStatus.text = getString(R.string.config_success)
                    textStatus.setTextColor(0xFF4ade80.toInt())

                    // If launched from widget config, return OK
                    if (appWidgetId != AppWidgetManager.INVALID_APPWIDGET_ID) {
                        val resultValue = Intent().apply {
                            putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
                        }
                        setResult(RESULT_OK, resultValue)
                    }

                    // Close after brief delay
                    btnSave.postDelayed({ finish() }, 800)
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdownNow()
    }
}
