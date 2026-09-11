from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path('/home/ubuntu/upload')
OUTPUT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons/source_contact_sheet.jpg')
FILES = sorted(SOURCE.glob('Screenshot_20260716_*.jpg'))

thumb_w, thumb_h = 160, 220
label_h, gap, columns = 28, 14, 5
rows = (len(FILES) + columns - 1) // columns
canvas_w = columns * thumb_w + (columns + 1) * gap
canvas_h = rows * (thumb_h + label_h) + (rows + 1) * gap
canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')
draw = ImageDraw.Draw(canvas)
font = ImageFont.load_default()

for index, path in enumerate(FILES, 1):
    image = Image.open(path).convert('RGB')
    image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    x = gap + ((index - 1) % columns) * (thumb_w + gap) + (thumb_w - image.width) // 2
    y = gap + ((index - 1) // columns) * (thumb_h + label_h + gap)
    canvas.paste(image, (x, y))
    draw.text((gap + ((index - 1) % columns) * (thumb_w + gap), y + thumb_h + 6), f'{index:02d}: {path.stem[-6:]}', fill='black', font=font)

canvas.save(OUTPUT, quality=92)
print(f'Created {OUTPUT} from {len(FILES)} source images')
