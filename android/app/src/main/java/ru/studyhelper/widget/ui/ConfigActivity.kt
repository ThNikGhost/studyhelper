package ru.studyhelper.widget.ui

import android.appwidget.AppWidgetManager
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import ru.studyhelper.widget.R
import ru.studyhelper.widget.data.FileLogger
import ru.studyhelper.widget.data.PrefsManager
import ru.studyhelper.widget.data.UpdateChecker
import ru.studyhelper.widget.data.UpdateInfo
import ru.studyhelper.widget.widget.WidgetRefreshWorker
import ru.studyhelper.widget.widget.WidgetUpdater
import java.io.File
import java.util.Locale
import java.util.concurrent.Executors

/**
 * Configuration screen shown when adding a widget or launched from app icon.
 * Allows the user to enter/update their API key and check for app updates.
 */
class ConfigActivity : AppCompatActivity() {

    private var appWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID
    private val widgetExecutor = Executors.newSingleThreadExecutor()
    private val updateExecutor = Executors.newSingleThreadExecutor()

    // Update-related state
    private var pendingInstallFile: File? = null

    // Launcher for "Install unknown apps" permission settings
    private val installPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult(),
    ) { _ ->
        // User returned from settings — retry install if permission was granted
        val file = pendingInstallFile
        pendingInstallFile = null
        if (file != null && file.exists() && packageManager.canRequestPackageInstalls()) {
            promptInstall(file)
        } else if (file != null) {
            FileLogger.warn(applicationContext, TAG, "Install permission still denied")
        }
    }

    // Update banner views (lazily initialized)
    private lateinit var updateBanner: View
    private lateinit var textUpdateTitle: TextView
    private lateinit var progressUpdate: ProgressBar
    private lateinit var textUpdateProgress: TextView
    private lateinit var btnUpdate: Button

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

        // Init update banner views
        updateBanner = findViewById(R.id.updateBanner)
        textUpdateTitle = findViewById(R.id.textUpdateTitle)
        progressUpdate = findViewById(R.id.progressUpdate)
        textUpdateProgress = findViewById(R.id.textUpdateProgress)
        btnUpdate = findViewById(R.id.btnUpdate)

        // Pre-fill existing key if available
        PrefsManager.getApiKey(this)?.let { existingKey ->
            editApiKey.setText(existingKey)
        }

        // Share logs button
        textShareLogs.setOnClickListener { shareLogs() }

        // Check for updates in background
        checkForUpdates()

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
            widgetExecutor.execute {
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
                    if (isFinishing || isDestroyed) return@runOnUiThread

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

    /**
     * Check GitHub for newer app version in background.
     */
    private fun checkForUpdates() {
        val context = applicationContext
        updateExecutor.execute {
            val info = UpdateChecker.checkForUpdate(context)
            if (info != null) {
                runOnUiThread {
                    if (!isFinishing && !isDestroyed) showUpdateBanner(info)
                }
            }
        }
    }

    /**
     * Show the update banner with version info and download button.
     */
    private fun showUpdateBanner(info: UpdateInfo) {
        textUpdateTitle.text = getString(R.string.update_available, info.versionName)
        updateBanner.visibility = View.VISIBLE
        btnUpdate.setOnClickListener { startDownload(info) }
    }

    /**
     * Download APK with progress bar and trigger install when done.
     */
    private fun startDownload(info: UpdateInfo) {
        btnUpdate.isEnabled = false
        btnUpdate.text = getString(R.string.update_downloading)
        progressUpdate.visibility = View.VISIBLE
        progressUpdate.progress = 0
        textUpdateProgress.visibility = View.VISIBLE
        textUpdateProgress.text = formatSize(0, info.fileSize)

        val context = applicationContext
        updateExecutor.execute {
            val file = UpdateChecker.downloadApk(context, info) { downloaded ->
                runOnUiThread {
                    if (isFinishing || isDestroyed) return@runOnUiThread
                    if (info.fileSize > 0) {
                        progressUpdate.progress = ((downloaded * 100) / info.fileSize).toInt()
                    }
                    textUpdateProgress.text = formatSize(downloaded, info.fileSize)
                }
            }

            runOnUiThread {
                if (isFinishing || isDestroyed) return@runOnUiThread
                if (file != null) {
                    promptInstall(file)
                } else {
                    // Download failed — show retry
                    btnUpdate.text = getString(R.string.update_retry)
                    btnUpdate.isEnabled = true
                    textUpdateProgress.text = getString(R.string.update_failed)
                    progressUpdate.visibility = View.GONE
                    btnUpdate.setOnClickListener { startDownload(info) }
                }
            }
        }
    }

    /**
     * Prompt the system package installer to install the downloaded APK.
     * Handles REQUEST_INSTALL_PACKAGES permission for API 26+.
     */
    private fun promptInstall(file: File) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O && !packageManager.canRequestPackageInstalls()) {
            // Need "Install unknown apps" permission — save file and open settings
            pendingInstallFile = file
            FileLogger.log(applicationContext, TAG, "Requesting install permission")
            val intent = Intent(
                Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                Uri.parse("package:$packageName"),
            )
            installPermissionLauncher.launch(intent)
            return
        }

        try {
            val uri = FileProvider.getUriForFile(
                this,
                "${applicationInfo.packageName}.fileprovider",
                file,
            )
            val installIntent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(installIntent)
            FileLogger.log(applicationContext, TAG, "Install intent launched")
        } catch (e: Exception) {
            FileLogger.error(applicationContext, TAG, "Install failed", e)
            Toast.makeText(this, getString(R.string.update_install_failed), Toast.LENGTH_SHORT)
                .show()
        }
    }

    /**
     * Format download progress as "X.X / Y.Y MB".
     */
    private fun formatSize(downloaded: Long, total: Long): String {
        val dlMb = downloaded / (1024.0 * 1024.0)
        val totalMb = total / (1024.0 * 1024.0)
        return "%.1f / %.1f MB".format(Locale.US, dlMb, totalMb)
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
        widgetExecutor.shutdownNow()
        updateExecutor.shutdownNow()
    }

    companion object {
        private const val TAG = "ConfigActivity"
    }
}
