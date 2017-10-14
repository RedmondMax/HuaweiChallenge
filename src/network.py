from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import glob
import numpy as np
import cv2
from tqdm import tqdm
import os
import matplotlib.pyplot as plt

TRAINING_PATH_Y = '../data/4000unlabeledLP_padded/'
TRAINING_PATH_X = '../data/4000unlabeledLP_blurred_padded/'
IMG_HEIGHT = 78
IMG_WIDTH = 245
LR = 1e-3
MODEL_NAME = 'deblurring-{}-{}.model'.format(LR, '1')

# Data loading and preprocessing
def process_test_data(filepath,value):
    test_data = []
    for img in tqdm(os.listdir(filepath)):
        path = os.path.join(filepath,img)
        img = cv2.resize(cv2.imread(path),(IMG_WIDTH,IMG_HEIGHT))
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        test_data.append(np.array(img))
    np.save('train_data_'+value+'.npy',test_data)
    return test_data

def network():
    # Building convolutional network
    network = input_data(shape=[None, IMG_WIDTH, IMG_HEIGHT, 3], name='input')
    network = conv_2d(network, 32, 3, activation='relu', regularizer="L2")
    network = local_response_normalization(network)
    network = conv_2d(network, 64, 3, activation='relu', regularizer="L2")
    network = local_response_normalization(network)
    network = conv_2d(network, 3, 3, activation='relu', regularizer="L2")
    network = regression(network, optimizer='adam', learning_rate=0.01,
                         loss='categorical_crossentropy', name='target')
    model = tflearn.DNN(network, tensorboard_verbose=0)
    if os.path.exists('{}.meta'.format(MODEL_NAME)):
        model.load(MODEL_NAME)
    return model

def main():
    if os.path.isfile('train_data_X.npy') is False:
        process_test_data(TRAINING_PATH_X,'X')
    train_data_X = np.load('train_data_X.npy')
    if os.path.isfile('train_data_Y.npy') is False:
        process_test_data(TRAINING_PATH_Y,'Y')
    train_data_Y = np.load('train_data_Y.npy')

    X = np.array([i for i in train_data_X]).reshape(-1, IMG_WIDTH, IMG_HEIGHT, 3)
    Y = np.array([i for i in train_data_Y]).reshape(-1, IMG_WIDTH, IMG_HEIGHT, 3)

    model = network()

    if os.path.exists('{}.meta'.format(MODEL_NAME)) is False:
        model.save('{}.model'.format(MODEL_NAME))

    #model.fit({'input': X}, {'target': Y}, n_epoch=3,
    #       snapshot_step=100, show_metric=True, run_id=MODEL_NAME)


    fig = plt.figure()
    ax = fig.add_subplot(2,2,1)
    data = X[0].reshape(-1,IMG_WIDTH,IMG_HEIGHT,3)
    ax.imshow(X[0])
    result = model.predict(data)[0]
    ax = fig.add_subplot(2,2,2)
    ax.imshow(result)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    plt.show()


if __name__ == '__main__':
    main()
