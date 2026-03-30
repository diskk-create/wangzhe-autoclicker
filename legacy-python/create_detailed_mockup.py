"""
Generate a detailed UI mockup with annotations
"""
from PIL import Image, ImageDraw, ImageFont

# Create image
width, height = 800, 500
img = Image.new('RGB', (width, height), color=(245, 245, 250))
draw = ImageDraw.Draw(img)

# Fonts
try:
    font_title = ImageFont.truetype("arial.ttf", 24)
    font_normal = ImageFont.truetype("arial.ttf", 16)
    font_small = ImageFont.truetype("arial.ttf", 14)
    font_tiny = ImageFont.truetype("arial.ttf", 12)
except:
    font_title = font_normal = font_small = font_tiny = ImageFont.load_default()

# Title
draw.text((20, 20), "WangZhe Auto Clicker v3.4.0 - Floating Ball UI", fill=(30, 30, 30), font=font_title)

# ========== Left: Collapsed State ==========
draw.text((50, 70), "收起状态", fill=(80, 80, 80), font=font_normal)

# Phone frame
phone_x, phone_y = 50, 100
phone_w, phone_h = 200, 350
draw.rounded_rectangle([phone_x, phone_y, phone_x + phone_w, phone_y + phone_h], 
                       radius=20, outline=(180, 180, 180), width=3)

# Phone screen
draw.rectangle([phone_x + 10, phone_y + 30, phone_x + phone_w - 10, phone_y + phone_h - 10],
               fill=(220, 220, 230))

# Floating ball (collapsed)
ball_x = phone_x + phone_w - 50
ball_y = phone_y + phone_h // 2
ball_size = 50

# Shadow
draw.ellipse([ball_x + 2, ball_y - 2, ball_x + ball_size + 2, ball_y + ball_size - 2],
             fill=(100, 100, 100))
# Ball
draw.ellipse([ball_x, ball_y, ball_x + ball_size, ball_y + ball_size],
             fill=(51, 153, 230))
# Highlight
draw.ellipse([ball_x + 8, ball_y + 18, ball_x + 30, ball_y + 32],
             fill=(255, 255, 255, 150))
# Icon
cx, cy = ball_x + 25, ball_y + 25
draw.polygon([(cx - 6, cy - 8), (cx - 6, cy + 8), (cx + 10, cy)], fill=(255, 255, 255))

# Annotation
draw.line([(ball_x, ball_y + ball_size + 10), (ball_x, ball_y + ball_size + 40)], 
          fill=(255, 100, 100), width=2)
draw.text((ball_x - 40, ball_y + ball_size + 45), "点击展开菜单", fill=(255, 100, 100), font=font_small)

# ========== Middle: Expanded State ==========
draw.text((320, 70), "展开状态", fill=(80, 80, 80), font=font_normal)

# Phone frame
phone_x2, phone_y2 = 300, 100
draw.rounded_rectangle([phone_x2, phone_y2, phone_x2 + phone_w, phone_y2 + phone_h],
                       radius=20, outline=(180, 180, 180), width=3)

# Phone screen
draw.rectangle([phone_x2 + 10, phone_y2 + 30, phone_x2 + phone_w - 10, phone_y2 + phone_h - 10],
               fill=(220, 220, 230))

# Menu panel
menu_x = phone_x2 + phone_w - 180
menu_y = phone_y2 + 80
menu_w, menu_h = 170, 250

draw.rounded_rectangle([menu_x + 3, menu_y + 3, menu_x + menu_w + 3, menu_y + menu_h + 3],
                       radius=12, fill=(50, 50, 50))
draw.rounded_rectangle([menu_x, menu_y, menu_x + menu_w, menu_y + menu_h],
                       radius=12, fill=(30, 30, 30))

# Menu content
draw.text((menu_x + 20, menu_y + 15), "WangZhe", fill=(240, 240, 240), font=font_small)
draw.text((menu_x + 50, menu_y + 35), "v3.4.0", fill=(120, 120, 120), font=font_tiny)
draw.text((menu_x + 55, menu_y + 55), "● Ready", fill=(0, 255, 0), font=font_tiny)

# Buttons
button_y = menu_y + 80
for text in ["▶ Start", "⏸ Stop", "🔄 Test", "✕ Exit"]:
    draw.rounded_rectangle([menu_x + 15, button_y, menu_x + menu_w - 15, button_y + 30],
                          radius=6, fill=(60, 60, 60))
    draw.text((menu_x + 55, button_y + 6), text, fill=(255, 255, 255), font=font_tiny)
    button_y += 38

# Floating ball (expanded, green)
ball_x2 = menu_x - 60
ball_y2 = menu_y + menu_h // 2 - 25
ball_size2 = 50

draw.ellipse([ball_x2 + 2, ball_y2 - 2, ball_x2 + ball_size2 + 2, ball_y2 + ball_size2 - 2],
             fill=(100, 100, 100))
draw.ellipse([ball_x2, ball_y2, ball_x2 + ball_size2, ball_y2 + ball_size2],
             fill=(76, 204, 76))
draw.ellipse([ball_x2 + 8, ball_y2 + 18, ball_x2 + 30, ball_y2 + 32],
             fill=(255, 255, 255, 150))
cx2, cy2 = ball_x2 + 25, ball_y2 + 25
draw.polygon([(cx2 - 6, cy2 - 8), (cx2 - 6, cy2 + 8), (cx2 + 10, cy2)], fill=(255, 255, 255))

# Annotation
draw.line([(menu_x + menu_w, menu_y + menu_h // 2), (menu_x + menu_w + 20, menu_y + menu_h // 2)],
          fill=(100, 100, 255), width=2)
draw.text((menu_x + menu_w + 25, menu_y + menu_h // 2 - 10), "菜单展开", fill=(100, 100, 255), font=font_small)

# ========== Right: Features ==========
draw.text((550, 70), "功能特性", fill=(80, 80, 80), font=font_normal)

features = [
    "✓ 悬浮球显示",
    "✓ 自由拖动位置",
    "✓ 点击展开菜单",
    "✓ 点击外部收起",
    "✓ 流畅动画效果",
    "✓ 置顶显示",
    "✓ 极简界面",
    "",
    "颜色状态：",
    "● 蓝色 = 就绪",
    "● 绿色 = 运行/展开",
    "● 黄色 = 已停止"
]

feature_y = 110
for text in features:
    color = (80, 80, 80) if text.startswith("✓") or text.startswith("●") else (60, 60, 60)
    if "蓝色" in text:
        color = (51, 153, 230)
    elif "绿色" in text:
        color = (76, 204, 76)
    elif "黄色" in text:
        color = (255, 200, 0)
    
    draw.text((550, feature_y), text, fill=color, font=font_small)
    feature_y += 25

# Save
output_path = r"C:\Users\Administrator\Desktop\floating_ball_detailed.png"
img.save(output_path, "PNG")
print(f"Detailed mockup saved to: {output_path}")
