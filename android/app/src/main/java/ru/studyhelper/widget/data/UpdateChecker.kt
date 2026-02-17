package ru.studyhelper.widget.data

import android.content.Context
import android.util.Log
import org.json.JSONObject
import ru.studyhelper.widget.BuildConfig
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URI

/**
 * Checks GitHub Releases for app updates and downloads APKs.
 * Uses unauthenticated GitHub API (60 req/hour limit — sufficient for manual checks).
 */
object UpdateChecker {

    private const val TAG = "SH_UpdateChecker"
    private const val GITHUB_REPO = "ThNikGhost/studyhelper"
    private const val RELEASES_URL =
        "https://api.github.com/repos/$GITHUB_REPO/releases/latest"
    // Prefix includes scheme — enforces HTTPS
    private const val ALLOWED_DOWNLOAD_PREFIX =
        "https://github.com/$GITHUB_REPO/"
    private const val TAG_PREFIX = "android/v"
    // TODO(release-signing): change to "app-release.apk" when keystore is configured
    private const val APK_ASSET_NAME = "app-debug.apk"
    private const val TIMEOUT_MS = 15_000
    private const val BUFFER_SIZE = 8192

    /**
     * Check GitHub for a newer release.
     *
     * @param context Application context for logging.
     * @return UpdateInfo if a newer version exists, null otherwise.
     */
    fun checkForUpdate(context: Context): UpdateInfo? {
        var connection: HttpURLConnection? = null
        return try {
            val url = URI(RELEASES_URL).toURL()
            FileLogger.log(context, TAG, "checkForUpdate: GET $RELEASES_URL")
            connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = TIMEOUT_MS
            connection.setRequestProperty("Accept", "application/vnd.github+json")
            connection.setRequestProperty(
                "User-Agent",
                "StudyHelper-Android/${BuildConfig.VERSION_NAME}",
            )

            val code = connection.responseCode
            FileLogger.log(context, TAG, "checkForUpdate: HTTP $code")

            if (code != 200) {
                FileLogger.warn(context, TAG, "checkForUpdate: non-200 response: $code")
                return null
            }

            val body = connection.inputStream.bufferedReader().use { it.readText() }
            val json = JSONObject(body)

            val tagName = json.optString("tag_name", "")
            if (!tagName.startsWith(TAG_PREFIX)) {
                FileLogger.warn(context, TAG, "checkForUpdate: unexpected tag format: $tagName")
                return null
            }

            val remoteVersion = tagName.removePrefix(TAG_PREFIX)
            val currentVersion = BuildConfig.VERSION_NAME

            if (compareVersions(currentVersion, remoteVersion) >= 0) {
                FileLogger.log(
                    context, TAG,
                    "checkForUpdate: up to date ($currentVersion >= $remoteVersion)",
                )
                return null
            }

            // Find APK asset
            val assets = json.optJSONArray("assets") ?: return null
            for (i in 0 until assets.length()) {
                val asset = assets.getJSONObject(i)
                if (asset.optString("name") == APK_ASSET_NAME) {
                    val downloadUrl = asset.optString("browser_download_url", "")
                    if (!downloadUrl.startsWith(ALLOWED_DOWNLOAD_PREFIX)) {
                        FileLogger.warn(
                            context, TAG,
                            "checkForUpdate: rejected download URL: $downloadUrl",
                        )
                        return null
                    }
                    val fileSize = asset.optLong("size", 0L)
                    FileLogger.log(
                        context, TAG,
                        "checkForUpdate: update available $currentVersion -> $remoteVersion " +
                            "(${fileSize / 1024}KB)",
                    )
                    return UpdateInfo(
                        versionName = remoteVersion,
                        downloadUrl = downloadUrl,
                        fileSize = fileSize,
                    )
                }
            }

            FileLogger.warn(context, TAG, "checkForUpdate: no $APK_ASSET_NAME asset found")
            null
        } catch (e: Exception) {
            Log.w(TAG, "Update check failed", e)
            FileLogger.error(context, TAG, "checkForUpdate: failed", e)
            null
        } finally {
            connection?.disconnect()
        }
    }

    /**
     * Download APK to cache directory with progress reporting.
     *
     * @param context Application context.
     * @param info Update info with download URL and expected size.
     * @param onProgress Callback with bytes downloaded so far.
     * @return Downloaded APK file, or null on failure.
     */
    fun downloadApk(
        context: Context,
        info: UpdateInfo,
        onProgress: (downloaded: Long) -> Unit,
    ): File? {
        val outFile = File(context.cacheDir, "update.apk")
        var connection: HttpURLConnection? = null
        return try {
            // Clean up any previous partial download
            if (outFile.exists()) outFile.delete()

            val url = URI(info.downloadUrl).toURL()
            FileLogger.log(context, TAG, "downloadApk: GET ${info.downloadUrl}")
            connection = url.openConnection() as HttpURLConnection
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = 30_000 // Longer timeout for download
            connection.setRequestProperty(
                "User-Agent",
                "StudyHelper-Android/${BuildConfig.VERSION_NAME}",
            )
            connection.instanceFollowRedirects = true

            val code = connection.responseCode
            if (code != 200) {
                FileLogger.warn(context, TAG, "downloadApk: HTTP $code")
                return null
            }

            connection.inputStream.use { input ->
                FileOutputStream(outFile).use { output ->
                    val buffer = ByteArray(BUFFER_SIZE)
                    var totalRead = 0L
                    var bytesRead: Int
                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        // Check for thread interruption (rotation, onDestroy)
                        if (Thread.currentThread().isInterrupted) {
                            FileLogger.warn(context, TAG, "downloadApk: interrupted")
                            outFile.delete()
                            return null
                        }
                        output.write(buffer, 0, bytesRead)
                        totalRead += bytesRead
                        onProgress(totalRead)
                    }
                }
            }

            // Verify downloaded file size matches expected
            if (info.fileSize > 0 && outFile.length() != info.fileSize) {
                FileLogger.warn(
                    context, TAG,
                    "downloadApk: size mismatch expected=${info.fileSize} actual=${outFile.length()}",
                )
                outFile.delete()
                return null
            }

            FileLogger.log(context, TAG, "downloadApk: completed, ${outFile.length()} bytes")
            outFile
        } catch (e: Exception) {
            Log.w(TAG, "APK download failed", e)
            FileLogger.error(context, TAG, "downloadApk: failed", e)
            if (outFile.exists()) outFile.delete()
            null
        } finally {
            connection?.disconnect()
        }
    }

    /**
     * Compare two semver version strings (e.g. "1.2.0" vs "1.3.0").
     *
     * @return negative if current < remote, 0 if equal, positive if current > remote.
     */
    fun compareVersions(current: String, remote: String): Int {
        val c = current.split(".").map { it.toIntOrNull() ?: 0 }
        val r = remote.split(".").map { it.toIntOrNull() ?: 0 }
        val maxLen = maxOf(c.size, r.size)
        for (i in 0 until maxLen) {
            val cv = c.getOrElse(i) { 0 }
            val rv = r.getOrElse(i) { 0 }
            if (cv != rv) return cv - rv
        }
        return 0
    }
}

/**
 * Info about an available update.
 */
data class UpdateInfo(
    val versionName: String,
    val downloadUrl: String,
    val fileSize: Long,
)
