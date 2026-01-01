from PIL import Image, ImageDraw
import sys

def create_icon(size, filename):
    """Створює іконку Ci з градієнтом"""
    img = Image.new('RGB', (size, size), '#0b0f14')
    draw = ImageDraw.Draw(img)
    
    # Градієнтна C-подібна форма (спрощена версія)
    center = size // 2
    radius_outer = int(size * 0.4)
    radius_inner = int(size * 0.28)
    
    # Малюємо голубе коло (зовнішнє)
    draw.ellipse(
        [center - radius_outer, center - radius_outer,
         center + radius_outer, center + radius_outer],
        fill='#4fc3f7'
    )
    
    # Вирізаємо внутрішнє коло (створюємо C-форму)
    draw.ellipse(
        [center - radius_inner, center - radius_inner,
         center + radius_inner, center + radius_inner],
        fill='#0b0f14'
    )
    
    # Вирізаємо правий сектор (створюємо відкриття C)
    draw.rectangle(
        [center, center - radius_outer - 10,
         center + radius_outer + 10, center + radius_outer + 10],
        fill='#0b0f14'
    )
    
    # Додаємо жовту крапку (акцент)
    dot_radius = int(size * 0.08)
    dot_x = center + int(radius_outer * 0.7)
    dot_y = center - int(radius_outer * 0.5)
    draw.ellipse(
        [dot_x - dot_radius, dot_y - dot_radius,
         dot_x + dot_radius, dot_y + dot_radius],
        fill='#ffd54f'
    )
    
    img.save(filename)
    print(f"✅ Створено: {filename} ({size}x{size})")

# Генерація іконок
try:
    create_icon(192, 'ui/icons/icon-192.png')
    create_icon(512, 'ui/icons/icon-512.png')
    print("✅ Іконки згенеровано")
except Exception as e:
    print(f"❌ Помилка: {e}")
    sys.exit(1)
