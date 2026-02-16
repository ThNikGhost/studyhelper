# StudyHelper Widget ProGuard rules

# Keep widget provider (referenced from AndroidManifest)
-keep class ru.studyhelper.widget.widget.ScheduleWidgetProvider { *; }

# Keep WorkManager worker
-keep class ru.studyhelper.widget.widget.WidgetRefreshWorker { *; }

# Keep ConfigActivity
-keep class ru.studyhelper.widget.ui.ConfigActivity { *; }
