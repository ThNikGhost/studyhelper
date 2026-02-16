package ru.studyhelper.widget.widget

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.os.Bundle
import java.util.concurrent.Executors

/**
 * AppWidgetProvider for the schedule widget.
 * Handles widget lifecycle events and size changes.
 */
class ScheduleWidgetProvider : AppWidgetProvider() {

    private val executor = Executors.newSingleThreadExecutor()

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        val appContext = context.applicationContext
        executor.execute {
            for (appWidgetId in appWidgetIds) {
                WidgetUpdater.update(appContext, appWidgetId)
            }
        }
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle,
    ) {
        // Widget was resized — rebuild with new layout
        val appContext = context.applicationContext
        executor.execute {
            WidgetUpdater.update(appContext, appWidgetId)
        }
    }

    override fun onEnabled(context: Context) {
        WidgetRefreshWorker.enqueue(context)
    }

    override fun onDisabled(context: Context) {
        WidgetRefreshWorker.cancel(context)
        executor.shutdown()
    }
}
