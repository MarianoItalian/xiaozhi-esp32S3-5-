from pathlib import Path
from PIL import Image
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path('/mnt/82d64aad-e489-45ce-b354-a3f894654e32/Folder MANUS/Xiaozhi_Emoticons')
SOURCE_DIR = ROOT / 'gif'
OUTPUT_DIR = ROOT / 'gif_3x_longer'
ARCHIVE = ROOT / 'Xiaozhi_Emoticons_blink_3x_longer_160x120.zip'
LABELS = [
    'Neutral', 'Happy', 'Laughing', 'Funny', 'Sad', 'Angry', 'Crying',
    'Loving', 'Embarrassed', 'Surprised', 'Shocked', 'Thinking', 'Winking',
    'Cool', 'Relaxed', 'Delicious', 'Kiss', 'Confident', 'Sleepy', 'Silly', 'Confused'
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
created = []
for position, label in enumerate(LABELS, 1):
    name = f'{position:02d}_{label}_blink.gif'
    source = SOURCE_DIR / name
    target = OUTPUT_DIR / name
    with Image.open(source) as gif:
        frames = []
        source_durations = []
        for frame_no in range(gif.n_frames):
            gif.seek(frame_no)
            frames.append(gif.convert('RGB').copy())
            source_durations.append(gif.info.get('duration', 100))
        loop = gif.info.get('loop', 0)

    if len(frames) != 5 or frames[0].size != (160, 120):
        raise ValueError(f'Nieoczekiwany format pliku: {source.name}')

    # Pętla ma dokładnie 3× czas pierwotnego GIF-a. Sam moment mrugnięcia
    # zostaje szybki, a wydłużamy wyłącznie pauzę z otwartymi oczami.
    original_total = sum(source_durations)
    blink_total = sum(source_durations[1:4])
    long_hold = (3 * original_total - blink_total) // 2
    durations = [long_hold, *source_durations[1:4], long_hold]
    if sum(durations) != 3 * original_total:
        raise ValueError(f'Nie udało się zachować czasu 3×: {source.name}')

    palette_frames = [image.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for image in frames]
    palette_frames[0].save(
        target,
        save_all=True,
        append_images=palette_frames[1:],
        duration=durations,
        loop=loop,
        optimize=True,
        disposal=2,
    )
    created.append(target)
    print(f'{target.name}: {sum(durations)} ms')

with ZipFile(ARCHIVE, 'w', ZIP_DEFLATED) as archive:
    for target in created:
        archive.write(target, target.name)

print(f'Pakiet: {ARCHIVE}')
