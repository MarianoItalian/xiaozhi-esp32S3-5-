from pathlib import Path
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
GIF_DIR = ROOT / 'gif'
ARCHIVE = ROOT / 'Xiaozhi_Emoticons_blink_160x120.zip'
REPORT = ROOT / 'raport_weryfikacji.md'

labels = [
    'Neutral', 'Happy', 'Laughing', 'Funny', 'Sad', 'Angry', 'Crying',
    'Loving', 'Embarrassed', 'Surprised', 'Shocked', 'Thinking', 'Winking',
    'Cool', 'Relaxed', 'Delicious', 'Kiss', 'Confident', 'Sleepy', 'Silly', 'Confused'
]
files = [GIF_DIR / f'{index:02d}_{label}_blink.gif' for index, label in enumerate(labels, 1)]

rows = []
for file in files:
    if not file.exists():
        raise FileNotFoundError(file)
    with Image.open(file) as image:
        frames = image.n_frames
        size = image.size
        loop = image.info.get('loop')
    if size != (160, 120):
        raise ValueError(f'Nieprawidłowy wymiar {size}: {file.name}')
    if frames < 3:
        raise ValueError(f'Zbyt mało klatek ({frames}): {file.name}')
    rows.append((file.name, size[0], size[1], frames, file.stat().st_size, loop))

with ZipFile(ARCHIVE, 'w', ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, arcname=file.name)

lines = [
    '# Raport weryfikacji — pakiet Xiaozhi',
    '',
    'Wszystkie pliki przeszły kontrolę: mają wymiary **160 × 120 px**, są animowanymi GIF-ami i mają co najmniej trzy klatki.',
    '',
    '| Plik | Szerokość | Wysokość | Klatki | Rozmiar (B) | Pętla |',
    '| --- | ---: | ---: | ---: | ---: | ---: |',
]
for name, width, height, frames, size_bytes, loop in rows:
    lines.append(f'| `{name}` | {width} | {height} | {frames} | {size_bytes} | {loop} |')
lines.extend([
    '',
    f'Archiwum: `{ARCHIVE.name}`',
    f'Łączna liczba emotikon: **{len(rows)}**.',
    '',
    '> Uwaga: panel Xiaozhi informuje, że użycie animowanych GIF-ów wymaga PSRAM w urządzeniu.',
])
REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Validated {len(rows)} GIF files')
print(f'Archive: {ARCHIVE}')
print(f'Report: {REPORT}')
