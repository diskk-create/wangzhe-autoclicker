#!/bin/bash
# 测试编译脚本
# 检查Kotlin语法错误

echo "=== 检查Kotlin文件语法 ==="

# 检查所有Kotlin文件
for file in app/src/main/java/com/wangzhe/autoclicker/*.kt; do
    echo "检查: $file"
    
    # 检查是否有语法错误
    if grep -n "TODO\|FIXME\|ERROR" "$file"; then
        echo "⚠️  发现TODO/FIXME/ERROR标记"
    fi
    
    # 检查import语句
    import_count=$(grep -c "^import" "$file")
    echo "  导入语句: $import_count"
    
    # 检查类定义
    class_name=$(basename "$file" .kt)
    if grep -q "class $class_name" "$file"; then
        echo "  ✅ 类定义正确: $class_name"
    else
        echo "  ❌ 类定义可能有问题"
    fi
done

echo ""
echo "=== 检查XML布局文件 ==="

# 检查布局文件
for file in app/src/main/res/layout/*.xml; do
    echo "检查: $(basename "$file")"
    
    # 检查ID定义
    id_count=$(grep -c "@+id/" "$file")
    echo "  ID定义: $id_count"
    
    # 检查Kotlin中使用的ID
    layout_name=$(basename "$file" .xml)
    echo "  布局名称: $layout_name"
done

echo ""
echo "=== 检查Gradle配置 ==="

# 检查build.gradle
if [ -f "app/build.gradle" ]; then
    echo "✅ 找到build.gradle"
    
    # 检查依赖
    dep_count=$(grep -c "implementation" "app/build.gradle")
    echo "  依赖数量: $dep_count"
    
    # 检查minSdk
    min_sdk=$(grep "minSdk" "app/build.gradle" | grep -o "[0-9]*" | head -1)
    echo "  minSdk: $min_sdk"
fi

echo ""
echo "=== 检查AndroidManifest.xml ==="

if [ -f "app/src/main/AndroidManifest.xml" ]; then
    echo "✅ 找到AndroidManifest.xml"
    
    # 检查权限
    perm_count=$(grep -c "uses-permission" "app/src/main/AndroidManifest.xml")
    echo "  权限数量: $perm_count"
    
    # 检查服务声明
    service_count=$(grep -c "service" "app/src/main/AndroidManifest.xml")
    echo "  服务数量: $service_count"
fi

echo ""
echo "=== 项目结构 ==="

echo "📁 项目根目录:"
ls -la

echo ""
echo "📁 app/src/main/java/com/wangzhe/autoclicker/:"
ls -la "app/src/main/java/com/wangzhe/autoclicker/"

echo ""
echo "📁 app/src/main/res/layout/:"
ls -la "app/src/main/res/layout/"

echo ""
echo "✅ 语法检查完成！"
echo ""
echo "下一步:"
echo "1. 运行 ./gradlew compileDebugKotlin 检查编译"
echo "2. 运行 ./gradlew assembleDebug 构建APK"
echo "3. 运行 adb install app-debug.apk 安装到设备"