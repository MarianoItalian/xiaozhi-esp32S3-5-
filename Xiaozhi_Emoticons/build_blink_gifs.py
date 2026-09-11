from pathlib import Path
from PIL import Image, ImageOps, ImageChops
import numpy as np
import cv2

SOURCE = Path('/home/ubuntu/upload')
OUT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons/gif')
SIZE = (160, 120)

# Każdy wpis: nr, nazwa kategorii z panelu Xiaozhi, kadr z otwartymi oczami, najbliższy kadr z zamkniętymi oczami.
EMOJIS = [
    ('01', 'Neutral', 'Screenshot_20260716_115656_TikTok(1)(1).jpg', 'Screenshot_20260716_114629_TikTok(1).jpg'),
    ('02', 'Happy', 'Screenshot_20260716_114751_TikTok(1).jpg', 'Screenshot_20260716_115421_TikTok(1).jpg'),
    ('03', 'Laughing', 'Screenshot_20260716_115022_TikTok(1).jpg', 'Screenshot_20260716_115421_TikTok(1).jpg'),
    ('04', 'Funny', 'Screenshot_20260716_115022_TikTok(1).jpg', 'Screenshot_20260716_115333_TikTok(1).jpg'),
    ('05', 'Sad', 'Screenshot_20260716_114441_TikTok(1).jpg', 'Screenshot_20260716_114606_TikTok(1).jpg'),
    ('06', 'Angry', 'Screenshot_20260716_114441_TikTok(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('07', 'Crying', 'Screenshot_20260716_114920_TikTok(1).jpg', 'Screenshot_20260716_114841_TikTok(1).jpg'),
    ('08', 'Loving', 'Screenshot_20260716_115722_TikTok(1).jpg', 'Screenshot_20260716_114629_TikTok(1).jpg'),
    ('09', 'Embarrassed', 'Screenshot_20260716_114815_TikTok(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('10', 'Surprised', 'Screenshot_20260716_114920_TikTok(1).jpg', 'Screenshot_20260716_114606_TikTok(1).jpg'),
    ('11', 'Shocked', 'Screenshot_20260716_114522_TikTok(1).jpg', 'Screenshot_20260716_114606_TikTok(1).jpg'),
    ('12', 'Thinking', 'Screenshot_20260716_115750_TikTok(1).jpg', 'Screenshot_20260716_114629_TikTok(1).jpg'),
    ('13', 'Winking', 'Screenshot_20260716_094043_TikTok(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('14', 'Cool', 'Screenshot_20260716_115040_TikTok(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('15', 'Relaxed', 'Screenshot_20260716_115656_TikTok(1)(1).jpg', 'Screenshot_20260716_114629_TikTok(1).jpg'),
    ('16', 'Delicious', 'Screenshot_20260716_115022_TikTok(1).jpg', 'Screenshot_20260716_115421_TikTok(1).jpg'),
    ('17', 'Kiss', 'Screenshot_20260716_115524_TikTok(1).jpg', 'Screenshot_20260716_114841_TikTok(1).jpg'),
    ('18', 'Confident', 'Screenshot_20260716_094108_TikTok(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('19', 'Sleepy', 'Screenshot_20260716_115656_TikTok(1)(1).jpg', 'Screenshot_20260716_094013_TikTok(1).jpg'),
    ('20', 'Silly', 'Screenshot_20260716_115005_TikTok(1).jpg', 'Screenshot_20260716_114606_TikTok(1).jpg'),
    ('21', 'Confused', 'Screenshot_20260716_114714_TikTok(1).jpg', 'Screenshot_20260716_114629_TikTok(1).jpg'),
]


def fit_face(path: Path) -> Image.Image:
    image = Image.open(path).convert('RGB')
    # Wysoki portret dopasowujemy do limitu 160×120, zostawiając górną część kadru z twarzą.
    return ImageOps.fit(image, SIZE, Image.Resampling.LANCZOS, centering=(0.5, 0.16))


def align_closed(open_frame: Image.Image, closed_frame: Image.Image) -> Image.Image:
    """Dopasowuje jedynie przesunięcie klatki mrugnięcia względem twarzy."""
    open_array = np.array(open_frame)
    closed_array = np.array(closed_frame)
    template = cv2.cvtColor(open_array, cv2.COLOR_RGB2GRAY)
    moving = cv2.cvtColor(closed_array, cv2.COLOR_RGB2GRAY)
    mask = np.zeros(SIZE[::-1], dtype=np.uint8)
    cv2.ellipse(mask, (80, 58), (56, 52), 0, 0, 360, 255, -1)
    warp = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 1e-5)
    try:
        _, warp = cv2.findTransformECC(template, moving, warp, cv2.MOTION_TRANSLATION, criteria, mask, 1)
        aligned = cv2.warpAffine(closed_array, warp, SIZE, flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        return Image.fromarray(aligned)
    except cv2.error:
        return closed_frame


def make_gif(order: str, label: str, open_name: str, closed_name: str) -> None:
    open_frame = fit_face(SOURCE / open_name)
    closed_frame = align_closed(open_frame, fit_face(SOURCE / closed_name))
    mid_frame = Image.blend(open_frame, closed_frame, 0.5)
    # Krótkie zamknięcie powiek; reszta pętli zatrzymuje wybrany wyraz twarzy.
    frames = [open_frame, mid_frame, closed_frame, mid_frame, open_frame]
    durations = [850, 55, 115, 55, 850]
    indexed = [frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for frame in frames]
    output = OUT / f'{order}_{label}_blink.gif'
    indexed[0].save(output, save_all=True, append_images=indexed[1:], duration=durations, loop=0, optimize=True, disposal=2)
    print(output.name)


OUT.mkdir(parents=True, exist_ok=True)
for item in EMOJIS:
    make_gif(*item)
