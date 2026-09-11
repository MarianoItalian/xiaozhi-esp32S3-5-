from pathlib import Path
from PIL import Image

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
GIF_DIR = ROOT / 'gif_v3_smooth_motion'
REPORT = ROOT / 'raport_weryfikacji_wersja_3_smooth_motion.md'
LABELS = [
    'Neutral', 'Happy', 'Laughing', 'Funny', 'Sad', 'Angry', 'Crying',
    'Loving', 'Embarrassed', 'Surprised', 'Shocked', 'Thinking', 'Winking',
    'Cool', 'Relaxed', 'Delicious', 'Kiss', 'Confident', 'Sleepy', 'Silly', 'Confused'
]

rows = []
for position, label in enumerate(LABELS, 1):
    file = GIF_DIR / f'{position:02d}_{label}_blink.gif'
    if not file.is_file():
        raise FileNotFoundError(file)
    with Image.open(file) as gif:
        if gif.size != (160, 120):
            raise ValueError(f'Nieprawidłowy wymiar {gif.size}: {file.name}')
        if gif.n_frames != 12:
            raise ValueError(f'Nieprawidłowa liczba klatek {gif.n_frames}: {file.name}')
        durations = []
        for frame in range(gif.n_frames):
            gif.seek(frame)
            durations.append(gif.info.get('duration', 0))
        if sum(durations[1:-1]) != 620:
            raise ValueError(f'Nieprawidłowy czas ruchu {sum(durations[1:-1])} ms: {file.name}')
        if gif.info.get('loop') != 0:
            raise ValueError(f'Brak pętli nieskończonej: {file.name}')
    rows.append((file.name, len(durations), sum(durations[1:-1]), sum(durations), file.stat().st_size))

lines = [
    '# Raport weryfikacji — emotikony Xiaozhi, wersja 3',
    '',
    'Zweryfikowano **21 GIF-ów**. Każdy ma wymiary **160 × 120 px**, 12 klatek i pętlę nieskończoną. Faza widocznego ruchu powiek trwa **620 ms**, czyli około trzy razy dłużej niż 210 ms w pierwotnej wersji.',
    '',
    '| Plik | Klatki | Czas ruchu powiek | Czas całej pętli | Rozmiar pliku |',
    '| --- | ---: | ---: | ---: | ---: |',
]
for name, frames, motion, total, bytes_count in rows:
    lines.append(f'| `{name}` | {frames} | {motion} ms | {total} ms | {bytes_count} B |')
lines.extend(['', '> W tej wersji nie wydłużano pauzy pomiędzy ruchami. Różnica względem pierwszego pakietu wynika z większej liczby klatek przejściowych powiek.', ''])
REPORT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Zweryfikowano {len(rows)} GIF-ów.')
print(f'Raport: {REPORT}')
