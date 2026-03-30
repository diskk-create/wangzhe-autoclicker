package com.wangzhe.autoclicker

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.app.NotificationCompat
import java.util.concurrent.TimeUnit

/**
 * 悬浮窗服务
 * 实现真正的Android悬浮窗
 */
class FloatingWindowService : Service() {

    private lateinit var windowManager: WindowManager
    private lateinit var floatingView: View
    private lateinit var expandedView: View
    private lateinit var collapsedView: View

    private var isRunning = false
    private var clickThread: Thread? = null
    private lateinit var imageRecognizer: ImageRecognizer

    // 王者荣耀11步点击坐标（基于1280x720分辨率）
    private val clickCoordinates = listOf(
        Pair(641, 564),   // 1. 登录（点击"开始游戏"）
        Pair(1190, 112),  // 2. 关闭弹窗
        Pair(514, 544),   // 3. 游戏大厅（点击"对战"）
        Pair(398, 539),   // 4. 王者峡谷匹配
        Pair(730, 601),   // 5. 人机模式（选择"人机"）
        Pair(1057, 569),  // 6. 开始游戏（点击"开始"）
        Pair(775, 660),   // 7. 准备游戏（点击"准备"）
        Pair(640, 561),   // 8. 准备进入游戏（确认进入）
        Pair(640, 360),   // 9. 游戏中（等待结束）
        Pair(635, 664),   // 10. 游戏结束（确认结算）
        Pair(645, 621)    // 11. 结算英雄（点击结算）
        // 注意：第12步"返回房间"坐标为(739, 651)，可根据需要添加
    )
    
    // 每一步的延迟时间（毫秒）
    private val clickDelays = listOf(
        3000,   // 1. 登录等待3秒
        2000,   // 2. 关闭弹窗等待2秒
        2000,   // 3. 游戏大厅等待2秒
        2000,   // 4. 匹配等待2秒
        2000,   // 5. 人机模式等待2秒
        3000,   // 6. 开始游戏等待3秒
        2000,   // 7. 准备游戏等待2秒
        10000,  // 8. 等待进入游戏10秒
        60000,  // 9. 游戏中等待60秒（游戏时间）
        2000,   // 10. 游戏结束等待2秒
        2000    // 11. 结算英雄等待2秒
    )

    override fun onCreate() {
        super.onCreate()

        // 创建通知渠道（Android 8.0+需要）
        createNotificationChannel()

        // 启动前台服务
        startForeground(NOTIFICATION_ID, createNotification())

        // 初始化图像识别器
        imageRecognizer = ImageRecognizer(this)

        // 初始化悬浮窗
        initFloatingWindow()
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    /**
     * 创建通知渠道
     */
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Auto Clicker Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Auto clicker is running"
            }

            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * 创建通知
     */
    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("WangZhe Auto Clicker")
            .setContentText(if (isRunning) "Running..." else "Ready")
            .setSmallIcon(R.mipmap.ic_launcher)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    /**
     * 初始化悬浮窗
     */
    @SuppressLint("ClickableViewAccessibility", "InflateParams")
    private fun initFloatingWindow() {
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager

        // 创建悬浮窗布局
        floatingView = LayoutInflater.from(this).inflate(R.layout.floating_window, null)

        // 获取展开和收起视图
        collapsedView = floatingView.findViewById(R.id.collapsed_view)
        expandedView = floatingView.findViewById(R.id.expanded_view)

        // 设置悬浮窗参数
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                @Suppress("DEPRECATION")
                WindowManager.LayoutParams.TYPE_PHONE
            },
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH or
                    WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 0
            y = 200
        }

        // 添加悬浮窗
        windowManager.addView(floatingView, params)

        // 设置拖动功能
        setupDrag(params)

        // 设置按钮点击
        setupButtons(params)
    }

    /**
     * 设置拖动功能
     */
    @SuppressLint("ClickableViewAccessibility")
    private fun setupDrag(params: WindowManager.LayoutParams) {
        var initialX = 0
        var initialY = 0
        var initialTouchX = 0f
        var initialTouchY = 0f
        var isDragging = false

        collapsedView.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x
                    initialY = params.y
                    initialTouchX = event.rawX
                    initialTouchY = event.rawY
                    isDragging = false
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = (event.rawX - initialTouchX).toInt()
                    val dy = (event.rawY - initialTouchY).toInt()
                    
                    if (Math.abs(dx) > 10 || Math.abs(dy) > 10) {
                        isDragging = true
                        params.x = initialX + dx
                        params.y = initialY + dy
                        windowManager.updateViewLayout(floatingView, params)
                    }
                    true
                }
                MotionEvent.ACTION_UP -> {
                    if (!isDragging) {
                        // 点击展开菜单
                        collapsedView.visibility = View.GONE
                        expandedView.visibility = View.VISIBLE
                    }
                    true
                }
                else -> false
            }
        }
    }

    /**
     * 设置按钮点击事件
     */
    private fun setupButtons(params: WindowManager.LayoutParams) {
        // Start按钮
        floatingView.findViewById<Button>(R.id.btn_start).setOnClickListener {
            startClicking()
            updateNotification()
        }

        // Stop按钮
        floatingView.findViewById<Button>(R.id.btn_stop).setOnClickListener {
            stopClicking()
            updateNotification()
        }

        // Test按钮
        floatingView.findViewById<Button>(R.id.btn_test).setOnClickListener {
            testClick()
        }

        // Image Recognition测试按钮
        floatingView.findViewById<Button>(R.id.btn_test_image).setOnClickListener {
            testImageRecognition()
        }

        // Close按钮 - 收起菜单
        floatingView.findViewById<Button>(R.id.btn_close).setOnClickListener {
            expandedView.visibility = View.GONE
            collapsedView.visibility = View.VISIBLE
        }

        // Exit按钮 - 关闭服务
        floatingView.findViewById<Button>(R.id.btn_exit).setOnClickListener {
            stopClicking()
            stopSelf()
        }
    }

    /**
     * 开始自动点击（智能版本）
     * 优先级：找图 > 找字 > 坐标点击
     */
    private fun startClicking() {
        if (isRunning) return
        
        isRunning = true
        updateStatus("Running...")
        updateStepText("正在启动...")
        updateLog("开始智能自动点击")

        clickThread = Thread {
            try {
                while (isRunning) {
                    // 执行完整的11步流程
                    for (index in clickCoordinates.indices) {
                        if (!isRunning) break
                        
                        val stepName = getStepName(index)
                        updateStepText("正在执行: $stepName")
                        updateLog("开始步骤${index + 1}: $stepName")
                        
                        // 智能点击：先尝试找图，再找字，最后使用坐标
                        val success = performSmartClick(index)
                        
                        if (success) {
                            updateLog("步骤${index + 1}完成: $stepName")
                        } else {
                            updateLog("步骤${index + 1}失败: $stepName")
                        }
                        
                        Thread.sleep(clickDelays.getOrElse(index) { 2000 }) // 使用预设延迟
                    }
                    
                    // 一轮结束，等待2秒后重新开始
                    if (isRunning) {
                        updateStepText("一轮结束，等待2秒后重新开始...")
                        updateLog("一轮执行完成，等待2秒...")
                        Thread.sleep(2000)
                        updateStepText("开始下一轮...")
                        updateLog("开始下一轮循环")
                    }
                }
            } catch (e: InterruptedException) {
                // 线程被中断，正常退出
                updateLog("自动点击被中断")
            } finally {
                updateStepText("已停止")
                updateStatus("● Stopped")
            }
        }.apply {
            isDaemon = true
            start()
        }
    }
    
    /**
     * 智能点击：优先找图，其次找字，最后坐标点击
     */
    private fun performSmartClick(index: Int): Boolean {
        val stepName = getStepName(index)
        val templateName = getTemplateName(index)
        val textTemplate = getTextTemplate(index)
        val fallbackCoordinate = clickCoordinates[index]
        
        updateLog("智能点击步骤${index + 1}: $stepName")
        
        // 1. 先尝试找图
        if (templateName != "unknown") {
            updateLog("尝试找图: $templateName")
            val imageResult = imageRecognizer.findImage(templateName)
            if (imageResult.success && imageResult.confidence >= 90) {
                updateLog("找图成功! ${imageResult.message}")
                // 使用找图找到的坐标
                return performClick(imageResult.x, imageResult.y, "找图")
            } else {
                updateLog("找图失败: ${imageResult.message}")
            }
        }
        
        // 2. 尝试找字
        if (textTemplate.isNotEmpty()) {
            updateLog("尝试找字: $textTemplate")
            val textResult = imageRecognizer.findText(textTemplate)
            if (textResult.success && textResult.confidence >= 90) {
                updateLog("找字成功! ${textResult.message}")
                // 使用找字找到的坐标
                return performClick(textResult.x, textResult.y, "找字")
            } else {
                updateLog("找字失败: ${textResult.message}")
            }
        }
        
        // 3. 兜底：使用固定坐标
        updateLog("使用兜底坐标: (${fallbackCoordinate.first}, ${fallbackCoordinate.second})")
        return performClick(fallbackCoordinate.first, fallbackCoordinate.second, "坐标点击")
    }
    
    /**
     * 获取步骤名称
     */
    private fun getStepName(index: Int): String {
        return when (index) {
            0 -> "登录"
            1 -> "关闭弹窗"
            2 -> "游戏大厅"
            3 -> "王者峡谷匹配"
            4 -> "选择人机模式"
            5 -> "开始游戏"
            6 -> "准备游戏"
            7 -> "等待进入游戏"
            8 -> "游戏中（等待结束）"
            9 -> "游戏结束"
            10 -> "结算英雄"
            else -> "未知步骤"
        }
    }
    
    /**
     * 获取步骤对应的模板名称（用于图像识别）
     */
    private fun getTemplateName(index: Int): String {
        return when (index) {
            0 -> "login_button"
            1 -> "close_popup"
            2 -> "game_hall"
            3 -> "match_arena"
            4 -> "ai_mode"
            5 -> "start_game"
            6 -> "ready_game"
            7 -> "enter_game"
            8 -> "in_game"
            9 -> "game_over"
            10 -> "settlement"
            else -> "unknown"
        }
    }
    
    /**
     * 获取步骤对应的文字模板（用于文字识别）
     */
    private fun getTextTemplate(index: Int): String {
        return when (index) {
            5 -> "开始游戏"  // 步骤5：开始游戏
            6 -> "准备"      // 步骤6：准备游戏
            7 -> "确认"      // 步骤7：确认进入
            9 -> "返回房间"  // 步骤9：游戏结束（返回房间）
            else -> ""
        }
    }

    /**
     * 停止自动点击
     */
    private fun stopClicking() {
        isRunning = false
        clickThread?.interrupt()
        clickThread = null
        updateStatus("● Stopped")
        updateStepText("已停止")
        updateLog("自动点击已停止")
    }

    /**
     * 获取屏幕分辨率并自动缩放坐标
     */
    private fun getScaledCoordinates(x: Int, y: Int): Pair<Int, Int> {
        // 基准分辨率 1280x720
        val baseWidth = 1280
        val baseHeight = 720
        
        // 这里需要获取实际屏幕分辨率
        // 暂时返回原始坐标，实际开发时需要获取DisplayMetrics
        return Pair(x, y)
        
        // 实际代码应该是：
        // val displayMetrics = applicationContext.resources.displayMetrics
        // val screenWidth = displayMetrics.widthPixels
        // val screenHeight = displayMetrics.heightPixels
        // 
        // val scaleX = screenWidth.toFloat() / baseWidth
        // val scaleY = screenHeight.toFloat() / baseHeight
        // 
        // val scaledX = (x * scaleX).toInt()
        // val scaledY = (y * scaleY).toInt()
        // return Pair(scaledX, scaledY)
    }

    /**
     * 执行点击
     */
    private fun performClick(x: Int, y: Int): Boolean {
        return performClick(x, y, "手动点击")
    }

    /**
     * 执行点击（带来源）
     */
    private fun performClick(x: Int, y: Int, source: String): Boolean {
        // 获取适配当前分辨率的坐标
        val (scaledX, scaledY) = getScaledCoordinates(x, y)
        
        // 记录日志
        logClick(scaledX, scaledY, source)
        
        // 方法1: 尝试使用ROOT权限（优先）
        if (performRootClick(scaledX, scaledY)) {
            updateLog("[$source] 使用ROOT权限点击 ($scaledX, $scaledY)")
            return true
        }
        
        // 方法2: 尝试使用无障碍服务
        if (performAccessibilityClick(scaledX, scaledY)) {
            updateLog("[$source] 使用无障碍服务点击 ($scaledX, $scaledY)")
            return true
        }
        
        // 方法3: 如果以上都失败，尝试普通点击（可能需要adb调试权限）
        if (performAdbClick(scaledX, scaledY)) {
            updateLog("[$source] 使用ADB权限点击 ($scaledX, $scaledY)")
            return true
        }
        
        updateLog("[$source] 点击失败，请检查ROOT或无障碍服务权限")
        return false
    }

    /**
     * 使用ROOT权限点击
     */
    private fun performRootClick(x: Int, y: Int): Boolean {
        return try {
            val command = "input tap $x $y"
            val process = Runtime.getRuntime().exec(arrayOf("su", "-c", command))
            process.waitFor(1, TimeUnit.SECONDS)
            val result = process.exitValue() == 0
            if (result) {
                updateLog("ROOT点击成功: $x, $y")
            }
            result
        } catch (e: Exception) {
            updateLog("ROOT点击失败: ${e.message}")
            false
        }
    }

    /**
     * 使用无障碍服务点击
     */
    private fun performAccessibilityClick(x: Int, y: Int): Boolean {
        return try {
            val result = AccessibilityService.performClick(x, y)
            if (result) {
                updateLog("无障碍点击成功: $x, $y")
            } else {
                updateLog("无障碍服务未启用或版本太低")
            }
            result
        } catch (e: Exception) {
            updateLog("无障碍点击异常: ${e.message}")
            false
        }
    }

    /**
     * 使用ADB调试权限点击
     */
    private fun performAdbClick(x: Int, y: Int): Boolean {
        return try {
            val command = "input tap $x $y"
            val process = Runtime.getRuntime().exec(command)
            process.waitFor(1, TimeUnit.SECONDS)
            val result = process.exitValue() == 0
            if (result) {
                updateLog("ADB点击成功: $x, $y")
            }
            result
        } catch (e: Exception) {
            updateLog("ADB点击失败: ${e.message}")
            false
        }
    }

    /**
     * 测试点击
     */
    private fun testClick() {
        Thread {
            updateLog("开始测试点击...")
            updateStepText("测试点击中...")
            
            // 测试屏幕中心
            val testX = 640
            val testY = 360
            val (scaledX, scaledY) = getScaledCoordinates(testX, testY)
            updateLog("测试点击屏幕中心: ($testX, $testY) -> ($scaledX, $scaledY)")
            
            if (performClick(testX, testY, "测试")) {
                updateLog("测试点击成功!")
                updateStepText("测试完成: 成功")
            } else {
                updateLog("测试点击失败!")
                updateStepText("测试完成: 失败")
            }
        }.start()
    }
    
    /**
     * 测试图像识别功能
     */
    private fun testImageRecognition() {
        Thread {
            updateLog("开始测试图像识别...")
            updateStepText("测试图像识别中...")
            
            try {
                // 测试所有模板的识别
                val result = imageRecognizer.testRecognition()
                updateLog("图像识别测试结果:\n$result")
                updateStepText("图像识别测试完成")
                
                // 测试智能点击
                updateLog("\n=== 测试智能点击 ===")
                for (i in 0..3) { // 测试前4个步骤
                    val stepName = getStepName(i)
                    val success = performSmartClick(i)
                    updateLog("步骤$i ($stepName): ${if (success) "成功" else "失败"}")
                    Thread.sleep(1000)
                }
                
                updateLog("智能点击测试完成")
                updateStepText("所有测试完成")
                
            } catch (e: Exception) {
                updateLog("图像识别测试失败: ${e.message}")
                updateStepText("测试失败")
            }
        }.start()
    }

    /**
     * 更新状态文本
     */
    private fun updateStatus(status: String) {
        floatingView.post {
            floatingView.findViewById<TextView>(R.id.tv_status)?.text = status
        }
    }
    
    /**
     * 更新步骤文本
     */
    private fun updateStepText(step: String) {
        floatingView.post {
            floatingView.findViewById<TextView>(R.id.tv_step)?.text = step
        }
    }
    
    /**
     * 更新日志
     */
    private fun updateLog(log: String) {
        floatingView.post {
            val logView = floatingView.findViewById<TextView>(R.id.tv_log)
            if (logView != null) {
                val currentText = logView.text.toString()
                val newText = "$currentText\n$log"
                // 保留最近10行日志
                val lines = newText.split("\n")
                logView.text = if (lines.size > 10) {
                    lines.takeLast(10).joinToString("\n")
                } else {
                    newText
                }
            }
        }
    }
    
    /**
     * 记录点击日志
     */
    private fun logClick(x: Int, y: Int, source: String = "未知") {
        val time = System.currentTimeMillis()
        updateLog("[$time] [$source] 点击坐标: ($x, $y)")
    }

    /**
     * 更新通知
     */
    private fun updateNotification() {
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, createNotification())
    }

    override fun onDestroy() {
        super.onDestroy()
        stopClicking()
        if (::floatingView.isInitialized) {
            windowManager.removeView(floatingView)
        }
    }

    companion object {
        private const val CHANNEL_ID = "WangZheAutoClickerChannel"
        private const val NOTIFICATION_ID = 1
    }
}
