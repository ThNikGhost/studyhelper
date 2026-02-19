package ru.studyhelper.widget.widget

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import ru.studyhelper.widget.data.FileLogger

/**
 * Receives AlarmManager callback when a lesson starts,
 * triggering widget refresh to replace expired countdown.
 */
class WidgetRefreshReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent?) {
        FileLogger.log(context, TAG, "alarm triggered — refreshing widgets")
        // cacheOnly=true: no network call, just re-evaluate findNextLesson()
        // with current time. Safe to run on main thread (no I/O).
        WidgetUpdater.updateAll(context.applicationContext, cacheOnly = true)
    }

    companion object {
        private const val TAG = "RefreshReceiver"
    }
}
