import os
import random

import player
import pygame
import bot
from pytmx.util_pygame import load_pygame

from settings import *

os.chdir(os.getcwd())


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.6, -self.rect.height*0.4)


class Trees(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.9, -self.rect.height * 0.6)
        self.hitbox.bottom = self.rect.bottom-50


class City(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.2)


class Fence(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)


class Chest(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)


class Sprites:
    def __init__(self, screen):
        # visible sprites = seen ones that don't have collision, obstacles = collisions

        # Get the screen sprites will be displayed on
        self.player = None
        self.screen = screen

        # Cursor
        # self.cursor_image = pygame.image.load('./graphics/UI/crosshair.png')
        # self.cursor_image = pygame.transform.scale(self.cursor_image, (50, 50))

        # Sprite Groups
        self.sprite_group = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bot_group = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        # set up sprites and create map
        self.setup()

    def setup(self):
        # Initialize tmx data
        tmx_data = load_pygame('./data/tmx/fuki4.tmx')

        # TILE LAYERS
        # Map borders made with stone walls
        for x, y, surf in tmx_data.get_layer_by_name("Borders").tiles():
            pos = (x * 32, y * 32)
            Tile(position=pos, surface=surf, groups=[self.sprite_group, self.obstacle_sprites], z=LAYERS['Borders'])

        # Facility
        for layer in ["Facility", "Facility Deco", "Facility Deco 2"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                pos = (x * 32, y * 32)
                Tile(position=pos, surface=surf, groups=[self.sprite_group, self.obstacle_sprites], z=LAYERS['Facility'])

        # OBJECT LAYERS
        # Tree layers
        for obj in tmx_data.get_layer_by_name('Trees'):
            Trees((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites], obj.name)

        for obj in tmx_data.get_layer_by_name('Houses'):
            City((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites], obj.name)

        # for obj in tmx_data.get_layer_by_name('Fence'):
        #     Fence((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites])

        for obj in tmx_data.get_layer_by_name('Chests'):
            Chest((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites])

        self.player = player.Player((1600, 1600), self.sprite_group, self.obstacle_sprites, self.screen)
        Tile(
            position=(0, 0),
            surface=pygame.image.load('./graphics/map_bg.png'),
            groups=self.sprite_group,
            z=LAYERS['Ground']
        )

        guard = bot.Bot((1700, 1700),
                                   [self.sprite_group, self.bot_group],
                                   self.obstacle_sprites,
                                   self.screen,
                                   z=LAYERS["main"])

        self.bot_group.add(guard)

    def run(self, dt):
        self.screen.fill('black')
        self.sprite_group.custom_draw(self.player)
        # self.screen.blit(self.cursor_image, player.Player.print_crosshair(self.screen))
        self.sprite_group.update(dt, self.bullet_sprites, self.player.hitbox, self.bot_group)
        if self.player.get_hitpoints() <= 0:
            self.player.dead = True

    def update(self):
        self.sprite_group.draw(self.screen)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()

        # Value the map will move by
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.screen.get_width() / 2
        self.offset.y = player.rect.centery - self.screen.get_height() / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.screen.blit(sprite.image, offset_rect)

