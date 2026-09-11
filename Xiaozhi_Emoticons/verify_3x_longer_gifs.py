from pathlib import Path
from PIL import Image

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
DIRECTORY = ROOT / 'gif_3x_longer'
REPORT = ROOT / 'raport_weryfikacji_3x_longer.md'
LABELS = [
    'Neutral', 'Happy', 'Laughing', 'Funny', 'Sad', 'Angry', 'Crying',
    'Loving', 'Embarrassed', 'Surprised', 'Shocked', 'Thinking', 'Winking',
    'Cool', 'Relaxed', 'Delicious', 'Kiss', 'Confident', 'Sleepy', 'Silly', 'Confused'
]

rows = []
for position, label in enumerate(LABELS, 1):
    file = DIRECTORY / f'{position:02d}_{label}_blink.gif'
    with Image.open(file) as gif:
        if gif.size != (160, 120):
            raise ValueError(f'Nieprawidłowy rozmiar {gif.size}: {file.name}')
        durations = []
        for frame_number in range(gif.n_frames):
            gif.seek(frame_number)
            durations.append(gif.info.get('duration', 0))
        if gif.n_frames != 5:
            raise ValueError(f'Nieprawidłowa liczba klatek {gif.n_frames}: {file.name}')
        if sum(durations) != 5730:
            raise ValueError(f'Nieprawidłowy czas {sum(durations)} ms: {file.name}')
        if gif.info.get('loop') != 0:
            raise ValueError(f'Brak pętli nieskończonej: {file.name}')
    rows.append((file.name, gif.size[0], gif.size[1], len(durations), sum(durations), file.stat().st_size))

lines = [
    '# Raport weryfikacji — Xiaozhi, pętla 3× dłuższa',
    '',
    'Zweryfikowano 21 animowanych GIF-ów. Każdy ma wymiary **160 × 120 px**, pięć klatek, pętlę nieskończoną i czas jednej pętli **5 730 ms**. Jest to dokładnie trzy razy więcej niż w poprzedniej wersji (1 910 ms).',
    '',
    '| Plik | Wymiary | Klatki | Czas pętli | Rozmiar pliku |',
    '| --- | --- | ---: | ---: | ---: |',
]
for name, width, height, frames, duration, byte_size in rows:
    lines.append(f'| `{name}` | {width} × {height} | {frames} | {duration} ms | {byte_size} B |')
lines.extend(['', '> Moment mrugnięcia zachowuje szybkie przejście; wydłużono wyłącznie pauzę z otwartymi oczami.', ''])
REPORT.write_text('\n'.join(lines), encoding='utf-8')
print(f'Zweryfikowano: {len(rows)} plików')
print(f'Raport: {REPORT}')
