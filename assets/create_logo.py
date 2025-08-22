#!/usr/bin/env python3
"""
Script to create a logo for .dav files
This creates a simple but professional logo in various formats
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_dav_logo():
    """Create DAV logo in multiple formats and sizes"""
    
    # Create directory if it doesn't exist
    os.makedirs('logos', exist_ok=True)
    
    # Colors
    bg_color = (41, 98, 255)      # Modern blue
    text_color = (255, 255, 255)   # White
    accent_color = (255, 215, 0)   # Gold
    
    sizes = [
        (16, 16),    # Small icon
        (32, 32),    # Standard icon
        (48, 48),    # Medium icon
        (64, 64),    # Large icon
        (128, 128),  # High resolution
        (256, 256),  # Very high resolution
        (512, 512),  # Ultra high resolution
    ]
    
    for width, height in sizes:
        # Create image
        img = Image.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on image size
        font_size = max(8, width // 6)
        
        try:
            # Try to use a nice font
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Draw "DAV" text
        text = "DAV"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 2  # Slightly higher
        
        # Draw text with shadow effect
        if width >= 32:
            # Shadow
            draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 128))
        
        # Main text
        draw.text((x, y), text, font=font, fill=text_color)
        
        # Add decorative element for larger sizes
        if width >= 64:
            # Draw a small accent line under the text
            line_y = y + text_height + 2
            line_start = x + text_width // 4
            line_end = x + 3 * text_width // 4
            draw.line([(line_start, line_y), (line_end, line_y)], 
                     fill=accent_color, width=max(1, width // 64))
        
        # Round corners for modern look (for larger sizes)
        if width >= 48:
            img = add_rounded_corners(img, width // 8)
        
        # Save in different formats
        img.save(f'logos/dav_logo_{width}x{height}.png')
        
        # Create ICO file for the largest size (for Windows file association)
        if width == 256:
            img.save('logos/dav_logo.ico', format='ICO', sizes=[(256, 256)])
    
    print("✅ Logos created successfully in 'logos/' directory!")
    print("Files created:")
    for width, height in sizes:
        print(f"  - dav_logo_{width}x{height}.png")
    print("  - dav_logo.ico")
    
def add_rounded_corners(img, radius):
    """Add rounded corners to an image"""
    # Create a mask for rounded corners
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius, fill=255)
    
    # Apply the mask
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result.paste(img, mask=mask)
    return result

if __name__ == "__main__":
    create_dav_logo()
