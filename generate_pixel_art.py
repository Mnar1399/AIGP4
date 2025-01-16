from PIL import Image, ImageDraw, ImageFont
import random

def generate_pixel_art_from_idea(idea_summary, image_path="static/generated_pixel_art.png"):
    """Generate pixel art characters and map based on the idea summary."""
    
    width, height = 128, 128  # حجم الصورة
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # تقسيم الفكرة لاستخراج بعض الكلمات الرئيسية (كمثال بسيط)
    keywords = idea_summary.lower().split()
    if "player" in keywords or "character" in keywords:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([32, 32, 64, 64], fill=color)  # رسم مربع يمثل اللاعب

    if "map" in keywords or "world" in keywords:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.rectangle([64, 64, 96, 96], fill=color)  # رسم مربع يمثل جزء من الخريطة

    img.save(image_path)
    print(f"Image saved at {image_path}")