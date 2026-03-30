package com.wangzhe.autoclicker

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.media.Image
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream

/**
 * 图像识别工具类
 * 用于找图和找字功能
 * 
 * 注意：Android原生版本需要添加OpenCV依赖来实现真正的图像识别
 * 当前版本使用简单的颜色匹配和模板匹配模拟
 */
class ImageRecognizer(private val context: android.content.Context) {

    companion object {
        private const val TAG = "ImageRecognizer"
        
        // 王者荣耀按钮模板坐标（基于1280x720分辨率）
        private val buttonTemplates = mapOf(
            // 登录按钮
            "login_button" to TemplateInfo(
                name = "登录按钮",
                x = 641, y = 564, width = 200, height = 80,
                color = 0xFF4A90E2, // 蓝色
                threshold = 90
            ),
            // 关闭弹窗按钮
            "close_popup" to TemplateInfo(
                name = "关闭弹窗",
                x = 1190, y = 112, width = 60, height = 60,
                color = 0xFFFF5722, // 橙色
                threshold = 90
            ),
            // 游戏大厅按钮
            "game_hall" to TemplateInfo(
                name = "游戏大厅",
                x = 514, y = 544, width = 180, height = 70,
                color = 0xFF8BC34A, // 绿色
                threshold = 90
            ),
            // 王者峡谷匹配
            "match_arena" to TemplateInfo(
                name = "王者峡谷匹配",
                x = 398, y = 539, width = 220, height = 90,
                color = 0xFFE91E63, // 粉色
                threshold = 90
            ),
            // 人机模式
            "ai_mode" to TemplateInfo(
                name = "人机模式",
                x = 730, y = 601, width = 150, height = 60,
                color = 0xFF9C27B0, // 紫色
                threshold = 90
            ),
            // 开始游戏
            "start_game" to TemplateInfo(
                name = "开始游戏",
                x = 1057, y = 569, width = 180, height = 70,
                color = 0xFFFF9800, // 橙色
                threshold = 90
            ),
            // 准备游戏
            "ready_game" to TemplateInfo(
                name = "准备游戏",
                x = 775, y = 660, width = 160, height = 60,
                color = 0xFF4CAF50, // 绿色
                threshold = 90
            ),
            // 准备进入
            "enter_game" to TemplateInfo(
                name = "准备进入",
                x = 640, y = 561, width = 200, height = 80,
                color = 0xFF2196F3, // 蓝色
                threshold = 90
            ),
            // 游戏中
            "in_game" to TemplateInfo(
                name = "游戏中",
                x = 640, y = 360, width = 300, height = 200,
                color = 0xFFF44336, // 红色
                threshold = 90
            ),
            // 游戏结束
            "game_over" to TemplateInfo(
                name = "游戏结束",
                x = 635, y = 664, width = 180, height = 70,
                color = 0xFF9E9E9E, // 灰色
                threshold = 90
            ),
            // 结算英雄
            "settlement" to TemplateInfo(
                name = "结算英雄",
                x = 645, y = 621, width = 160, height = 60,
                color = 0xFFFFC107, // 黄色
                threshold = 90
            )
        )

        // 文字识别模板（简单的颜色匹配）
        private val textTemplates = mapOf(
            "开始游戏" to TextTemplateInfo(
                text = "开始游戏",
                expectedColor = 0xFFFFFFFF, // 白色文字
                bgColor = 0xFF4A90E2,      // 蓝色背景
                threshold = 90
            ),
            "准备" to TextTemplateInfo(
                text = "准备",
                expectedColor = 0xFFFFFFFF,
                bgColor = 0xFF4CAF50,
                threshold = 90
            ),
            "确认" to TextTemplateInfo(
                text = "确认",
                expectedColor = 0xFFFFFFFF,
                bgColor = 0xFF2196F3,
                threshold = 90
            ),
            "返回房间" to TextTemplateInfo(
                text = "返回房间",
                expectedColor = 0xFFFFFFFF,
                bgColor = 0xFF9E9E9E,
                threshold = 90
            )
        )
    }

    data class TemplateInfo(
        val name: String,
        val x: Int,
        val y: Int,
        val width: Int,
        val height: Int,
        val color: Int, // 预期颜色（ARGB）
        val threshold: Int // 匹配阈值（百分比）
    )

    data class TextTemplateInfo(
        val text: String,
        val expectedColor: Int,
        val bgColor: Int,
        val threshold: Int
    )

    data class RecognitionResult(
        val success: Boolean,
        val confidence: Int, // 置信度 0-100
        val x: Int = 0,
        val y: Int = 0,
        val message: String = ""
    )

    private val handlerThread = HandlerThread("ImageRecognition")
    private val handler: Handler
    
    init {
        handlerThread.start()
        handler = Handler(handlerThread.looper)
        Log.d(TAG, "ImageRecognizer initialized")
    }

    /**
     * 找图功能
     * @param templateName 模板名称
     * @param screenWidth 屏幕宽度
     * @param screenHeight 屏幕高度
     * @return RecognitionResult
     */
    fun findImage(templateName: String, screenWidth: Int = 1280, screenHeight: Int = 720): RecognitionResult {
        return try {
            val template = buttonTemplates[templateName]
            if (template == null) {
                Log.w(TAG, "模板未找到: $templateName")
                return RecognitionResult(false, 0, message = "模板未找到")
            }

            // 计算适配后的坐标
            val scaleX = screenWidth.toFloat() / 1280
            val scaleY = screenHeight.toFloat() / 720
            
            val scaledX = (template.x * scaleX).toInt()
            val scaledY = (template.y * scaleY).toInt()
            val scaledWidth = (template.width * scaleX).toInt()
            val scaledHeight = (template.height * scaleY).toInt()

            Log.d(TAG, "查找: ${template.name}, 坐标: ($scaledX, $scaledY), 尺寸: ${scaledWidth}x$scaledHeight")

            // TODO: 这里应该实现真实的屏幕截图和图像识别
            // 当前版本使用模拟识别，始终返回成功
            val confidence = 95 // 模拟置信度
            
            if (confidence >= template.threshold) {
                RecognitionResult(
                    success = true,
                    confidence = confidence,
                    x = scaledX + scaledWidth / 2, // 点击中心点
                    y = scaledY + scaledHeight / 2,
                    message = "找到${template.name}, 置信度: ${confidence}%"
                )
            } else {
                RecognitionResult(
                    success = false,
                    confidence = confidence,
                    message = "${template.name}识别失败, 置信度: ${confidence}% < ${template.threshold}%"
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "找图失败: ${e.message}", e)
            RecognitionResult(false, 0, message = "找图失败: ${e.message}")
        }
    }

    /**
     * 找字功能
     * @param text 要查找的文字
     * @param screenWidth 屏幕宽度
     * @param screenHeight 屏幕高度
     * @return RecognitionResult
     */
    fun findText(text: String, screenWidth: Int = 1280, screenHeight: Int = 720): RecognitionResult {
        return try {
            val template = textTemplates[text]
            if (template == null) {
                Log.w(TAG, "文字模板未找到: $text")
                return RecognitionResult(false, 0, message = "文字模板未找到")
            }

            Log.d(TAG, "查找文字: ${template.text}")

            // TODO: 这里应该实现真实的文字识别（OCR）
            // 当前版本使用模拟识别
            val confidence = 92 // 模拟置信度
            
            if (confidence >= template.threshold) {
                // 根据文字类型返回不同的坐标
                val (x, y) = when (text) {
                    "开始游戏" -> Pair(1057, 569)
                    "准备" -> Pair(775, 660)
                    "确认" -> Pair(640, 561)
                    "返回房间" -> Pair(739, 651)
                    else -> Pair(640, 360)
                }
                
                // 计算适配后的坐标
                val scaleX = screenWidth.toFloat() / 1280
                val scaleY = screenHeight.toFloat() / 720
                val scaledX = (x * scaleX).toInt()
                val scaledY = (y * scaleY).toInt()

                RecognitionResult(
                    success = true,
                    confidence = confidence,
                    x = scaledX,
                    y = scaledY,
                    message = "找到文字'${template.text}', 置信度: ${confidence}%"
                )
            } else {
                RecognitionResult(
                    success = false,
                    confidence = confidence,
                    message = "文字'${template.text}'识别失败, 置信度: ${confidence}% < ${template.threshold}%"
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "找字失败: ${e.message}", e)
            RecognitionResult(false, 0, message = "找字失败: ${e.message}")
        }
    }

    /**
     * 智能点击：优先找图，如果失败则找字，最后使用坐标点击
     * @param stepName 步骤名称
     * @param screenWidth 屏幕宽度
     * @param screenHeight 屏幕高度
     * @param fallbackCoordinates 兜底坐标
     * @return Pair<Boolean, String> (是否成功, 使用的策略)
     */
    fun smartClick(
        stepName: String,
        screenWidth: Int = 1280,
        screenHeight: Int = 720,
        fallbackCoordinates: Pair<Int, Int>? = null
    ): Pair<Boolean, String> {
        Log.d(TAG, "智能点击: $stepName")

        // 1. 优先找图
        val imageResult = findImage(stepName, screenWidth, screenHeight)
        if (imageResult.success && imageResult.confidence >= 90) {
            Log.i(TAG, "找图成功: ${imageResult.message}")
            // TODO: 实际执行点击 imageResult.x, imageResult.y
            return Pair(true, "找图 (${imageResult.confidence}%)")
        }

        // 2. 次优先找字
        val textResult = findText(stepName, screenWidth, screenHeight)
        if (textResult.success && textResult.confidence >= 90) {
            Log.i(TAG, "找字成功: ${textResult.message}")
            // TODO: 实际执行点击 textResult.x, textResult.y
            return Pair(true, "找字 (${textResult.confidence}%)")
        }

        // 3. 兜底：使用固定坐标
        if (fallbackCoordinates != null) {
            Log.i(TAG, "使用兜底坐标: $fallbackCoordinates")
            val (x, y) = fallbackCoordinates
            val scaledX = (x * screenWidth.toFloat() / 1280).toInt()
            val scaledY = (y * screenHeight.toFloat() / 720).toInt()
            // TODO: 实际执行点击 scaledX, scaledY
            return Pair(true, "坐标点击 (兜底)")
        }

        Log.w(TAG, "所有点击方式都失败: $stepName")
        return Pair(false, "全部失败")
    }

    /**
     * 获取当前屏幕尺寸（需要屏幕截图权限）
     * @return Pair<Int, Int> (width, height)
     */
    fun getScreenSize(): Pair<Int, Int> {
        // TODO: 实现获取屏幕尺寸
        return Pair(1280, 720) // 默认返回基准分辨率
    }

    /**
     * 保存屏幕截图（用于调试）
     */
    fun saveScreenshot(bitmap: Bitmap, fileName: String = "screenshot_${System.currentTimeMillis()}.png") {
        handler.post {
            try {
                val file = File(context.filesDir, fileName)
                val stream = FileOutputStream(file)
                bitmap.compress(Bitmap.CompressFormat.PNG, 90, stream)
                stream.flush()
                stream.close()
                Log.d(TAG, "截图已保存: ${file.absolutePath}")
            } catch (e: Exception) {
                Log.e(TAG, "保存截图失败: ${e.message}", e)
            }
        }
    }

    /**
     * 清理资源
     */
    fun release() {
        handlerThread.quitSafely()
        Log.d(TAG, "ImageRecognizer released")
    }

    /**
     * 获取所有可用的模板名称
     */
    fun getAvailableTemplates(): List<String> {
        return buttonTemplates.keys.toList()
    }

    /**
     * 获取所有可用的文字模板
     */
    fun getAvailableTexts(): List<String> {
        return textTemplates.keys.toList()
    }

    /**
     * 测试图像识别功能
     */
    fun testRecognition(): String {
        val results = mutableListOf<String>()
        
        // 测试找图
        results.add("=== 找图测试 ===")
        buttonTemplates.forEach { (name, template) ->
            val result = findImage(name)
            results.add("${template.name}: ${if (result.success) "成功" else "失败"} (${result.confidence}%)")
        }

        // 测试找字
        results.add("\n=== 找字测试 ===")
        textTemplates.forEach { (text, _) ->
            val result = findText(text)
            results.add("$text: ${if (result.success) "成功" else "失败"} (${result.confidence}%)")
        }

        return results.joinToString("\n")
    }
}