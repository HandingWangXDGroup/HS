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
        self.missile_num = None
        self.target_num = None
        self.missiles = None
        self.targets = None
        self.targets_map = None
        self.missiles_map = None
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
        # init game state
        self.display.fill(BLACK)
        self.missile_num = 2
        self.target_num = 1
        self.target_exist = self.target_num
        a = np.random.randint(1, (self.w - BLOCK_SIZE) // BLOCK_SIZE, size=[self.target_num, 1]) * BLOCK_SIZE
        b = np.random.randint(1, (self.h - BLOCK_SIZE) // BLOCK_SIZE, size=[self.target_num, 1]) * BLOCK_SIZE
        # 目标初始位置随机生成
        self.targets = np.append(a, b, axis=1)
        # 导弹初始位置为0
        self.missiles = np.zeros([self.missile_num, 2])
        # # 导弹移动向量初始化
        # self.moves = np.zeros([self.missile_num, 2])
        # # 导弹攻击状态
        # self.attack = np.zeros([self.missile_num, 1])

        # 地图状态初始化
        for i in range(self.target_num):  # 初始化目标颜色
            pt = Point(self.targets[i][0], self.targets[i][1])
            pygame.draw.rect(self.display, RED, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        for j in range(self.missile_num):  # 初始化导弹颜色
            pt = Point(self.missiles[j][0], self.missiles[j][1])
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        # 初始化地图状态
        self.map = np.ones([self.w // BLOCK_SIZE, self.h // BLOCK_SIZE])
        # 记录地图状态
        self.missiles_map = self.missiles // BLOCK_SIZE
        self.targets_map = self.targets // BLOCK_SIZE
        self.frame_iteration = 0
        self.score = 0
        self.reward = 0
        self.flag = np.ones([self.missile_num, 1])
        self.fuel = np.linspace(1000, 1000, self.missile_num)

        for j in range(self.missile_num):
            # 判断导弹视野范围内是否有目标
            for i in range(len(neighbor)):
                nb = self.missiles_map[j] + neighbor[i]
                if 0 <= nb[0] <= (self.w // BLOCK_SIZE) and 0 <= nb[1] <= (self.h // BLOCK_SIZE):  # 是否在地图内
                    for target in self.targets_map:
                        t = False
                        if nb[0] == target[0] and nb[1] == target[1]:
                            t = True
                    if not t:  # 是否是目标
                        if self.map[int(nb[0])][int(nb[1])] == 1:
                            self.map[int(nb[0])][int(nb[1])] = 0
                            #self.reward += 1.5
                            #print('explored')
                        if i > 0:  # 除导弹位置外的其他位置变白,除非那个位置是目标
                            pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                            pygame.draw.rect(self.display, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                        if i == 0:  # 导弹位置是蓝的
                            pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                    else:
                        self.map[int(nb[0])][int(nb[1])] = 5
                        #self.reward += 5
                        pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                        pygame.draw.rect(self.display, RED, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        self._update_ui()

    def play_step(self, action):
        self._update_ui()
        self.frame_iteration += 1
        self.reward -= 0.5
        #print('walked')
        # 1. collect user input
        '''for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()'''

        # 2. move and attack
        self._operate(action)
        #pygame.time.wait(100)
        self._update_ui()

        #self.observe()

        # 3. check if game over

        game_over = False
        if (self.flag == 0).all() or self.target_exist == 0:
            game_over = True
            return self.reward, game_over, self.score

        # 4. place new food or just move
        # 5. update ui and clock
        self._update_ui()
        # self.clock.tick(SPEED)
        # 6. return game over and score
        return self.reward, game_over, self.score

    '''def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False'''

    def _update_ui(self):

        text = font.render("Score: " + str(self.score), True, BLUE2)
        #self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _operate(self, action):
        action_dic = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1]]
        action_pre = np.zeros([self.missile_num, 3])
        for i in range(self.missile_num):
            action_pre[i] = np.array(action_dic)[action[i]]
        action = action_pre
        for i in range(len(self.flag)):
            if self.flag[i] == 1:
                self.missiles_map[i] = self.missiles_map[i] + action[i][0:2]
                self.missiles[i][0] = self.missiles[i][0] + BLOCK_SIZE*action[i][0]
                self.missiles[i][1] = self.missiles[i][1] + BLOCK_SIZE * action[i][1]
                # self.missiles[i] = self.missiles_map[i]*BLOCK_SIZE
                # 修正飞到边界外（如果将要飞到边界外就原地不动）
                # if int(self.missiles[i][0]) > self.w+1:
                #     self.missiles[i][0] = self.missiles[i][0] - action[i][0] * BLOCK_SIZE
                #     self.missiles_map[i][0] = self.missiles_map[i][0] - action[i][0]
                # if self.missiles[i][0] < 0:
                #     self.missiles[i][0] = self.missiles[i][0] + action[i][0] * BLOCK_SIZE
                #     self.missiles_map[i][0] = self.missiles_map[i][0] + action[i][0]
                # if self.missiles[i][1] >= self.h+1:
                #     self.missiles[i][1] = self.missiles[i][1] - action[i][1] * BLOCK_SIZE
                #     self.missiles_map[i][1] = self.missiles_map[i][1] - action[i][1]
                # if self.missiles[i][1] < 0:
                #     self.missiles[i][1] = self.missiles[i][1] + action[i][1] * BLOCK_SIZE
                #     self.missiles_map[i][1] = self.missiles_map[i][1] + action[i][1]

                # 如果将要飞出边界就停在边界
                if int(self.missiles[i][0]) >= self.w:
                    self.missiles[i][0] = self.w - BLOCK_SIZE
                    self.missiles_map[i][0] = self.w // BLOCK_SIZE - 1
                    self.reward -= 2
                if self.missiles[i][0] < 0:
                    self.missiles[i][0] = 0
                    self.missiles_map[i][0] = 0
                    self.reward -= 2
                if int(self.missiles[i][1]) >= self.h:
                    self.missiles[i][1] = self.h - BLOCK_SIZE
                    self.missiles_map[i][1] = self.h // BLOCK_SIZE - 1
                    self.reward -= 2
                if self.missiles[i][1] < 0:
                    self.missiles[i][1] = 0
                    self.missiles_map[i][1] = 0
                    self.reward -= 2
                self.fuel[i] -= 1

                # 执行攻击指令
                if action[i][2] == 1:  # attack == 1
                    self.flag[i] = 0  # flag置零，让这个导弹失效
                    self.reward -= 2
                    #print('attacked wrong target')
                    for j in range(self.target_num):
                        if (self.missiles_map[i] == self.targets_map[j]).all():
                            self.targets_map[j] = [-1, -1]
                            self.target_exist -= 1

                            self.reward += 50
                            #print('attacked')
                            self.score += 1
                            #pygame.time.wait(1000)
                if self.fuel[i] == 0:
                    self.flag[i] = 0

    def get_avail_agent_actions(self, agent_id):
        if self.flag[agent_id] == 1:
            if int(self.missiles[agent_id][0]) == self.w and int(self.missiles[agent_id][1]) == self.h:
                avail_action = [0, 1, 0, 1, 1]
            elif int(self.missiles[agent_id][0]) == self.w and int(self.missiles[agent_id][1]) == 0:
                avail_action = [0, 1, 1, 0, 1]
            elif int(self.missiles[agent_id][0]) == self.w:
                avail_action = [0, 1, 1, 1, 1]
            elif int(self.missiles[agent_id][0]) == 0 and int(self.missiles[agent_id][1]) == self.h:
                avail_action = [1, 0, 0, 1, 1]
            elif int(self.missiles[agent_id][0]) == 0 and int(self.missiles[agent_id][1]) == 0:
                avail_action = [1, 0, 1, 0, 1]
            elif int(self.missiles[agent_id][0]) == 0:
                avail_action = [1, 0, 1, 1, 1]
            elif int(self.missiles[agent_id][1]) == self.h:
                avail_action = [1, 1, 0, 1, 1]
            elif int(self.missiles[agent_id][1]) == 0:
                avail_action = [1, 1, 1, 0, 1]
            else:
                avail_action = [1, 1, 1, 1, 1]
            return avail_action



    def get_obs(self):
        '''for j in range(self.missile_num):
            # 判断导弹视野范围内是否有目标
            if self.flag[j] == 1:
                pt = Point(self.missiles[j][0], self.missiles[j][1])
                pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                for i in range(len(neighbor)):
                    nb = self.missiles_map[j] + neighbor[i]
                    # 邻域是否在地图内
                    if 0 <= nb[0] <= (self.w // BLOCK_SIZE - 1) and 0 <= nb[1] <= (self.h // BLOCK_SIZE - 1):
                        for target in self.targets_map:
                            if nb[0] == target[0] and nb[1] == target[1]:
                                t = True
                                break
                            t = False
                        if not t:  # 是否是目标
                            if self.map[int(nb[0])][int(nb[1])] == 1:
                                self.map[int(nb[0])][int(nb[1])] = 0
                                self.reward += 1.5
                                #print('explored')
                            if i > 0:  # 除导弹位置外的其他位置变白,除非那个位置是目标
                                pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                                pygame.draw.rect(self.display, WHITE, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                            if i == 0:  # 导弹位置是蓝的
                                pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                                pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                        else:
                            if self.map[int(nb[0])][int(nb[1])] == 1:
                                self.map[int(nb[0])][int(nb[1])] = 5
                                self.reward += 3
                                #print('explored the target')
                            self.map[int(nb[0])][int(nb[1])] = 5
                            pt = Point(nb[0] * BLOCK_SIZE, nb[1] * BLOCK_SIZE)
                            pygame.draw.rect(self.display, RED, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))'''

        obs = np.zeros([self.missile_num, 3])
        for p in range(self.missile_num):
            # missile location
            x, y = int(self.missiles[p][0] / 20), int(self.missiles[p][1] / 20)

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

            # 相对坐标改为方向
            def to_target(x, y):
                loc_x = find_target(x, y)[0]
                loc_y = find_target(x, y)[1]  # 给一个未探索的格子
                for i in range(int(self.w / 20 - 1)):
                    for j in range(int(self.h / 20 - 1)):
                        if self.map[i][j] == 5:
                            loc_x = i - x
                            loc_y = j - y
                        if loc_x == 0 and loc_y == 0:
                            dir = 0
                        elif abs(loc_x) > abs(loc_y):
                            if loc_x > 0:
                                dir = 1  # 向右——0
                            else:
                                dir = 2  # 向左——1
                        elif abs(loc_x) < abs(loc_y):
                            if loc_y > 0:
                                dir = 3  # 向下——2
                            else:
                                dir = 4  # 向上——3
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

            # 多一维——探索到几个目标
            obs[p][0] = explored_target()
            obs[p][1] = to_target(x, y)
            obs[p][2] = self.flag[p]
        return obs

    def get_state(self):
        missile_loc = np.zeros([2, 2])
        for p in range(self.missile_num):
            # missile location
            x, y = int(self.missiles[p][0] / 20), int(self.missiles[p][1] / 20)
            missile_loc[p][0] = x
            missile_loc[p][1] = y

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
            nearest_missile = np.random.randint(0, p)
        else:
            dist = 9999
            for p in range(self.missile_num):
                if abs(missile_loc[p][0] - loc_x) + abs(missile_loc[p][1] - loc_y) < dist:
                    nearest_missile = p
                    dist = abs(missile_loc[p][0] - loc_x) + abs(missile_loc[p][1] - loc_y)
        state = [
            missile_loc,
            explored_target(),
            nearest_missile
        ]
        return state
