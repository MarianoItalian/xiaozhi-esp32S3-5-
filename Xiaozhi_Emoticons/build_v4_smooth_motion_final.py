from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import cv2
import numpy as np
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
SOURCE = Path('/home/ubuntu/upload')
OUTPUT = ROOT / 'gif_v4_smooth_motion_final'
ARCHIVE = ROOT / 'Xiaozhi_Emoticons_v4_smooth_motion_final_160x120.zip'
SIZE = (160, 120)

EMOJIS = [
    ('01', 'Neutral', '093933', '114629', False),
    ('02', 'Happy', '114751', '115421', False),
    ('03', 'Laughing', '115022', '115333', False),
    ('04', 'Funny', '114944', '115421', False),
    ('05', 'Sad', '114441', '114606', False),
    ('06', 'Angry', '115229', '094013', False),
    ('07', 'Crying', '115113', '114841', False),
    ('08', 'Loving', '115722', '114629', False),
    ('09', 'Embarrassed', '114815', '094013', False),
    ('10', 'Surprised', '114920', '114606', False),
    ('11', 'Shocked', '114522', '114606', False),
    ('12', 'Thinking', '115750', '114629', False),
    ('13', 'Winking', '094043', '094013', True),
    ('14', 'Cool', '115040', '094013', False),
    ('15', 'Relaxed', '115656', '115143', False),
    ('16', 'Delicious', '115636', '115421', False),
    ('17', 'Kiss', '115524', '114841', False),
    ('18', 'Confident', '094108', '094013', False),
    ('19', 'Sleepy', '094013', '115143', False),
    ('20', 'Silly', '115005', '115333', False),
    ('21', 'Confused', '114714', '115256', False),
]


def source_file(code: str) -> Path:
    files = sorted(SOURCE.glob(f'Screenshot_20260716_{code}_TikTok(1)*.jpg'))
    if len(files) != 1:
        raise FileNotFoundError(f'Źródło {code}: {files}')
    return files[0]


def fit_image(code: str) -> Image.Image:
    image = Image.open(source_file(code)).convert('RGB')
    return ImageOps.fit(image, SIZE, Image.Resampling.LANCZOS, centering=(0.5, 0.16))


def make_eye_mask(wink: bool) -> Image.Image:
    # Stałe położenie działa dla serii ujęć z tego samego kadru. Zmiana dotyczy wyłącznie oczu.
    data = np.zeros((SIZE[1], SIZE[0]), dtype=np.uint8)
    positions = [(60, 48), (100, 48)]
    if wink:
        positions = [(60, 48)]
    for position in positions:
        cv2.ellipse(data, position, (20, 9), 0, 0, 360, 255, -1)
    return Image.fromarray(data).filter(ImageFilter.GaussianBlur(radius=2.0))


def blend_eyes(open_image: Image.Image, closed_image: Image.Image, mask: Image.Image, amount: float) -> Image.Image:
    alpha = mask.point(lambda value: round(value * amount))
    return Image.composite(closed_image, open_image, alpha)


def export_emoji(order: str, label: str, open_code: str, closed_code: str, wink: bool) -> Path:
    open_image = fit_image(open_code)
    closed_image = fit_image(closed_code)
    mask = make_eye_mask(wink)

    # Dziesięć widocznych faz tworzy jedną płynną sekwencję otwierania i zamykania.
    # 630 ms ruchu = 3 × 210 ms z pierwotnej wersji pakietu.
    amounts = [0.10, 0.25, 0.45, 0.70, 1.00, 0.70, 0.45, 0.25, 0.10, 0.00]
    movement_durations = [70, 60, 60, 60, 70, 60, 60, 60, 60, 70]
    frames = [open_image] + [blend_eyes(open_image, closed_image, mask, amount) for amount in amounts]
    durations = [850] + movement_durations
    if sum(movement_durations) != 630:
        raise ValueError('Czas ruchu musi wynosić 630 ms.')

    paletted = [frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for frame in frames]
    target = OUTPUT / f'{order}_{label}_blink.gif'
    paletted[0].save(
        target,
        save_all=True,
        append_images=paletted[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return target


OUTPUT.mkdir(parents=True, exist_ok=True)
files = []
for emoji in EMOJIS:
    exported = export_emoji(*emoji)
    files.append(exported)
    print(f'{exported.name}: 11 klatek, ruch 630 ms')

with ZipFile(ARCHIVE, 'w', ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, arcname=file.name)
print(f'Pakiet: {ARCHIVE}')
