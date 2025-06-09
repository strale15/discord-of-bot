from PIL import Image, ImageDraw, ImageFont
import os

def generate_number_images(count, output_dir="resources/training/context_imgs", image_size=(512, 512), font_size=200):
    os.makedirs(output_dir, exist_ok=True)

    # Try to load a font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    for i in range(1, count + 1):
        img = Image.new("RGB", image_size, "black")
        draw = ImageDraw.Draw(img)

        text = str(i)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

        draw.text(position, text, font=font, fill="white")

        img.save(os.path.join(output_dir, f"ctx_{i:03}.png"))

    print(f"Generated {count} images in '{output_dir}'.")

# Example usage
generate_number_images(15)
print("done")
