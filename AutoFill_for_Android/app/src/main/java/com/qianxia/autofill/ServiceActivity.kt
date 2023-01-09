package com.qianxia.autofill

import android.content.Context
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.CheckBox
import kotlin.system.exitProcess

class ServiceActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_service)
        val allowCheck: CheckBox = findViewById(R.id.allow_check)
        val startBtn: Button = findViewById(R.id.start_btn)
        val editor = getSharedPreferences("data", Context.MODE_PRIVATE).edit()

        allowCheck.isChecked = getSharedPreferences("data", Context.MODE_PRIVATE).getBoolean("is_allowed", false)
        startBtn.isEnabled = allowCheck.isChecked
        allowCheck.setOnClickListener {
            when (allowCheck.isChecked) {
                false -> {
                    editor.putBoolean("is_allowed", false).apply()
                    startBtn.isEnabled = false
                }
                true -> {
                    editor.putBoolean("is_allowed", true).apply()
                    startBtn.isEnabled = true
                }
            }
        }
        startBtn.setOnClickListener {
            finish()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (!getSharedPreferences("data", Context.MODE_PRIVATE).getBoolean("is_allowed", false)) {
            exitProcess(0)
        }
    }
}