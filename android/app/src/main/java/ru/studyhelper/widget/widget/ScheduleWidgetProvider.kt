package ru.studyhelper.widget.widget

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.os.Bundle
import ru.studyhelper.widget.data.FileLogger
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
        FileLogger.log(
            context.applicationContext, TAG,
            "onUpdate: ids=${appWidgetIds.toList()}",
        )
        val appContext = context.applicationContext
        executor.execute {
            for (appWidgetId in appWidgetIds) {
                try {
                    WidgetUpdater.update(appContext, appWidgetId)
                } catch (e: Exception) {
                    FileLogger.error(appContext, TAG, "onUpdate failed for id=$appWidgetId", e)
                }
            }
        }
    }

    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle,
    ) {
        FileLogger.log(
            context.applicationContext, TAG,
            "onAppWidgetOptionsChanged: id=$appWidgetId",
        )
        // Widget was resized — rebuild with new layout
        val appContext = context.applicationContext
        executor.execute {
            try {
                WidgetUpdater.update(appContext, appWidgetId)
            } catch (e: Exception) {
                FileLogger.error(appContext, TAG, "onOptionsChanged failed for id=$appWidgetId", e)
            }
        }
    }

    override fun onEnabled(context: Context) {
        FileLogger.log(context.applicationContext, TAG, "onEnabled: first widget added")
        WidgetRefreshWorker.enqueue(context)
    }

    override fun onDisabled(context: Context) {
        FileLogger.log(context.applicationContext, TAG, "onDisabled: last widget removed")
        WidgetRefreshWorker.cancel(context)
        executor.shutdown()
    }

    companion object {
        private const val TAG = "WidgetProvider"
    }
}
