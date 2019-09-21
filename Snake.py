import tkinter as tk
from tkinter import ttk
import random
import numpy as np
import SnakeAI
import os

class Snake:
    """
    Abstract Snake class.
    """

    def __init__(self, AI):

        """
        Initialize the basic snake and set up the game.
        """
        # State of the snake
        self._currsnake = []  # The pixels the snake occupies
        self._terminated = False
        self._ate = False
        self._direction = "RIGHT"
        self._len = 3

        self.x, self.y = (20, 20)
        self._nugget = (0, 0)
        self.score = 0

        self._AI = AI
        self._snake_features = np.zeros((10, 1))

        self._create_snake()
        self._set_nugget()

    def _create_snake(self):
        """
        Set up the snake to be in position.
        """

        startX = 2
        startY = 1
        for i in range(self._len):
            self._currsnake.append((startX + i, startY))

        self._update_features()

    def _move(self):
        """
        Makes a move based on the decision made by the AI, and updates
        the snake features.
        """
        move = self._AI.decide(self._snake_features)
        self._direction = move
        self._update_features()

    def play(self):
        raise NotImplementedError

    def _check(self):
        """
        Checks if the snake has died or has eaten a fruit.
        """

        # Checks if dead due to self injury
        headX, headY = self._currsnake[-1]
        if (headX, headY) in self._currsnake[:-1]:
            self._terminated = True

        # Check if dead due to hitting wall
        if headX == self.x or headY == self.y or headX == -1 or headY == -1:
            self._terminated = True

        # Check if nugget is eaten
        if (headX, headY) == self._nugget:
            self._ate = True
            self._len += 1
            self._set_nugget()

    def _set_nugget(self):
        """
        Update the _nugget to be in a new, random location.
        """

        self._nugget = (random.randint(0, self.x - 1),
                        random.randint(0, self.y - 1))

        # Prevents nugget from being in snake body
        if self._nugget in self._currsnake:
            self._set_nugget()

    def _update_score(self):
        """
        Updates the score of the snake.
        """

        if self._terminated:
            self.score -= 100

        if self._ate:
            self.score += 10

        # previous snake head
        prev_dis = abs(self._currsnake[-2][0] - self._nugget[0]) + \
                   abs(self._currsnake[-2][1] - self._nugget[1])

        # current snake head
        new_dis = abs(self._currsnake[-1][0] - self._nugget[0]) + \
                  abs(self._currsnake[-1][1] - self._nugget[1])

        if new_dis <= prev_dis:
            self.score += 2
        else:
            self.score -= 4

    def _update_features(self):
        """
        Update the feature vector for the snake.
        """

        curr_head = self._currsnake[-1]

        if self._direction == "RIGHT":
            self._snake_features[0:4] = np.array([1, 0, 0, 0]).reshape(4, 1)
        elif self._direction == "DOWN":
            self._snake_features[0:4] = np.array([0, 1, 0, 0]).reshape(4, 1)
        elif self._direction == "LEFT":
            self._snake_features[0:4] = np.array([0, 0, 1, 0]).reshape(4, 1)
        else:  # self._direction == "UP"
            self._snake_features[0:4] = np.array([0, 0, 0, 1]).reshape(4, 1)

        # Distance from head to nugget in X, Y direction.
        sX, sY = self._nugget[0] - curr_head[0], self._nugget[1] - curr_head[1]
        self._snake_features[4:6] = np.array([sX, sY]).reshape(2, 1)

        occ = np.zeros((4, 1))

        # Check left of the head, 1 if obstacle present
        if (curr_head[0] - 1, curr_head[1]) in self._currsnake or \
                curr_head[0] - 1 < 0:
            occ[0] = 1
        # Check right of head, 1 if obstacle present
        if (curr_head[0] + 1, curr_head[1]) in self._currsnake or \
                curr_head[0] + 1 > self.x - 1:
            occ[1] = 1
        # Check top of head, 1 if obstacle present
        if (curr_head[0], curr_head[1] - 1) in self._currsnake or \
                curr_head[1] - 1 < 0:
            occ[2] = 1
        # Check bottom of head, 1 if obstacle present
        if (curr_head[0], curr_head[1] + 1) in self._currsnake or \
                curr_head[0] + 1 > self.y - 1:
            occ[3] = 1

        self._snake_features[6:10] = occ


class TrainingSnake(Snake):

    def __init__(self, AI):
        """
        Initialize the TrainingSnake.
        """
        Snake.__init__(self, AI)

    def play(self):

        """
        Plays the game of snake. Ends when the snake dies or score goes below
        threshold score.
        """
        while (not self._terminated) and self.score > -100:
            self._next()

    def _next(self):
        """
        Helper function for play(). It updates the new head of the snake
        and deletes the tail if the snake hasn't ate anything.
        """
        # == Set the head and tails of the snake ==

        headX, headY = self._currsnake[-1]
        tailX, tailY = self._currsnake[0]

        newheadX, newheadY = 0, 0

        # == Remove the tail if nugget not eaten==
        if not self._ate:
            self._currsnake.pop(0)
        else:
            self._ate = False

        self._move()

        if self._direction == "LEFT":
            newheadX, newheadY = headX - 1, headY

        elif self._direction == "RIGHT":
            newheadX, newheadY = headX + 1, headY

        elif self._direction == "UP":
            newheadX, newheadY = headX, headY - 1

        else:
            assert self._direction == "DOWN"
            newheadX, newheadY = headX, headY + 1

        self._currsnake.append((newheadX, newheadY))

        self._check()
        self._update_score()


class RenderSnake(TrainingSnake):

    def __init__(self, root, AI):
        """
        Initialize the RenderSnake, and setup the rendering.
        """
        TrainingSnake.__init__(self, AI)
        self.root = root
        self._time = 50  # speed of the snake
        self._gameboard = [] # The pixels

        self._gameframe = ttk.Frame(self.root,
                                    relief="solid", padding=(5, 5))
        for i in range(0, self.y):
            newline = []
            for j in range(self.x):
                newcell = tk.Label(self._gameframe, background="white")
                newcell.grid(row=i, column=j, ipadx=6)
                newline.append(newcell)
            self._gameboard.append(newline)

        self._gameframe.grid(row=0, column=0, columnspan=2)

        self._render_startsnake()
        self._rendernugget()

    def _render_startsnake(self):
        """
        Set up the starting snake, and display it.
        """
        startY, startX = 1, 2
        for i in range(self._len):
            self._gameboard[startY][startX + i].config(background="black")

    def play(self):
        """
        Plays a turn after self._time milliseconds.
        """
        if self._terminated or self.score < -100:
            return

        self._next()
        self.root.after(self._time, self.play)

    def _next(self):
        """
        Updates the gameboard with the appropiate snake and nugget.
        """
        tailX, tailY = self._currsnake[0]

        if not self._ate:
            self._gameboard[tailY][tailX].config(background="white")

        TrainingSnake._next(self)

        newheadX, newheadY = self._currsnake[-1]
        if 0 <= newheadY < self.y and 0 <= newheadX < self.x:
            self._gameboard[newheadY][newheadX].config(
                background="black")

        self._rendernugget()

    def _rendernugget(self):
        """
        Render the nugget in its location.
        """
        nuggetX, nuggetY = self._nugget
        self._gameboard[nuggetY][nuggetX].config(background="red")


class PlayableSnake(RenderSnake):

    def __init__(self, root):
        """
        Initialize the PlayableSnake, and bind commands. Also slows down
        the time to a reasonable playable time.
        """
        RenderSnake.__init__(self, root, None)
        self.root.bind("<Left>", lambda e: self._move("LEFT"))
        self.root.bind("<Right>", lambda e: self._move("RIGHT"))
        self.root.bind("<Up>", lambda e: self._move("UP"))
        self.root.bind("<Down>", lambda e: self._move("DOWN"))
        self._time = 150

    def _move(self, direction = None):
        """
        Changes the direction according to the player.
        """
        # This is because TrainingSnake calls _move() in the play() method.

        if direction is None:
            direction = self._direction

        self._direction = direction



if __name__ == "__main__":

    AI = SnakeAI.AI()
    AI_PATH = os.getcwd() + "/AI_1.csv"
    AI.load(AI_PATH)

    root = tk.Tk()
    game = RenderSnake(root, AI)
    game.play()
    root.mainloop()
