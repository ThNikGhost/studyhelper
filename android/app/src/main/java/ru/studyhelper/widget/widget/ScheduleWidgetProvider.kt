package ru.studyhelper.widget.widget

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import java.util.concurrent.Executors

/**
 * AppWidgetProvider for the schedule widget.
 * Handles widget lifecycle events.
 */
class ScheduleWidgetProvider : AppWidgetProvider() {

    private val executor = Executors.newSingleThreadExecutor()

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        // Update each widget instance on a background thread (network call)
        val appContext = context.applicationContext
        executor.execute {
            for (appWidgetId in appWidgetIds) {
                WidgetUpdater.update(appContext, appWidgetId)
            }
        }
    }

    override fun onEnabled(context: Context) {
        // First widget added — schedule periodic refresh
        WidgetRefreshWorker.enqueue(context)
    }

    override fun onDisabled(context: Context) {
        // Last widget removed — cancel periodic refresh
        WidgetRefreshWorker.cancel(context)
    }
}
