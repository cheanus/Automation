package com.qianxia.autofill

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Build
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import android.widget.ToggleButton
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.NotificationCompat
import androidx.work.*
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val prefs = getSharedPreferences("data", Context.MODE_PRIVATE)
        val toggleBtn: ToggleButton = findViewById(R.id.toggle_btn)
        val isToggleChecked = prefs.getBoolean("is_toggle_checked", false)
        var i = 1

        if (!prefs.getBoolean("is_allowed", false)) {
            val intent = Intent(this, ServiceActivity::class.java)
            startActivity(intent)
        }
        toggleBtn.isChecked = isToggleChecked
        toggleBtn.setOnCheckedChangeListener { _, isChecked ->
            if (prefs.getString("account", "") == "" || prefs.getString("password", "") == "") {
                Toast.makeText(this, "未设置账户信息", Toast.LENGTH_SHORT).show()
                toggleBtn.isChecked = false
            } else {
                if (isChecked) {
                    val request = (PeriodicWorkRequest.Builder(
                        PlanWorker::class.java,
                        12, TimeUnit.HOURS
                    )
                        .setBackoffCriteria(BackoffPolicy.LINEAR, 20, TimeUnit.MINUTES)
                        .setInputData(
                            workDataOf(
                                "account" to prefs.getString("account", "")!!,
                                "password" to prefs.getString("password", "")!!,
                                "is_allowed" to prefs.getBoolean("is_allowed", false)
                            )
                        )
                        .build())
                    WorkManager.getInstance(this).enqueue(request)
                    Toast.makeText(this, "每日自动填报已开启", Toast.LENGTH_SHORT).show()
                } else {
                    WorkManager.getInstance(this).cancelAllWork()
                    Toast.makeText(this, "每日自动填报已关闭", Toast.LENGTH_SHORT).show()
                }
                prefs.edit().putBoolean("is_toggle_checked", isChecked).apply()
            }
        }
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.setting_item -> startActivity(Intent(this, SettingActivity::class.java))
            R.id.help_item -> startActivity(Intent(this, HelpActivity::class.java))
        }
        return true
    }
}