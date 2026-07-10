package com.example.alarm_app

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.view.WindowManager
import androidx.core.app.NotificationCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val WAKE_CHANNEL = "com.alarm_app/wake_screen"
    private val ALARM_CHANNEL = "com.alarm_app/alarm"
    private val CHANNEL_ID = "alarm_urgent_channel"
    private var wakeLock: PowerManager.WakeLock? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        // Canal focado em acordar o hardware
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, WAKE_CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "wakeScreen") {
                wakeScreenDevice()
                result.success(true)
            } else {
                result.notImplemented()
            }
        }

        // Canal para disparar os alertas visuais
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, ALARM_CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "bringToForeground" -> {
                    triggerUrgentNotification()
                    result.success(true)
                }
                else -> result.notImplemented()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        configureWindowFlags()
        createNotificationChannel()
    }

    private fun configureWindowFlags() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        }
        window.addFlags(
            WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
            WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
            WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON or
            WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
        )
    }

    // Força o ecrã físico a acender usando o PowerManager do Android
    private fun wakeScreenDevice() {
        runOnUiThread {
            configureWindowFlags()
            try {
                val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
                if (!powerManager.isInteractive) {
                    // Tipo de lock que acende o ecrã com brilho total e desliga após alguns segundos automaticamente
                    wakeLock = powerManager.newWakeLock(
                        PowerManager.SCREEN_BRIGHT_WAKE_LOCK or PowerManager.ACQUIRE_CAUSES_WAKEUP,
                        "AlarmApp::MotionWakeTag"
                    )
                    wakeLock?.acquire(3000) // Acende por 3 segundos para mostrar a notificação
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "Alertas de Movimento"
            val descriptionText = "Canal para notificações críticas de sensores"
            val importance = NotificationManager.IMPORTANCE_HIGH // Garante o formato Heads-up (banner no topo)
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
                enableLights(true)
                enableVibration(true)
            }
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    // Cria a notificação Banner (Heads-up) que aparece por cima de qualquer app (como o Bloco de Notas)
    private fun triggerUrgentNotification() {
        runOnUiThread {
            val intent = Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            
            val flag = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            } else {
                PendingIntent.FLAG_UPDATE_CURRENT
            }
            
            val pendingIntent = PendingIntent.getActivity(this, 0, intent, flag)

            val builder = NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
                .setContentTitle("⚠️ MOVIMENTO DETETADO!")
                .setContentText("Toca aqui imediatamente para introduzir o PIN e desligar o alarme.")
                .setPriority(NotificationCompat.PRIORITY_MAX) // Força o Banner a descer no ecrã
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setContentIntent(pendingIntent)
                .setAutoCancel(true)
                .setOngoing(true) // Impede o utilizador de fechar a notificação deslizando para o lado

            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.notify(2002, builder.build())
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (wakeLock?.isHeld == true) {
            wakeLock?.release()
        }
    }
}