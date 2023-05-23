import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('./Font/arial.ttf', 25)
Point = namedtuple('Point', 'x, y')
Treasure = pygame.image.load('Treasure.png')
Treasure = pygame.transform.scale(Treasure, (20, 20))
Seeker = pygame.image.load('Seeker.jpg')
Seeker = pygame.transform.scale(Seeker, (20, 20))

# rgb colors
WHITE = (255, 255, 255)
# WHITE = (100, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 100

neighbor = np.array([[0, 0], [0, 1], [0, -1], [1, 0], [-1, 0]])


class XunFeiGame:
    def __init__(self, w=200, h=200):
        self.frame_iteration = None
        self.seeker_num = None
        self.target_num = None
        self.seekers = None
        self.targets = None
        self.targets_map = None
        self.seekers_map = None
        self.flag = None
        self.scores = None
        self.moves = None
        self.attack = None
        self.map = None
        self.fuel = None
        self.target_exist = None

        self.reward = None
        self.score = None
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('XunFei')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.display.fill(BLACK)
        self.seeker_num = 2
        self.target_num = 1
        self.target_exist = self.target_num
        a = np.random.randint(1, (self.w - BLOCK_SIZE) // BLOCK_SIZE, size=[self.target_num, 1]) * BLOCK_SIZE
        b = np.random.randint(1, (self.h - BLOCK_SIZE) // BLOCK_SIZE, size=[self.target_num, 1]) * BLOCK_SIZE
        self.targets = np.append(a, b, axis=1)
        self.seekers = np.zeros([self.seeker_num, 2])
        for i in range(self.target_num):
            pt = Point(self.targets[i][0], self.targets[i][1])
            pygame.draw.rect(self.display, RED, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        for j in range(self.seeker_num):
            pt = Point(self.seekers[j][0], self.seekers[j][1])
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        self.map = np.ones([self.w // BLOCK_SIZE, self.h // BLOCK_SIZE])
        self.seekers_map = self.seekers // BLOCK_SIZE
        self.targets_map = self.targets // BLOCK_SIZE
        self.frame_iteration = 0
        self.score = 0
        self.reward = 0
        self.flag = np.ones([self.seeker_num, 1])
        self.fuel = np.linspace(1000, 1000, self.seeker_num)

        for j in range(self.seeker_num):
            for i in range(len(neighbor)):
                nb = self.seekers_map[j] + neighbor[i]
                if 0 <= nb[0] <= (self.w // BLOCK_SIZE) and 0 <= nb[1] <= (self.h // BLOCK_SIZE):
                    for target in self.targets_map:
                        t = False
                        if nb[0] == target[0] and nb[1] == target[1]:
                            t = True
                    if not t:
                        if self.map[int(nb[0])][int(nb[1])] == 1:
                            self.map[int(nb[0])][int(nb[1])] = 0
                        if i > 0:
                            pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                            pygame.draw.rect(self.display, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                        if i == 0:
                            pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                    else:
                        self.map[int(nb[0])][int(nb[1])] = 5
                        pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                        pygame.draw.rect(self.display, RED, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        self._update_ui()

    def play_step(self, action):
        self._update_ui()
        self.frame_iteration += 1
        self.reward -= 0.5

        self._operate(action)
        self._update_ui()



        game_over = False
        if (self.flag == 0).all() or self.target_exist == 0:
            game_over = True
            return self.reward, game_over, self.score

        self._update_ui()
        return self.reward, game_over, self.score

    def _update_ui(self):

        text = font.render("Score: " + str(self.score), True, BLUE2)
        #self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _operate(self, action):
        action_dic = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1]]
        action_pre = np.zeros([self.seeker_num, 3])
        for i in range(self.seeker_num):
            action_pre[i] = np.array(action_dic)[action[i]]
        action = action_pre
        for i in range(len(self.flag)):
            if self.flag[i] == 1:
                self.seekers_map[i] = self.seekers_map[i] + action[i][0:2]
                self.seekers[i][0] = self.seekers[i][0] + BLOCK_SIZE*action[i][0]
                self.seekers[i][1] = self.seekers[i][1] + BLOCK_SIZE * action[i][1]

                if int(self.seekers[i][0]) >= self.w:
                    self.seekers[i][0] = self.w - BLOCK_SIZE
                    self.seekers_map[i][0] = self.w // BLOCK_SIZE - 1
                    self.reward -= 2
                if self.seekers[i][0] < 0:
                    self.seekers[i][0] = 0
                    self.seekers_map[i][0] = 0
                    self.reward -= 2
                if int(self.seekers[i][1]) >= self.h:
                    self.seekers[i][1] = self.h - BLOCK_SIZE
                    self.seekers_map[i][1] = self.h // BLOCK_SIZE - 1
                    self.reward -= 2
                if self.seekers[i][1] < 0:
                    self.seekers[i][1] = 0
                    self.seekers_map[i][1] = 0
                    self.reward -= 2
                self.fuel[i] -= 1

                if action[i][2] == 1:
                    self.flag[i] = 0
                    self.reward -= 2
                    for j in range(self.target_num):
                        if (self.seekers_map[i] == self.targets_map[j]).all():
                            self.targets_map[j] = [-1, -1]
                            self.target_exist -= 1

                            self.reward += 50
                            self.score += 1
                if self.fuel[i] == 0:
                    self.flag[i] = 0

    def get_avail_agent_actions(self, agent_id):
        if self.flag[agent_id] == 1:
            if int(self.seekers[agent_id][0]) == self.w and int(self.seekers[agent_id][1]) == self.h:
                avail_action = [0, 1, 0, 1, 1]
            elif int(self.seekers[agent_id][0]) == self.w and int(self.seekers[agent_id][1]) == 0:
                avail_action = [0, 1, 1, 0, 1]
            elif int(self.seekers[agent_id][0]) == self.w:
                avail_action = [0, 1, 1, 1, 1]
            elif int(self.seekers[agent_id][0]) == 0 and int(self.seekers[agent_id][1]) == self.h:
                avail_action = [1, 0, 0, 1, 1]
            elif int(self.seekers[agent_id][0]) == 0 and int(self.seekers[agent_id][1]) == 0:
                avail_action = [1, 0, 1, 0, 1]
            elif int(self.seekers[agent_id][0]) == 0:
                avail_action = [1, 0, 1, 1, 1]
            elif int(self.seekers[agent_id][1]) == self.h:
                avail_action = [1, 1, 0, 1, 1]
            elif int(self.seekers[agent_id][1]) == 0:
                avail_action = [1, 1, 1, 0, 1]
            else:
                avail_action = [1, 1, 1, 1, 1]
            return avail_action



    def get_obs(self):
        obs = np.zeros([self.seeker_num, 3])
        for p in range(self.seeker_num):
            # seeker location
            x, y = int(self.seekers[p][0] / 20), int(self.seekers[p][1] / 20)

            def explored_target():
                target_num = 0
                for i in range(int(self.w / 20 - 1)):
                    for j in range(int(self.h / 20 - 1)):
                        if self.map[i][j] == 5:
                            target_num += 1
                return target_num

            def find_target(x, y):
                tar = 0
                for i in range(int(self.w / 20 - 1)):
                    for j in range(int(self.h / 20 - 1)):
                        if self.map[i][j] == 5:
                            loc_x = i
                            loc_y = j
                            tar = 1
                if tar != 1:
                    unexplored = []
                    for i in range(int(self.w / 20 - 1)):
                        for j in range(int(self.h / 20 - 1)):
                            if self.map[i][j] == 1:
                                unexplored.append([i, j])
                    index = np.random.randint(0, len(unexplored))
                    loc_x = unexplored[index][0]
                    loc_y = unexplored[index][1]
                return loc_x, loc_y

            def to_target(x, y):
                loc_x = find_target(x, y)[0]
                loc_y = find_target(x, y)[1]
                for i in range(int(self.w / 20 - 1)):
                    for j in range(int(self.h / 20 - 1)):
                        if self.map[i][j] == 5:
                            loc_x = i - x
                            loc_y = j - y
                        if loc_x == 0 and loc_y == 0:
                            dir = 0
                        elif abs(loc_x) > abs(loc_y):
                            if loc_x > 0:
                                dir = 1
                            else:
                                dir = 2
                        elif abs(loc_x) < abs(loc_y):
                            if loc_y > 0:
                                dir = 3
                            else:
                                dir = 4
                        else:
                            if loc_x > 0:
                                if np.random.uniform(0, 1) > 0.5:
                                    dir = 1
                                else:
                                    dir = 3
                            elif loc_x < 0:
                                if np.random.uniform(0, 1) > 0.5:
                                    dir = 2
                                else:
                                    dir = 4
                return dir

            obs[p][0] = explored_target()
            obs[p][1] = to_target(x, y)
            obs[p][2] = self.flag[p]
        return obs

    def get_state(self):
        seeker_loc = np.zeros([2, 2])
        for p in range(self.seeker_num):
            x, y = int(self.seekers[p][0] / 20), int(self.seekers[p][1] / 20)
            seeker_loc[p][0] = x
            seeker_loc[p][1] = y

        def explored_target():
            target_num = 0
            for i in range(int(self.w / 20 - 1)):
                for j in range(int(self.h / 20 - 1)):
                    if self.map[i][j] == 5:
                        target_num += 1
            return target_num

        def find_target():
            tar = 0
            loc_x = 0
            loc_y = 0
            for i in range(int(self.w / 20 - 1)):
                for j in range(int(self.h / 20 - 1)):
                    if self.map[i][j] == 5:
                        loc_x = i
                        loc_y = j
                        tar = 1
            return tar, loc_x, loc_y
        tar, loc_x, loc_y = find_target()
        if tar != 1:
            nearest_seeker = np.random.randint(0, p)
        else:
            dist = 9999
            for p in range(self.seeker_num):
                if abs(seeker_loc[p][0] - loc_x) + abs(seeker_loc[p][1] - loc_y) < dist:
                    nearest_seeker = p
                    dist = abs(seeker_loc[p][0] - loc_x) + abs(seeker_loc[p][1] - loc_y)
        state = [
            seeker_loc,
            explored_target(),
            nearest_seeker
        ]
        return state
