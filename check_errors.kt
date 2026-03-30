// 这是一个简单的Kotlin语法检查脚本
// 用于检查FloatingWindowService.kt中的潜在问题

import java.io.File

fun main() {
    val filePath = "app/src/main/java/com/wangzhe/autoclicker/FloatingWindowService.kt"
    val file = File(filePath)
    
    if (!file.exists()) {
        println("错误: 文件不存在: $filePath")
        return
    }
    
    println("=== 检查FloatingWindowService.kt文件 ===")
    println("文件大小: ${file.length()} bytes")
    println("文件行数: ${file.readLines().size}")
    
    val content = file.readText()
    
    // 检查常见问题
    checkImports(content)
    checkMethodSignatures(content)
    checkReferences(content)
    checkSyntax(content)
    
    println("\n=== 检查完成 ===")
}

fun checkImports(content: String) {
    println("\n1. 检查import语句:")
    val imports = content.lines().filter { it.startsWith("import ") }
    imports.forEach { println("  ✓ $it") }
    
    // 检查必要的import
    val requiredImports = listOf(
        "android.widget.TextView",
        "android.view.View",
        "android.os.IBinder"
    )
    
    requiredImports.forEach { required ->
        if (imports.any { it.contains(required) }) {
            println("  ✓ 找到: $required")
        } else {
            println("  ⚠️ 未找到: $required")
        }
    }
}

fun checkMethodSignatures(content: String) {
    println("\n2. 检查方法签名:")
    
    // 检查主要方法是否存在
    val methods = listOf(
        "override fun onBind",
        "override fun onCreate",
        "override fun onDestroy",
        "private fun initFloatingWindow",
        "private fun startClicking",
        "private fun stopClicking",
        "private fun performClick",
        "private fun getScaledCoordinates"
    )
    
    methods.forEach { method ->
        if (content.contains(method)) {
            println("  ✓ 找到: $method")
        } else {
            println("  ❌ 未找到: $method")
        }
    }
}

fun checkReferences(content: String) {
    println("\n3. 检查资源引用:")
    
    // 检查布局文件中定义的ID是否在代码中使用
    val layoutIds = listOf(
        "R.id.tv_step",
        "R.id.tv_log",
        "R.id.collapsed_view",
        "R.id.expanded_view",
        "R.id.btn_start",
        "R.id.btn_stop",
        "R.id.btn_test",
        "R.id.btn_close",
        "R.id.btn_exit",
        "R.id.tv_status"
    )
    
    layoutIds.forEach { id ->
        if (content.contains(id)) {
            println("  ✓ 引用: $id")
        } else {
            println("  ⚠️ 未引用: $id")
        }
    }
}

fun checkSyntax(content: String) {
    println("\n4. 检查语法:")
    
    // 检查常见的语法问题
    val checks = listOf(
        Check("大括号匹配", content.count { it == '{' } == content.count { it == '}' }, "大括号不匹配"),
        Check("小括号匹配", content.count { it == '(' } == content.count { it == ')' }, "小括号不匹配"),
        Check("中括号匹配", content.count { it == '[' } == content.count { it == ']' }, "中括号不匹配"),
        Check("字符串引号匹配", content.count { it == '"' } % 2 == 0, "字符串引号不匹配"),
        Check("类定义", content.contains("class FloatingWindowService : Service()"), "缺少类定义"),
        Check("companion object", content.contains("companion object"), "缺少companion object"),
        Check("结尾大括号", content.trim().endsWith('}'), "文件结尾不完整")
    )
    
    checks.forEach { check ->
        if (check.passed) {
            println("  ✓ ${check.name}")
        } else {
            println("  ❌ ${check.name}: ${check.message}")
        }
    }
}

data class Check(val name: String, val passed: Boolean, val message: String)

main()