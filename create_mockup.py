"""
Generate a mockup of the floating ball UI
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create image
width, height = 400, 600
img = Image.new('RGB', (width, height), color=(240, 240, 245))
draw = ImageDraw.Draw(img)

# Title
try:
    font_title = ImageFont.truetype("arial.ttf", 20)
    font_normal = ImageFont.truetype("arial.ttf", 14)
    font_small = ImageFont.truetype("arial.ttf", 12)
except:
    font_title = ImageFont.load_default()
    font_normal = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Draw background pattern
for i in range(0, width, 40):
    draw.line([(i, 0), (i, height)], fill=(230, 230, 235), width=1)
for i in range(0, height, 40):
    draw.line([(0, i), (width, i)], fill=(230, 230, 235), width=1)

# Draw floating ball (collapsed state)
ball_x, ball_y = 50, 280
ball_size = 70

# Ball shadow
draw.ellipse(
    [ball_x + 4, ball_y - 4, ball_x + ball_size + 4, ball_y + ball_size - 4],
    fill=(100, 100, 100, 100)
)

# Ball glow
draw.ellipse(
    [ball_x - 5, ball_y - 5, ball_x + ball_size + 5, ball_y + ball_size + 5],
    fill=(51, 153, 230, 50)
)

# Main ball
draw.ellipse(
    [ball_x, ball_y, ball_x + ball_size, ball_y + ball_size],
    fill=(51, 153, 230)
)

# Ball highlight
draw.ellipse(
    [ball_x + 12, ball_y + 25, ball_x + 42, ball_y + 43],
    fill=(255, 255, 255, 100)
)

# Play icon
cx, cy = ball_x + 35, ball_y + 35
draw.polygon([(cx - 8, cy - 10), (cx - 8, cy + 10), (cx + 12, cy)], fill=(255, 255, 255))

# Label
draw.text((10, 360), "收起状态", fill=(100, 100, 100), font=font_normal)
draw.text((10, 380), "(点击展开菜单)", fill=(150, 150, 150), font=font_small)

# Draw expanded menu
menu_x, menu_y = 150, 100
menu_width, menu_height = 200, 320

# Menu shadow
draw.rounded_rectangle(
    [menu_x + 5, menu_y + 5, menu_x + menu_width + 5, menu_y + menu_height + 5],
    radius=12,
    fill=(50, 50, 50, 100)
)

# Menu background
draw.rounded_rectangle(
    [menu_x, menu_y, menu_x + menu_width, menu_y + menu_height],
    radius=12,
    fill=(30, 30, 30)
)

# Menu title
draw.text((menu_x + 50, menu_y + 20), "WangZhe Clicker", fill=(240, 240, 240), font=font_title)
draw.text((menu_x + 75, menu_y + 50), "v3.4.0", fill=(150, 150, 150), font=font_small)

# Status
draw.text((menu_x + 70, menu_y + 80), "● Ready", fill=(0, 255, 0), font=font_normal)

# Buttons
button_y = menu_y + 110
buttons = [
    ("▶ Start", (38, 153, 64)),
    ("⏸ Stop", (179, 64, 64)),
    ("🔄 Test", (64, 115, 191)),
    ("✕ Exit", (102, 102, 102))
]

for text, color in buttons:
    # Button background
    draw.rounded_rectangle(
        [menu_x + 15, button_y, menu_x + menu_width - 15, button_y + 40],
        radius=8,
        fill=color
    )
    # Button text
    draw.text((menu_x + 75, button_y + 10), text, fill=(255, 255, 255), font=font_normal)
    button_y += 50

# Draw expanded ball
ball_x2, ball_y2 = 50, 450
ball_size2 = 60

# Ball shadow
draw.ellipse(
    [ball_x2 + 3, ball_y2 - 3, ball_x2 + ball_size2 + 3, ball_y2 + ball_size2 - 3],
    fill=(100, 100, 100, 100)
)

# Ball glow (green for expanded)
draw.ellipse(
    [ball_x2 - 5, ball_y2 - 5, ball_x2 + ball_size2 + 5, ball_y2 + ball_size2 + 5],
    fill=(76, 204, 76, 50)
)

# Main ball (green for expanded)
draw.ellipse(
    [ball_x2, ball_y2, ball_x2 + ball_size2, ball_y2 + ball_size2],
    fill=(76, 204, 76)
)

# Ball highlight
draw.ellipse(
    [ball_x2 + 10, ball_y2 + 22, ball_x2 + 36, ball_y2 + 38],
    fill=(255, 255, 255, 100)
)

# Play icon
cx2, cy2 = ball_x2 + 30, ball_y2 + 30
draw.polygon([(cx2 - 7, cy2 - 8), (cx2 - 7, cy2 + 8), (cx2 + 10, cy2)], fill=(255, 255, 255))

# Label
draw.text((10, 520), "展开状态", fill=(100, 100, 100), font=font_normal)
draw.text((10, 540), "(绿色 = 菜单展开)", fill=(150, 150, 150), font=font_small)

# Legend
draw.text((150, 430), "● 蓝色 = 就绪", fill=(51, 153, 230), font=font_small)
draw.text((150, 450), "● 绿色 = 运行/展开", fill=(76, 204, 76), font=font_small)

# Save
output_path = r"C:\Users\Administrator\Desktop\floating_ball_mockup.png"
img.save(output_path, "PNG")
print(f"Mockup saved to: {output_path}")
