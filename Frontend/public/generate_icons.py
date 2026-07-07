import os
import sys
import subprocess

def install_and_import(package):
    try:
        import PIL
    except ImportError:
        print(f"Installing {package} for icon generation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
install_and_import('pillow')

from PIL import Image, ImageDraw

def create_pwa_icon(size):
    # Colors matching the Modern Industrial Slate Blue theme
    charcoal = (15, 23, 42)    # #0f172a
    steel_blue = (2, 132, 199) # #0284c7
    white = (255, 255, 255)
    
    # Create image with charcoal background
    img = Image.new('RGBA', (size, size), charcoal)
    draw = ImageDraw.Draw(img)
    
    # Draw a stylized hexagon (representing bolt/nut) in the center
    center = size // 2
    r_outer = size // 3
    
    import math
    points = []
    for i in range(6):
        angle = math.radians(i * 60)
        x = center + r_outer * math.cos(angle)
        y = center + r_outer * math.sin(angle)
        points.append((x, y))
        
    draw.polygon(points, fill=steel_blue)
    
    # Draw a inner charcoal circle to represent the bolt core
    r_inner = size // 6
    draw.ellipse([center - r_inner, center - r_inner, center + r_inner, center + r_inner], fill=charcoal)
    
    # Draw a smaller steel blue inner center circle
    r_dot = size // 15
    draw.ellipse([center - r_dot, center - r_dot, center + r_dot, center + r_dot], fill=white)
    
    filename = f"logo-{size}.png"
    img.save(filename, "PNG")
    print(f"Generated PWA compliant icon: {filename}")

if __name__ == "__main__":
    create_pwa_icon(192)
    create_pwa_icon(512)
