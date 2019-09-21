import numpy as np
import Snake
from random import randint, choices, seed
import math

class AI:

    def __init__(self):

        self.theta_1 = np.zeros((7, 11))
        self.theta_2 = np.zeros((7, 8))
        self.theta_3 = np.zeros((4, 8))
        self.reproduce = 0.5
        self.die = 0.5

    def decide(self, v_snake) -> str:
        """
        Makes a decision based on <<v_snake>>.
        """

        # == Add bias ==
        v_snake = add_ones(v_snake)

        # == Start forward propogation
        z_2 = self.theta_1 @ v_snake
        a_2 = sigmoid(z_2)
        a_2 = add_ones(a_2)
        z_3 = self.theta_2 @ a_2
        a_3 = sigmoid(z_3)
        a_3 = add_ones(a_3)
        z_4 = self.theta_3 @ a_3
        a_4 = sigmoid(z_4)

        result = ""
        if np.argmax(a_4) == 0:
            result = "RIGHT"
        elif np.argmax(a_4) == 1:
            result = "DOWN"
        elif np.argmax(a_4) == 2:
            result = "LEFT"
        else:
            assert np.argmax(a_4) == 3
            result = "UP"

        return result

    def save(self, path):

        with open(path, 'w') as file:
            self._save(self.theta_1, file)
            self._save(self.theta_2, file)
            self._save(self.theta_3, file)

    def _save(self, theta, file):

        row, column = theta.shape

        for i in range(row):

            line = ""
            for j in range(column):
                line += str(theta[i, j]) + ","

            line = line[:-1]
            line += "\n"
            file.write(line)

    def load(self, path):

        with open(path, 'r') as file:
            self._load(self.theta_1, file)
            self._load(self.theta_2, file)
            self._load(self.theta_3, file)

    def _load(self, theta, file):

        row, column = theta.shape

        for i in range(row):
            data = file.readline().split(",")
            for j in range(column):
                theta[i, j] = float(data[j])

    def copy(self):

        newAI = AI()
        newAI.theta_1 = np.copy(self.theta_1)
        newAI.theta_2 = np.copy(self.theta_2)
        newAI.theta_3 = np.copy(self.theta_3)
        return newAI


@ np.vectorize
def sigmoid(v):
    return 1/(1 + np.exp(-v))


def add_ones(v):
    return np.r_[np.array([1]).reshape(1, 1), v]

