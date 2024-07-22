from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
import gdown
import requests
import base64
from io import BytesIO

image_size = (224)
channels = 3
model=None
# Define the function to handle the KerasLayer when loading the model
def load_m():
    target_size = (384, 384)
    efficientnetv2 = tf.keras.applications.efficientnet_v2.EfficientNetV2S(
                    include_top=False,
                    weights='imagenet',
                    input_tensor=None,
                    input_shape=target_size+(3,),
                    pooling='avg',
                    # classes=1000,
                    # classifier_activation='softmax',
                )
    # Create a new model on top of EfficientNetV2
    model = tf.keras.Sequential()
    # model.add(tf.keras.layers.Input(target_size+(3,)))
    model.add(efficientnetv2)
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.BatchNormalization())
    # model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    model.add(tf.keras.layers.Dropout(0.3))
    model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    # model.add(tf.keras.layers.Dropout(0.5))
    # model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    # model.add(tf.keras.layers.Dropout(0.5))
    # model.add(tf.keras.layers.Dense(1024, activation = 'relu'))
    # model.add(tf.keras.layers.Dropout(0.5))
    # model.add(tf.keras.layers.Dense(512, activation = 'relu'))
    # model.add( tf.keras.layers.Dense(64, activation = 'softmax'))
    # model.add( tf.keras.layers.Dense(32, activation = 'softmax'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))
    model.compile(optimizer=tf.keras.optimizers.RMSprop(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    # model.load_weights(filepath='model_weights/')
    url = 'https://drive.google.com/drive/folders/1ptqlr_T0XRs88FAoucKSf7pxcEixRZ9O'
    gdown.download_folder(url, quiet=True, use_cookies=False)
    model.load_weights(filepath='model_weights/')
    for layer in model.layers:
        layer.trainable = False
    return model

def preprocessData(data, image_size = 384):
    ## Main Preprocessing function for input images 
    img = cv2.resize(data,(image_size,image_size))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array *= 1./255
    
    if len(DATA['image'].strip().split(',')) == 2:
        extension, file = DATA['image'].strip().split(',')
        if extension not in ['data:image/png;base64','data:image/jpeg;base64','data:image/jpg;base64'] : 
            msg = "Invalid file type. Submit only .jpg, .png, or .jpeg files."
            return jsonify({"msg":msg}), 400
        padding = len(file) % 4
        if padding:
            file += '=' * (4 - padding)
        image_data = base64.b64decode(file)
    else:
        file = DATA['image'].strip()
        # if extension in ['data:image/png;base64','data:image/jpeg;base64','data:image/jpg;base64'] : 
        #     msg = "Invalid file type. Submit only .jpg, .png, or .jpeg files."
            # return jsonify({"msg":msg}), 400
        padding = len(file) % 4
        if padding:
            file += '=' * (4 - padding)
        image_data = base64.b64decode(file)
    image_stream = BytesIO(image_data)
    pil_image = Image.open(image_stream#.stream
                            ).convert('RGB')#.resize((300, 300))
    width, height = pil_image.size
    if width > height:
        new_width = 224
        new_height = int((height/width)*224)
    else:
        new_height = 224
        new_width = int((width/height)*224)
    new_size = (new_width, new_height)
    save_image = pil_image.resize(new_size)
    image_stream = BytesIO()
    save_image.save(image_stream, format='JPEG')
    image_data = image_stream.getvalue()
    data = np.array(pil_image)
    # pil_image.save("old_api/test_pil.jpeg")
    

    ## Image for saving
    rice_image = image_data

    # with open("old_api/test_bin.bin", 'wb') as BIN:
    #     BIN.write(rice_image)

    ## Model prediction
    global model
    if model == None:
        model = load_m()#load_model('model_text.h5')
        # model.load_weights()
    data = preprocessData(data)
    result = np.argmax(model(data))+1
    print(result)
    # print("INSERT HERE")
    # result = '3'
        ## End of prediction

    ## Getting Recommendation using output from model
    stress_id = int(result)
    return stress_id