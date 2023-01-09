package com.qianxia.autofill

import android.content.Context
import android.content.Intent
import android.graphics.Paint
import android.os.Build
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.Looper
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.annotation.RequiresApi
import kotlin.concurrent.thread

class SettingActivity : AppCompatActivity() {
    @RequiresApi(Build.VERSION_CODES.M)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_setting)
        val prefs = getSharedPreferences("data", Context.MODE_PRIVATE)
        var account = prefs.getString("account", "")!!
        var password = prefs.getString("password", "")!!
        val accountEdit:EditText = findViewById(R.id.account_eidt)
        val passwordEdit:EditText = findViewById(R.id.password_edit)
        val saveBtn:Button = findViewById(R.id.save_btn)
        val testbtn:Button = findViewById(R.id.test_btn)
        val useText:TextView = findViewById(R.id.use_policy)

        useText.paint.flags = Paint.UNDERLINE_TEXT_FLAG
        accountEdit.setText(account)
        passwordEdit.setText(password)

        saveBtn.setOnClickListener {
            prefs.edit().putString("account", accountEdit.text.toString()).apply()
            prefs.edit().putString("password", passwordEdit.text.toString()).apply()
        }
        useText.setOnClickListener {
            startActivity(Intent(this, ServiceActivity::class.java))
        }
        testbtn.setOnClickListener {
            Log.i("SettingActivity", "abcd")
            account = prefs.getString("account", "")!!
            password = prefs.getString("password", "")!!
            thread {
                Log.i("SettingActivity", "bcde")
                Looper.prepare()
                when (goFill(account, password)) {
                    0 -> Toast.makeText(this, "打卡成功", Toast.LENGTH_SHORT).show()
                    -1 -> Toast.makeText(this, "网络故障", Toast.LENGTH_SHORT).show()
                    -2 -> Toast.makeText(this, "打卡失败", Toast.LENGTH_SHORT).show()
                    -3 -> Toast.makeText(this, "账户错误", Toast.LENGTH_SHORT).show()
                }
                Looper.loop()
            }
            Log.i("SettingActivity", "cdef")
        }
    }
}