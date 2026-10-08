package house.anderson.amigos.updater

import android.content.Context
import androidx.work.Worker
import androidx.work.WorkerParameters

class UpdateWorker(appContext: Context, params: WorkerParameters) : Worker(appContext, params) {
    override fun doWork(): Result {
        return try {
            when (val result = UpdateEngine.checkAndDownload(applicationContext)) {
                is UpdateEngine.CheckResult.Ready -> {
                    UpdaterNotifier.updateReady(applicationContext, result.version)

                    if (UpdaterState.labAutoInstall(applicationContext)) {
                        val service = UpdaterAccessibilityService.instance
                        if (service != null) {
                            service.requestLabAutoInstall()
                        }
                    }
                }
                is UpdateEngine.CheckResult.UpToDate -> {
                    // Quiet success: no notification spam when nothing changed.
                }
            }
            Result.success()
        } catch (t: Throwable) {
            UpdaterState.note(applicationContext, "BACKGROUND CHECK FAILED: ${t.message ?: t.javaClass.simpleName}")
            Result.retry()
        }
    }
}
