package com.qianxia.autofill

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.text.Html
import android.widget.Button
import android.widget.TextView

class HelpActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_help)
        val helpBack:Button = findViewById(R.id.help_back)
        helpBack.setOnClickListener {
            finish()
        }
    }
}