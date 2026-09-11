from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import cv2
import numpy as np
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
SOURCE = Path('/home/ubuntu/upload')
OUTPUT = ROOT / 'gif_v3_smooth_motion'
ARCHIVE = ROOT / 'Xiaozhi_Emoticons_v3_smooth_motion_160x120.zip'
SIZE = (160, 120)

# label, zdjęcie główne, zdjęcie z powiekami domkniętymi, mrugnięcie jednym okiem
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
    choices = sorted(SOURCE.glob(f'Screenshot_20260716_{code}_TikTok(1)*.jpg'))
    if len(choices) != 1:
        raise FileNotFoundError(f'Nie znaleziono jednoznacznie źródła {code}: {choices}')
    return choices[0]


def fit(path: Path) -> Image.Image:
    img = Image.open(path).convert('RGB')
    return ImageOps.fit(img, SIZE, Image.Resampling.LANCZOS, centering=(0.5, 0.16))


def detect_face(image: Image.Image) -> tuple[int, int, int, int]:
    # Wszystkie obrazy pochodzą z jednego pionowego kadru i po dopasowaniu do 160×120
    # twarz mieści się w tym samym bezpiecznym obszarze. Stały region wyklucza błędy
    # automatycznego wykrywania przy tak małym rozmiarze docelowym.
    return 22, 0, 116, 120


def align_to_open(open_img: Image.Image, closed_img: Image.Image) -> Image.Image:
    # Ujęcia mają wspólne źródło i kadr. Późniejsza maska ograniczy zmianę tylko do oczu.
    return closed_img


def eye_mask(open_img: Image.Image, wink: bool) -> Image.Image:
    x, y, w, h = detect_face(open_img)
    mask = Image.new('L', SIZE, 0)
    # Maska obejmuje wyłącznie powiekę i minimalny fragment skóry wokół oka.
    canvas = np.array(mask)
    centers = [(int(x + 0.33 * w), int(y + 0.40 * h)), (int(x + 0.67 * w), int(y + 0.40 * h))]
    axes = (max(10, int(0.17 * w)), max(5, int(0.075 * h)))
    selected = centers[:1] if wink else centers
    for center in selected:
        cv2.ellipse(canvas, center, axes, 0, 0, 360, 255, -1)
    return Image.fromarray(canvas).filter(ImageFilter.GaussianBlur(radius=2.0))


def composite(open_img: Image.Image, closed_img: Image.Image, mask: Image.Image, amount: float) -> Image.Image:
    alpha = mask.point(lambda v: int(v * amount))
    return Image.composite(closed_img, open_img, alpha)


def export_one(order: str, label: str, open_code: str, closed_code: str, wink: bool) -> None:
    open_img = fit(source_file(open_code))
    closed_img = align_to_open(open_img, fit(source_file(closed_code)))
    mask = eye_mask(open_img, wink)

    # Ruch: 10 faz, 630 ms łącznie — trzy razy dłużej niż w wersji pierwszej (210 ms).
    motion_amounts = [0.10, 0.25, 0.45, 0.70, 1.00, 0.70, 0.45, 0.25, 0.10, 0.00]
    motion_times = [70, 60, 60, 60, 60, 60, 60, 60, 60, 70]
    movement = [composite(open_img, closed_img, mask, amount) for amount in motion_amounts]
    frames = [open_img] + movement + [open_img]
    durations = [850] + motion_times + [850]

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
    print(f'{target.name}: {len(frames)} klatek, ruch {sum(motion_times)} ms')


OUTPUT.mkdir(parents=True, exist_ok=True)
for emoji in EMOJIS:
    export_one(*emoji)

with ZipFile(ARCHIVE, 'w', ZIP_DEFLATED) as archive:
    for order, label, *_ in EMOJIS:
        file = OUTPUT / f'{order}_{label}_blink.gif'
        archive.write(file, arcname=file.name)
print(f'Pakiet: {ARCHIVE}')
