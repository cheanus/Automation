package com.qianxia.autofill

import android.content.Context
import android.util.Log
import androidx.work.Worker
import androidx.work.WorkerParameters

class PlanWorker(context: Context, params: WorkerParameters): Worker(context, params) {
    override fun doWork(): Result {
        if (inputData.getBoolean("is_allowed", false)) {
            val account = inputData.getString("account")!!
            val password = inputData.getString("password")!!
            return if (goFill(account, password) == 0) {
                Result.success()
            } else {
                Log.i("PlanWorker", "$account $password")
                Result.retry()
            }
        }
        return Result.success()
    }
}