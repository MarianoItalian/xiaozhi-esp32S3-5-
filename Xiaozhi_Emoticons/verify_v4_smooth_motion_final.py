from pathlib import Path
from PIL import Image

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
GIF_DIR = ROOT / 'gif_v4_smooth_motion_final'
REPORT = ROOT / 'raport_weryfikacji_wersja_4_final.md'
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
        if gif.n_frames != 11:
            raise ValueError(f'Nieprawidłowa liczba klatek {gif.n_frames}: {file.name}')
        durations = []
        for frame_number in range(gif.n_frames):
            gif.seek(frame_number)
            durations.append(gif.info.get('duration', 0))
        motion_time = sum(durations[1:])
        if motion_time != 630:
            raise ValueError(f'Nieprawidłowy czas ruchu {motion_time} ms: {file.name}')
        if gif.info.get('loop') != 0:
            raise ValueError(f'Brak pętli nieskończonej: {file.name}')
    rows.append((file.name, gif.n_frames, motion_time, sum(durations), file.stat().st_size))

lines = [
    '# Raport weryfikacji — Xiaozhi, wersja 4',
    '',
    'Zweryfikowano **21 GIF-ów**. Każdy plik ma wymiary **160 × 120 px**, zawiera 11 klatek i jest zapętlony bez końca. Widoczny ruch powiek trwa **630 ms**, a więc jest dokładnie trzy razy dłuższy niż 210 ms w pierwszej wersji.',
    '',
    '| Plik | Klatki | Czas ruchu oczu | Czas pętli | Rozmiar pliku |',
    '| --- | ---: | ---: | ---: | ---: |',
]
for name, frame_count, motion_time, total_time, byte_count in rows:
    lines.append(f'| `{name}` | {frame_count} | {motion_time} ms | {total_time} ms | {byte_count} B |')
lines.extend([
    '',
    'Wykorzystanie zdjęć: **21 różnych zdjęć głównych** oraz **7 dodatkowych ujęć** jako źródeł powiek w ruchu. Łącznie użyto wszystkich **28 dostarczonych portretów**.',
    '',
    '> Pauza z nieruchomą twarzą nie została wydłużona; zmieniono wyłącznie liczbę i czas klatek ruchu powiek.',
])
REPORT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Zweryfikowano: {len(rows)} GIF-ów')
print(f'Raport: {REPORT}')
