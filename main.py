
# IMPORTS
import pygame

import player
import state

import os
import time

os.chdir(os.getcwd())

# CLASSES


class Game:
    def __init__(self):
        pygame.init()

        self.game_canvas = pygame.Surface((1080, 720))
        self.screen = pygame.display.set_mode((1080, 720))
        pygame.display.set_caption("Fukushima 2044")

        # self.clock = pygame.time.Clock()
        self.keepGoing, self.playing = True, True
        self.actions = {"left": False,
                        "right": False,
                        "up": False,
                        "down": False,
                        "Level1": False,
                        "Level2": False,
                        "Pause": False,
                        "Title": False,
                        "Game over": False,
                        "return": False, "Game won": False}
        self.dt, self.prev_time = 0, 0

        self.state_stack = []
        self.load_states()

    def run(self):
        while self.keepGoing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.keepGoing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.keepGoing = False
                    self.playing = False
                if event.key == pygame.K_a:
                    self.actions["left"] = True
                if event.key == pygame.K_d:
                    self.actions["right"] = True
                if event.key == pygame.K_w:
                    self.actions["up"] = True
                if event.key == pygame.K_s:
                    self.actions["down"] = True
                if event.key == pygame.K_1:
                    self.actions["Level1"] = True
                if event.key == pygame.K_1:
                    self.actions["Level2"] = True
                if event.key == pygame.K_ESCAPE:
                    self.actions["Title"] = True
                if event.key == pygame.K_p:
                    self.actions["Pause"] = True
                if event.key == pygame.K_RETURN:
                    self.actions["return"] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    self.actions["left"] = False
                if event.key == pygame.K_d:
                    self.actions["right"] = False
                if event.key == pygame.K_w:
                    self.actions["up"] = False
                if event.key == pygame.K_s:
                    self.actions["down"] = False
                if event.key == pygame.K_1:
                    self.actions["Level1"] = False
                if event.key == pygame.K_1:
                    self.actions["Level2"] = False
                if event.key == pygame.K_ESCAPE:
                    self.actions["Title"] = False
                if event.key == pygame.K_p:
                    self.actions["Pause"] = False
                if event.key == pygame.K_RETURN:
                    self.actions["return"] = False

    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self):
        self.state_stack[-1].render(self.screen)
        # pygame.display.update()
        pygame.display.flip()
        # self.clock.tick(60)

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def load_states(self):
        # Create title state
        self.title_screen = state.Title(self)

        # Add title state to the stack
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False


game = Game()
game.run()
