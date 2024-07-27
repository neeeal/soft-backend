from tensorflow.keras.preprocessing import image
import tensorflow as tf
import gdown
import cv2
import numpy as np

def load_m():
    target_size = (384, 384)
    efficientnetv2 = tf.keras.applications.efficientnet_v2.EfficientNetV2S(
                    include_top=False,
                    weights='imagenet',
                    input_tensor=None,
                    input_shape=target_size+(3,),
                    pooling='avg',
                )
    # Create a new model on top of EfficientNetV2
    model = tf.keras.Sequential()
    model.add(efficientnetv2)
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.BatchNormalization())
    model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))
    model.compile(optimizer=tf.keras.optimizers.RMSprop(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    url = 'https://drive.google.com/drive/folders/1ptqlr_T0XRs88FAoucKSf7pxcEixRZ9O'
    print("DOWNLOADING............................................")
    gdown.download_folder(url, quiet=True, use_cookies=False)
    print("LOADING WEIGHTS............................................")
    model.load_weights(filepath='model_weights/')
    print("DONE, NOW LAYERS............................................")
    for layer in model.layers:
        layer.trainable = False
    print("LAYERS DONE............................................")
    return model

def preprocessData(data, image_size = 384):
    ## Main Preprocessing function for input images 
    img = cv2.resize(data,(image_size,image_size))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array *= 1./255

    return img_array