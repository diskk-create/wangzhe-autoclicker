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

    // 点击坐标（基于1280x720分辨率）
    private val clickCoordinates = listOf(
        Pair(100, 200),   // 步骤1
        Pair(200, 300),   // 步骤2
        // ... 添加更多坐标
    )

    override fun onCreate() {
        super.onCreate()

        // 创建通知渠道（Android 8.0+需要）
        createNotificationChannel()

        // 启动前台服务
        startForeground(NOTIFICATION_ID, createNotification())

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
     * 开始自动点击
     */
    private fun startClicking() {
        if (isRunning) return
        
        isRunning = true
        updateStatus("Running...")

        clickThread = Thread {
            while (isRunning) {
                try {
                    for ((x, y) in clickCoordinates) {
                        if (!isRunning) break
                        performClick(x, y)
                        Thread.sleep(1000) // 1秒间隔
                    }
                    Thread.sleep(2000) // 一轮结束等待2秒
                } catch (e: InterruptedException) {
                    break
                }
            }
        }.apply {
            isDaemon = true
            start()
        }
    }

    /**
     * 停止自动点击
     */
    private fun stopClicking() {
        isRunning = false
        clickThread?.interrupt()
        clickThread = null
        updateStatus("Stopped")
    }

    /**
     * 执行点击
     */
    private fun performClick(x: Int, y: Int) {
        try {
            // 尝试使用ROOT权限
            val command = "input tap $x $y"
            val process = Runtime.getRuntime().exec(arrayOf("su", "-c", command))
            process.waitFor()
            
            if (process.exitValue() == 0) {
                return
            }
        } catch (e: Exception) {
            // ROOT权限失败，尝试使用无障碍服务
        }

        // 使用无障碍服务点击
        performAccessibilityClick(x, y)
    }

    /**
     * 使用无障碍服务点击
     */
    private fun performAccessibilityClick(x: Int, y: Int) {
        // TODO: 实现无障碍服务点击
        // AccessibilityService需要额外实现
    }

    /**
     * 测试点击
     */
    private fun testClick() {
        Thread {
            performClick(640, 360) // 点击屏幕中心
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
