import os
import numpy as np
from keras.models import model_from_json
from keras.preprocessing import image

from app.config import MODEL_DIR

json_file = open(os.path.join(MODEL_DIR, 'model.json'), 'r')
loaded_model_json = json_file.read()
json_file.close()


def analyze_image(image_path):
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(os.path.join(
        MODEL_DIR,
        'xray_class_weights.best.hdf5'
        ))
    loaded_model.compile(optimizer='adam',
                         loss='binary_crossentropy',
                         metrics=['binary_accuracy', 'mae'])
    img_width, img_height = 150, 150
    img = image.load_img(image_path, target_size=(img_width, img_height))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)

    images = np.vstack([x])

    p = loaded_model.predict(images, batch_size=32, verbose=True)
    from keras import backend as K
    K.clear_session()

    diseases = ['Atelectasis', 'Consolidation', 'Infiltration', 'Pneumothorax',
                'Edema', 'Emphysema', 'Fibrosis', 'Effusion', 'Pneumonia',
                'Pleural_Thickening', 'Cardiomegaly', 'Nodule', 'Mass']

    result = {}
    for i, j in zip(diseases, p[0]):
        # print('%s: %2.2f%%' % (i, j*100))
        result[i] = j*100

    return result
