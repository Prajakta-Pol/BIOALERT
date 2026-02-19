#import cv2
#import mediapipe as mp
#import numpy as np

#mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
 #   static_image_mode=True,
  #  max_num_faces=1,
   # refine_landmarks=True
#)

#def extract_face_vector(image_path):
 #   image = cv2.imread(image_path)
  #  if image is None:
   #     return None

    #rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #results = mp_face_mesh.process(rgb)

    #if not results.multi_face_landmarks:
     #   return None

    #landmarks = results.multi_face_landmarks[0]

    #vector = []
    #for lm in landmarks.landmark:
     #   vector.extend([lm.x, lm.y, lm.z])

    #return np.array(vector)

#def compare_faces(vec1, vec2):
 #   if vec1 is None or vec2 is None:
  #      return 0

   # distance = np.linalg.norm(vec1 - vec2)
    #similarity = max(0, 100 - distance * 100)

    #return similarity
