import mediapipe as mp

print('mediapipe:', mp.__version__)
print('has_solutions:', hasattr(mp, 'solutions'))
if hasattr(mp, 'solutions'):
    print('has_face_mesh:', hasattr(mp.solutions, 'face_mesh'))
