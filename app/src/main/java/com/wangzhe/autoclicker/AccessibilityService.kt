package com.wangzhe.autoclicker

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.graphics.Path
import android.os.Build
import android.view.accessibility.AccessibilityEvent

/**
 * 无障碍服务
 * 用于在没有ROOT权限的情况下执行点击
 */
class AccessibilityService : AccessibilityService() {

    companion object {
        var instance: AccessibilityService? = null
            private set

        fun isenabled(): Boolean {
            return instance != null
        }

        fun performClick(x: Int, y: Int): Boolean {
            return instance?.performClickInternal(x, y) ?: false
        }
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // 不需要处理事件
    }

    override fun onInterrupt() {
        // 中断处理
    }

    override fun onDestroy() {
        super.onDestroy()
        instance = null
    }

    /**
     * 执行点击
     */
    private fun performClickInternal(x: Int, y: Int): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) {
            return false
        }

        val path = Path().apply {
            moveTo(x.toFloat(), y.toFloat())
        }

        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 100))
            .build()

        return dispatchGesture(gesture, null, null)
    }

    /**
     * 执行滑动手势
     */
    private fun performSwipeInternal(startX: Int, startY: Int, endX: Int, endY: Int, duration: Long): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.N) {
            return false
        }

        val path = Path().apply {
            moveTo(startX.toFloat(), startY.toFloat())
            lineTo(endX.toFloat(), endY.toFloat())
        }

        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, duration))
            .build()

        return dispatchGesture(gesture, null, null)
    }
}
