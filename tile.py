import pygame
import map
import os
import random


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, sprite_group, sprite_type, surface=pygame.Surface((map.TILESIZE, map.TILESIZE))):
        super().__init__(sprite_group)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(0, -10)

        # # self.trees = ["shrub1.png", "shrub2.png", "shrub3.png", "tree1.png", "tree2.png", "tree3.png"]
        # # self.image = pygame.image.load(f"./graphics/sprites/trees/{random.choice(self.trees)}")
        #
        # self.rect = self.image.get_rect(topleft=position)
        #
        # # new method I found online to change the hit-box so that it's smaller
        # # if tile type = (something) change the hit-box accordingly, this one is currently for the tree
        # self.hitbox = self.rect.inflate(-100, -50)
