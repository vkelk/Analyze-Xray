import numpy as np
import h5py
from keras.models import model_from_json
from keras.preprocessing import image

json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
print('here1')
loaded_model.load_weights("xray_class_weights.best.hdf5")
loaded_model.compile(optimizer='adam',
                     loss='binary_crossentropy',
                     metrics=['binary_accuracy','mae'])

img_width, img_height = 150, 150

print("Enter the image path:")
image_path = input()
img = image.load_img(image_path, target_size=(img_width, img_height))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0)

images = np.vstack([x])

p = loaded_model.predict(images, batch_size=32, verbose=True)

diseases = ['Atelectasis', 'Consolidation', 'Infiltration', 'Pneumothorax',
            'Edema', 'Emphysema', 'Fibrosis', 'Effusion', 'Pneumonia',
            'Pleural_Thickening', 'Cardiomegaly', 'Nodule', 'Mass']

for i, j in zip(diseases, p[0]):
    print('%s: %2.2f%%' % (i, j*100))
