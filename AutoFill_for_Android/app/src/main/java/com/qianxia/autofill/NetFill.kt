package com.qianxia.autofill

import android.util.Log
import okhttp3.*
import java.net.CookieManager
import java.net.CookiePolicy

fun goFill(username: String, password: String): Int {
    var url = "https://uis.nwpu.edu.cn/cas/login?service=https%3A%2F%2Fecampus.nwpu.edu.cn%2F%3Fpath%3Dhttps%3A%2F%2Fecampus.nwpu.edu.cn"
    val cookieManager = CookieManager()
    cookieManager.setCookiePolicy(CookiePolicy.ACCEPT_ALL)
    val cookieJar = JavaNetCookieJar(cookieManager)
    val client = OkHttpClient.Builder().cookieJar(cookieJar).build()
    var request = Request.Builder().url(url).build()
    try {
        var response = client.newCall(request).execute()
        val execution = Regex("""name="execution" value="(.*?)"""").find(response.body?.string().toString())?.groups?.get(1)?.value!!
        var str1 = "d605d8df6bf5ca8a54fe078683196518"
        val httpUrl = HttpUrl.Builder().scheme("https").host("ecampus.nwpu.edu.cn").build()
        val cookie1:Cookie = Cookie.parse(httpUrl, "Hm_lvt_$str1="+System.currentTimeMillis().toString())!!
        val cookie2:Cookie = Cookie.parse(httpUrl, "Hm_lpvt_$str1="+System.currentTimeMillis().toString())!!
        cookieJar.saveFromResponse(httpUrl, listOf(cookie1, cookie2))
        var body = (FormBody.Builder()
            .add("username", username)
            .add("password", password)
            .add("currentMenu", "1")
            .add("execution", execution)
            .add("_eventId", "submit")
            .add("geolocation", "")
            .add("submit", "One moment please...")
            .build())
        request = Request.Builder().url(url).post(body).build()
        client.newCall(request).execute()  // received login coolie

        url = "https://yqtb.nwpu.edu.cn/sso/login.jsp"
        request = Request.Builder().url(url).build()
        response = client.newCall(request).execute()
        str1 = Regex("""url:'(.*?)'""").findAll(response.body?.string().toString()).toList()[3].groups[1]?.value!!

        url = "https://yqtb.nwpu.edu.cn/wx/ry/jbxx_v.jsp"
        request = Request.Builder().url(url).build()
        val str2 = client.newCall(request).execute().body?.string()
        val userLoginId = Regex("""学号：</label></div>(\s*)<span class="weui-cell__value">(.*?)</span>""").find(str2.toString())?.groups?.get(2)?.value!!
        val userName = Regex("""姓名：</label></div>(\s*)<span class="weui-cell__value">(.*?)</span>""").find(str2.toString())?.groups?.get(2)?.value!!

        url = "https://yqtb.nwpu.edu.cn/wx/ry/$str1"
        body = (FormBody.Builder()
            .add("hsjc", "1")
            .add("xasymt", "1")
            .add("actionType", "addRbxx")
            .add("userLoginId", userLoginId)
            .add("szcsbm", "1")
            .add("bdzt", "1")
            .add("szcsmc", "在学校")
            .add("szcsmc1", "在学校")
            .add("sfyzz", "0")
            .add("sfqz", "0")
            .add("tbly", "pc")
            .add("qtqksm", "")
            .add("ycqksm", "")
            .add("sfxn", "0")
            .add("sfdw", "0")
            .add("longlat", "")
            .add("userType", "2")
            .add("userName", userName)
            .build())
        request = (Request.Builder()
            .url(url)
            .addHeader("Referer", "https://yqtb.nwpu.edu.cn/wx/ry/jrsb_xs.jsp")
            .addHeader("X-Requested-With", "XMLHttpRequest")
            .post(body)
            .build())
        response = client.newCall(request).execute()
        return if (response.body?.string()?.toList()?.get(36) != '1') {
            -2
        } else {
            0
        }
    } catch (e: java.net.ConnectException) {
        return -1
    } catch (e: java.net.UnknownHostException) {
        return -1
    } catch (e: java.lang.IndexOutOfBoundsException) {
        return -3
    }
}

//fun main() {
//    println(goFill("18282947878", "Hjl5968vcn@"))
//}