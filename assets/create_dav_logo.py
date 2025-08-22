#!/usr/bin/env python3
"""
Professional DAV Logo Generator
Creates modern, professional logos for the DAV programming language
Inspired by Django's clean aesthetic but with unique DAV identity
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

def create_gradient(width, height, color1, color2, direction='vertical'):
    """Create a gradient between two colors"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:  # horizontal
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    return img

def get_font(size, bold=False):
    """Get the best available font"""
    fonts_to_try = [
        # Modern fonts
        "/System/Library/Fonts/SF-Pro-Display-Bold.otf" if bold else "/System/Library/Fonts/SF-Pro-Display-Regular.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "arial.ttf",
        "Arial.ttf",
        # Fallback
        None
    ]
    
    for font_path in fonts_to_try:
        try:
            if font_path:
                return ImageFont.truetype(font_path, size)
            else:
                return ImageFont.load_default()
        except:
            continue
    
    return ImageFont.load_default()

def create_main_logo():
    """Create the main DAV logo with modern professional styling"""
    width, height = 500, 200
    
    # Professional color palette (inspired by modern tech branding)
    colors = {
        'primary': (41, 128, 185),      # Professional blue
        'secondary': (52, 73, 94),      # Dark slate
        'accent': (46, 204, 113),       # Green accent
        'dark': (44, 62, 80),           # Almost black
        'white': (255, 255, 255),       # Pure white
        'light_gray': (236, 240, 241),  # Light gray
        'gradient_start': (52, 152, 219), # Light blue
        'gradient_end': (41, 128, 185)    # Darker blue
    }
    
    # Create background with subtle gradient
    img = create_gradient(width, height, colors['gradient_start'], colors['gradient_end'], 'diagonal')
    
    # Create a semi-transparent overlay for depth
    overlay = Image.new('RGBA', (width, height), (255, 255, 255, 30))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # Get fonts
    font_logo = get_font(72, bold=True)
    font_subtitle = get_font(16)
    font_tagline = get_font(14)
    
    # Draw geometric accent element (inspired by modern logos)
    accent_x, accent_y = 30, 60
    accent_size = 80
    
    # Create a modern geometric shape (hexagon)
    points = []
    center_x, center_y = accent_x + accent_size//2, accent_y + accent_size//2
    for i in range(6):
        angle = math.radians(i * 60 - 30)  # Start from top
        x = center_x + (accent_size//3) * math.cos(angle)
        y = center_y + (accent_size//3) * math.sin(angle)
        points.append((x, y))
    
    # Draw hexagon with gradient effect
    draw.polygon(points, fill=colors['accent'], outline=colors['white'], width=3)
    
    # Add inner design
    inner_points = []
    for i in range(6):
        angle = math.radians(i * 60 - 30)
        x = center_x + (accent_size//6) * math.cos(angle)
        y = center_y + (accent_size//6) * math.sin(angle)
        inner_points.append((x, y))
    draw.polygon(inner_points, fill=colors['white'])
    
    # Add "D" in the center
    font_d = get_font(24, bold=True)
    d_bbox = draw.textbbox((0, 0), "D", font=font_d)
    d_width = d_bbox[2] - d_bbox[0]
    d_height = d_bbox[3] - d_bbox[1]
    draw.text((center_x - d_width//2, center_y - d_height//2), "D", 
              font=font_d, fill=colors['primary'])
    
    # Main DAV text
    text_x = 150
    text_y = 50
    
    # DAV with shadow effect
    shadow_offset = 2
    draw.text((text_x + shadow_offset, text_y + shadow_offset), "DAV", 
              font=font_logo, fill=colors['dark'])
    draw.text((text_x, text_y), "DAV", font=font_logo, fill=colors['white'])
    
    # Subtitle and tagline
    draw.text((text_x, text_y + 85), "Programming Language", 
              font=font_subtitle, fill=colors['white'])
    draw.text((text_x, text_y + 105), "Code in French • Code in English", 
              font=font_tagline, fill=colors['light_gray'])
    
    # Modern accent line
    line_y = text_y + 130
    draw.line([(text_x, line_y), (text_x + 200, line_y)], 
              fill=colors['accent'], width=3)
    
    # Subtle border
    draw.rectangle([0, 0, width-1, height-1], outline=colors['white'], width=2)
    
    return img

def create_horizontal_logo():
    """Create a horizontal logo for headers and banners"""
    width, height = 800, 150
    
    colors = {
        'primary': (41, 128, 185),
        'secondary': (52, 73, 94),
        'accent': (46, 204, 113),
        'white': (255, 255, 255),
        'light_gray': (236, 240, 241)
    }
    
    # Clean white background with subtle shadow
    img = Image.new('RGB', (width, height), colors['white'])
    draw = ImageDraw.Draw(img)
    
    # Geometric logo mark
    logo_x, logo_y = 30, 35
    logo_size = 80
    
    # Modern square with rounded corners effect
    draw.rounded_rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                          radius=15, fill=colors['primary'], outline=colors['secondary'], width=2)
    
    # Inner design
    inner_margin = 20
    draw.rounded_rectangle([logo_x + inner_margin, logo_y + inner_margin, 
                           logo_x + logo_size - inner_margin, logo_y + logo_size - inner_margin], 
                          radius=8, fill=colors['accent'])
    
    # DAV text inside
    font_inner = get_font(20, bold=True)
    inner_text = "DAV"
    bbox = draw.textbbox((0, 0), inner_text, font=font_inner)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((logo_x + logo_size//2 - text_width//2, 
               logo_y + logo_size//2 - text_height//2), 
              inner_text, font=font_inner, fill=colors['white'])
    
    # Main text
    text_x = logo_x + logo_size + 30
    font_main = get_font(48, bold=True)
    font_sub = get_font(18)
    
    draw.text((text_x, 30), "DAV", font=font_main, fill=colors['primary'])
    draw.text((text_x + 150, 45), "Programming Language", font=font_sub, fill=colors['secondary'])
    draw.text((text_x, 85), "Français • English • Professional", font=font_sub, fill=colors['secondary'])
    
    return img

def create_square_logo():
    """Create a square logo for social media and app icons"""
    size = 512
    
    colors = {
        'primary': (41, 128, 185),
        'secondary': (52, 73, 94),
        'accent': (46, 204, 113),
        'white': (255, 255, 255),
        'gradient_start': (52, 152, 219),
        'gradient_end': (41, 128, 185)
    }
    
    # Gradient background
    img = create_gradient(size, size, colors['gradient_start'], colors['gradient_end'])
    draw = ImageDraw.Draw(img)
    
    # Modern circular design
    center = size // 2
    outer_radius = size // 3
    inner_radius = size // 5
    
    # Outer circle
    draw.ellipse([center - outer_radius, center - outer_radius, 
                  center + outer_radius, center + outer_radius], 
                 fill=colors['white'], outline=colors['secondary'], width=8)
    
    # Inner circle
    draw.ellipse([center - inner_radius, center - inner_radius, 
                  center + inner_radius, center + inner_radius], 
                 fill=colors['accent'])
    
    # DAV text
    font_size = 64
    font = get_font(font_size, bold=True)
    text = "DAV"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    draw.text((center - text_width//2, center - text_height//2), 
              text, font=font, fill=colors['white'])
    
    # Add subtle ring effect
    ring_radius = outer_radius + 20
    draw.arc([center - ring_radius, center - ring_radius, 
              center + ring_radius, center + ring_radius], 
             0, 360, fill=colors['white'], width=4)
    
    return img

def create_favicon():
    """Create favicon in multiple sizes"""
    base_size = 64
    
    colors = {
        'primary': (41, 128, 185),
        'accent': (46, 204, 113),
        'white': (255, 255, 255)
    }
    
    img = Image.new('RGB', (base_size, base_size), colors['primary'])
    draw = ImageDraw.Draw(img)
    
    # Simple but recognizable design
    margin = 8
    draw.rounded_rectangle([margin, margin, base_size - margin, base_size - margin], 
                          radius=6, fill=colors['accent'])
    
    # Large D
    font = get_font(32, bold=True)
    text = "D"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    draw.text((base_size//2 - text_width//2, base_size//2 - text_height//2), 
              text, font=font, fill=colors['white'])
    
    return img

def create_wordmark():
    """Create a text-only wordmark logo"""
    width, height = 400, 100
    
    colors = {
        'primary': (41, 128, 185),
        'secondary': (52, 73, 94),
        'white': (255, 255, 255)
    }
    
    img = Image.new('RGB', (width, height), colors['white'])
    draw = ImageDraw.Draw(img)
    
    # Clean typography-focused design
    font_main = get_font(56, bold=True)
    font_sub = get_font(14)
    
    # DAV with professional styling
    main_text = "DAV"
    bbox = draw.textbbox((0, 0), main_text, font=font_main)
    main_width = bbox[2] - bbox[0]
    
    x_pos = (width - main_width) // 2
    y_pos = 10
    
    # Draw with subtle shadow
    draw.text((x_pos + 1, y_pos + 1), main_text, font=font_main, fill=colors['secondary'])
    draw.text((x_pos, y_pos), main_text, font=font_main, fill=colors['primary'])
    
    # Subtitle
    sub_text = "PROGRAMMING LANGUAGE"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_x = (width - sub_width) // 2
    
    draw.text((sub_x, y_pos + 65), sub_text, font=font_sub, fill=colors['secondary'])
    
    return img

def main():
    """Generate all logo variants"""
    output_dir = "dav_professional_logos"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎨 Creating Professional DAV Logo Suite...")
    print("   Inspired by modern tech branding (Django-style but unique)")
    
    # Main logo
    print("📐 Creating main logo...")
    main_logo = create_main_logo()
    main_logo.save(f"{output_dir}/dav_main_logo.png")
    main_logo.save(f"{output_dir}/dav_main_logo.jpg", "JPEG", quality=95)
    
    # Horizontal logo
    print("📏 Creating horizontal logo...")
    horizontal = create_horizontal_logo()
    horizontal.save(f"{output_dir}/dav_horizontal.png")
    horizontal.save(f"{output_dir}/dav_horizontal.jpg", "JPEG", quality=95)
    
    # Square logo
    print("⏹️  Creating square logo...")
    square = create_square_logo()
    square.save(f"{output_dir}/dav_square.png")
    
    # Different square sizes
    for size in [256, 128, 64, 32]:
        resized = square.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f"{output_dir}/dav_square_{size}x{size}.png")
    
    # Favicon
    print("🔖 Creating favicon...")
    favicon = create_favicon()
    favicon.save(f"{output_dir}/favicon.png")
    favicon.save(f"{output_dir}/favicon.ico")
    
    # Wordmark
    print("✏️  Creating wordmark...")
    wordmark = create_wordmark()
    wordmark.save(f"{output_dir}/dav_wordmark.png")
    
    # Web-optimized versions
    print("🌐 Creating web-optimized versions...")
    web_sizes = [(300, 120), (400, 160), (600, 240)]
    for w, h in web_sizes:
        web_logo = main_logo.resize((w, h), Image.Resampling.LANCZOS)
        web_logo.save(f"{output_dir}/dav_web_{w}x{h}.png", optimize=True)
    
    # Social media sizes
    print("📱 Creating social media versions...")
    social_square = square.resize((1024, 1024), Image.Resampling.LANCZOS)
    social_square.save(f"{output_dir}/dav_social_square.png")
    
    banner = horizontal.resize((1200, 225), Image.Resampling.LANCZOS)
    banner.save(f"{output_dir}/dav_social_banner.png")
    
    print(f"\n🎉 Professional DAV Logo Suite Complete!")
    print(f"📁 All files saved in: {output_dir}/")
    print("\n📋 Logo Variants Created:")
    print("   • Main Logo (500x200) - Primary brand logo")
    print("   • Horizontal Logo (800x150) - For headers/navigation")
    print("   • Square Logo (512x512) - App icons, social media")
    print("   • Wordmark (400x100) - Text-only version")
    print("   • Favicon (64x64) - Website icon")
    print("   • Web sizes (300x120, 400x160, 600x240)")
    print("   • Social media optimized versions")
    print("\n🎨 Design Features:")
    print("   • Modern, professional aesthetic")
    print("   • Consistent color palette")
    print("   • Scalable vector-style design")
    print("   • Multiple format outputs (PNG, JPG, ICO)")
    print("   • Django-inspired but uniquely DAV")

if __name__ == "__main__":
    main()