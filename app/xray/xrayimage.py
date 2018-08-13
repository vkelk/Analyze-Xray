import os
import numpy as np
import pandas as pd
from keras.models import model_from_json
from keras.preprocessing.image import ImageDataGenerator

from app.config import MODEL_DIR, WEIGHTS_FILE

json_file = open(os.path.join(MODEL_DIR, 'model.json'), 'r')
loaded_model_json = json_file.read()
json_file.close()
IMG_DIR = os.path.join(MODEL_DIR, 'imgs')


def flow_df(idg, df, path, y, **kwargs):
    dfg = idg.flow_from_directory(IMG_DIR, class_mode='sparse', **kwargs)
    dfg.filenames = df[path].values
    dfg.classes = np.stack(df[y].values)
    dfg.samples = df.shape[0]
    dfg.n = df.shape[0]
    dfg._set_index_array()
    dfg.directory = ''
    return dfg


def analyze_image(image_path):
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights(WEIGHTS_FILE)
    loaded_model.compile(optimizer='adam',
                         loss='binary_crossentropy',
                         metrics=['binary_accuracy', 'mae'])
    IMG_SIZE = (150, 150)

    diseases = [
        'No Finding', 'Atelectasis', 'Consolidation', 'Infiltration', 'Pneumothorax',
        'Edema', 'Emphysema', 'Fibrosis', 'Effusion', 'Pneumonia',
        'Pleural_Thickening', 'Cardiomegaly', 'Nodule', 'Mass'
        ]

    # added for tinygen
    # samplede2017 preparation
    # This is our main dataframe which we have to work on. Yes
    de_2017 = pd.read_csv(os.path.join(MODEL_DIR, 'Data_Entry_2017.csv'))
    de_2017.columns = [
        'Image Index', 'Finding Labels', 'Follow-up #', 'Patient ID',
        'Patient Age', 'Patient Gender', 'View Position', 'OriginalImageWidth',
        'OriginalImageHeight', 'OriginalImagePixelSpacingx',
        'OriginalImagePixelSpacingy', 'ToDrop'
        ]

    # Mapping the paths in the dataframe
    de_2017['Image Paths'] = de_2017['Image Index'].map(lambda x: image_path)

    for i in diseases:
        de_2017[i] = de_2017['Finding Labels'].apply(lambda x: 1 if i in x else 0)
    sample_de_2017 = de_2017.copy()
    sample_de_2017['disease_vector'] = sample_de_2017.apply(lambda x: [x[diseases].values], 1).map(lambda x: x[0])
    # end samplede2017 preparation

    idg = ImageDataGenerator(
        samplewise_center=True, samplewise_std_normalization=True,
        horizontal_flip=False, vertical_flip=False,
        height_shift_range=0.05, width_shift_range=0.1,
        rotation_range=5, shear_range=0.1, fill_mode='reflect', zoom_range=0
        )

    # tiny gen
    # need to include: sample_de_2017 prep
    # need to include: idg and flow_df
    # print('tiny gen')
    tiny_test_df = sample_de_2017.head().reset_index(drop=True)
    tiny_test_df.loc[0, 'Image Index'] = '00003923_006.png'
    # tiny_test_df=tiny_test_df.loc[0,:]
    tiny_test_df.to_csv(os.path.join(MODEL_DIR, 'tiny_test_df.csv'))
    tiny_gen = flow_df(
        idg, tiny_test_df, path='Image Paths', y='disease_vector',
        target_size=IMG_SIZE, color_mode='rgb', batch_size=256
        )

    tiny_X, tiny_Y = next(tiny_gen)

    tiny_pred = loaded_model.predict(tiny_X, batch_size=32, verbose=True)
    tiny_pred = tiny_pred[0]
    # print(tiny_pred)
    # end tiny gen

    from keras import backend as K
    K.clear_session()

    # for i, j in zip(diseases, tiny_pred):
    #     print('%s: %2.2f%%' % (i, j*100))

    pct2 = pd.read_csv(os.path.join(MODEL_DIR, 'predpercentiles.csv'))
    pct2 = pct2.iloc[:, 1:]
    pct2.columns = diseases

    result = {}
    for i in range(0, len(diseases)):
        colthis = diseases[i]
        lookup_percentile = tiny_pred[i]
        toprint = pct2.loc[(pct2[colthis] - lookup_percentile).abs().argsort()[:2], colthis].index[0]
        result[colthis] = int(toprint)

    return result
