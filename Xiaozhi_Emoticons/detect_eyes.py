from pathlib import Path
import cv2

source = Path('/home/ubuntu/upload')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

for path in sorted(source.glob('Screenshot_20260716_*.jpg')):
    image = cv2.imread(str(path))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(80, 80))
    details = []
    for x, y, w, h in faces:
        roi = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi, scaleFactor=1.08, minNeighbors=4, minSize=(20, 12), maxSize=(w // 2, h // 2))
        details.append(f'face=({x},{y},{w},{h}) eyes={[(int(ex+x),int(ey+y),int(ew),int(eh)) for ex, ey, ew, eh in eyes]}')
    print(f'{path.name}: ' + '; '.join(details))
