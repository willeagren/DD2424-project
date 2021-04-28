import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


class CNN:
    def __init__(self, verbose=False):
        self.model = models.Sequential()
        self.optimizer = 'adam'
        self.loss = tf.keras.losses.MSE
        self.history = None
        self.x_train = None
        self.y_train = None
        self.x_validation = None
        self.y_validation = None
        self.x_test = None
        self.y_test = None
        self.verbose = verbose
        self.DEFAULT_FILEPATH = '../parsed_data/parsed_games_test.csv'

    def init_model(self):
        # conv2D :: n_filter=400, kernel=(4, 4)
        self.model.add(layers.Conv2D(filters=400, kernel_size=(4, 4), input_shape=(8, 8, 7)))
        # MaxPool2D :: kernel=(2, 2), stride=(2, 2)
        self.model.add(layers.MaxPool2D(pool_size=(2, 2), strides=(2, 2)))
        # conv2D :: n_filter=200, kernel=(2, 2)
        self.model.add(layers.Conv2D(filters=200, kernel_size=(2, 2)))
        # Flatten to single output dimension
        self.model.add(layers.Flatten())
        # LinearIP :: output_dim=70, neurons=RELU
        self.model.add(layers.Dense(units=70, activation='linear'))
        # Dropout :: p=0.2
        self.model.add(layers.Dropout(rate=0.2))
        # LinearIP :: output_dim=1, neurons=RELU
        self.model.add(layers.Dense(units=1, activation='linear'))

        if self.verbose:
            print('<|\tInitializing the CNN model')

    def model_summary(self):
        self.model.summary()

    def parse_data(self, filepath=None):
        if filepath is None:
            filepath = self.DEFAULT_FILEPATH
        if self.verbose:
            print(f'<|\tParsing the data from filepath :: {filepath}')
        train = pd.DataFrame(pd.read_csv(filepath))
        x_train = train.loc[:, train.columns != 'y']
        y_train = train.loc[:, train.columns == 'y']
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.2)
        x_valid, x_test, y_valid, y_test = train_test_split(x_valid, y_valid, test_size=0.5)
        self.x_train = x_train.reshape(len(x_train), 8, 8, 7)
        self.x_validation = x_valid.reshape(len(x_valid), 8, 8, 7)
        self.x_test = x_test.reshape(len(x_test), 8, 8, 7)
        self.y_train = y_train
        self.y_validation = y_valid
        self.y_test = y_test

    def batch_train(self, optimizer=None, loss=None, n_epochs=10):
        if self.verbose:
            print(f'<|\tTraining the model utilizing big batch')
            if optimizer is None:
                print(f'<|\t\tNo optimizer specified\t\t=>  using default: {self.optimizer}')
                optimizer = self.optimizer
            if loss is None:
                print(f'<|\t\tNo loss specified\t\t\t=>  using default: {self.loss}')
            loss = self.loss
        self.model.compile(optimizer=optimizer, loss=loss)
        self.history = self.model.fit(self.x_train, self.y_train, epochs=n_epochs, validation_data=(self.x_validation, self.y_validation))

    def plot_history(self, hist_type='loss', xlabel='epoch', ylabel='loss'):
        plt.plot(self.history.history[hist_type], label=hist_type)
        plt.plot(self.history.history[f'val_{hist_type}'], label=f'val_{hist_type}')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.show()

    def model_predict(self, offset=0.5):
        y = self.model.predict(self.x_test)

        assert len(y) == len(self.y_test), \
            print(f'<|\t\tERROR: '
                  f'predictions and target note same length.'
                  f'\n\t\tlen(prediction)={len(y)} :: len(target)={len(self.y_test)}')
        acc = 0
        for (target, predicted) in zip(self.y_test, y):
            if target - offset <= predicted <= target + offset:
                acc += 1
        print(f'<|\tModel testing accuracy: {100*round(float(acc)/float(len(y)), 4)}%')


def main():
    # ----- Unit testing -----
    model = CNN(verbose=True)
    model.init_model()
    model.parse_data()
    model.batch_train(n_epochs=3)
    # model.plot_history()
    model.model_predict()


if __name__ == '__main__':
    main()