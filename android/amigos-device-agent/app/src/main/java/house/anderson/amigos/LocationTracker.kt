package house.anderson.amigos

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import org.json.JSONObject
import kotlin.math.roundToInt

object LocationTracker : LocationListener {
    private const val PREFS = "navigation_location"
    private var manager: LocationManager? = null
    @Volatile private var tracking = false

    fun hasPermission(context: Context): Boolean =
        context.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
        context.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED

    @Synchronized
    fun start(context: Context) {
        if (tracking || !hasPermission(context)) return
        val app = context.applicationContext
        val lm = app.getSystemService(LocationManager::class.java) ?: return
        manager = lm
        try {
            if (app.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED &&
                lm.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000L, 2f, this)
                lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)?.let { record(app, it) }
            }
            if (lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 5000L, 10f, this)
                lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)?.let { record(app, it) }
            }
            tracking = true
        } catch (_: Throwable) {
            tracking = false
        }
    }

    @Synchronized
    fun stop() {
        try { manager?.removeUpdates(this) } catch (_: Throwable) {}
        manager = null
        tracking = false
    }

    fun isTracking(): Boolean = tracking

    override fun onLocationChanged(location: Location) {
        val context = AppContextHolder.context ?: return
        record(context, location)
    }

    @Suppress("DEPRECATION")
    override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
    override fun onProviderEnabled(provider: String) {}
    override fun onProviderDisabled(provider: String) {}

    private fun record(context: Context, l: Location) {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val speedMps = if (l.hasSpeed()) l.speed else -1f
        val bearing = if (l.hasBearing()) l.bearing else -1f
        p.edit()
            .putLong("time_ms", l.time.takeIf { it > 0 } ?: System.currentTimeMillis())
            .putLong("lat_bits", java.lang.Double.doubleToRawLongBits(l.latitude))
            .putLong("lon_bits", java.lang.Double.doubleToRawLongBits(l.longitude))
            .putFloat("accuracy_m", if (l.hasAccuracy()) l.accuracy else -1f)
            .putFloat("speed_mps", speedMps)
            .putFloat("bearing_deg", bearing)
            .putString("provider", l.provider ?: "unknown")
            .putLong("fix_count", p.getLong("fix_count", 0L) + 1L)
            .apply()

        val payload = JSONObject().apply {
            put("lat", l.latitude)
            put("lon", l.longitude)
            if (l.hasAccuracy()) put("accuracyM", l.accuracy)
            if (l.hasSpeed()) put("speedMps", l.speed)
            if (l.hasBearing()) put("bearingDeg", l.bearing)
            put("provider", l.provider ?: "unknown")
        }.toString()

        NavigationOverlay.update(context)

        LocalBridgeSender.send(
            DeviceEvent(
                source = "location",
                packageName = context.packageName,
                title = "navigation_location",
                text = payload
            )
        )
    }

    fun latest(context: Context): LocationSnapshot? {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (!p.contains("lat_bits") || !p.contains("lon_bits")) return null
        return LocationSnapshot(
            latitude = java.lang.Double.longBitsToDouble(p.getLong("lat_bits", 0L)),
            longitude = java.lang.Double.longBitsToDouble(p.getLong("lon_bits", 0L)),
            accuracyM = p.getFloat("accuracy_m", -1f),
            speedMps = p.getFloat("speed_mps", -1f),
            bearingDeg = p.getFloat("bearing_deg", -1f),
            provider = p.getString("provider", "unknown") ?: "unknown",
            timeMs = p.getLong("time_ms", 0L),
            fixCount = p.getLong("fix_count", 0L)
        )
    }

    fun snapshot(context: Context): String {
        val s = latest(context)
        if (s == null) {
            return "GPS PROOF\nGPS permission: " + hasPermission(context) +
                "\nGPS tracking: " + isTracking() +
                "\nGPS fixes: 0"
        }
        val speedMph = if (s.speedMps >= 0) (s.speedMps * 2.2369363f).roundToInt().toString() else "unknown"
        val heading = if (s.bearingDeg >= 0) compass(s.bearingDeg) + " (" + s.bearingDeg.roundToInt() + "°)" else "unknown"
        return "GPS PROOF\n" +
            "GPS permission: " + hasPermission(context) + "\n" +
            "GPS tracking: " + isTracking() + "\n" +
            "GPS fixes: " + s.fixCount + "\n" +
            "Accuracy: " + (if (s.accuracyM >= 0) s.accuracyM.roundToInt().toString() + " m" else "unknown") + "\n" +
            "Speed: " + speedMph + " mph\n" +
            "Heading: " + heading + "\n" +
            "Provider: " + s.provider
    }

    fun privateSummary(context: Context): String {
        val s = latest(context) ?: return "GPS fix not available yet."
        val speedMph = if (s.speedMps >= 0) (s.speedMps * 2.2369363f).roundToInt() else null
        val heading = if (s.bearingDeg >= 0) compass(s.bearingDeg) else null
        return buildString {
            append("GPS fix available")
            if (speedMph != null) append(", speed ").append(speedMph).append(" mph")
            if (heading != null) append(", heading ").append(heading)
            if (s.accuracyM >= 0) append(", accuracy about ").append(s.accuracyM.roundToInt()).append(" metres")
            append(".")
        }
    }

    private fun compass(deg: Float): String {
        val names = arrayOf("N","NE","E","SE","S","SW","W","NW")
        val i = ((deg + 22.5f) / 45f).toInt() % 8
        return names[i]
    }
}

data class LocationSnapshot(
    val latitude: Double,
    val longitude: Double,
    val accuracyM: Float,
    val speedMps: Float,
    val bearingDeg: Float,
    val provider: String,
    val timeMs: Long,
    val fixCount: Long
)

object AppContextHolder {
    @Volatile var context: Context? = null
}
