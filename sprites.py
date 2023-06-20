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
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.7, -self.rect.height*0.7)


class Trees(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width*1, -self.rect.height*1)


class Apple(pygame.sprite.Sprite):
    def __init__(self, position, groups=None):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/sprites/item_sprites/apple_inventory.png")
        self.apple_pos = position
        self.chest_is_open = False
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)
        self.z = LAYERS['apple']


class City(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.5, -self.rect.height * 0.5)


class Chest(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)
        self.chest = True
        self.chest_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.x, self.rect.y)

        self.apples_surf = pygame.image.load("./graphics/sprites/item_sprites/apple_inventory.png")
        self.apple_pos = position

    def open(self):
        self.image = pygame.image.load("./graphics/chests/chest_open.png")
        self.create_apple()

    def create_apple(self):
        Apple(position=self.apple_pos, groups=[self.groups()[0], self.groups()[2]])
        self.chest_is_open = True


class Sprites:
    def __init__(self, screen, actions):
        # visible sprites = seen ones that don't have collision, obstacles = collisions

        # Get the screen sprites will be displayed on
        self.player = None
        self.screen = screen

        # Sprite Groups
        self.sprite_group = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.bot_group = pygame.sprite.Group()
        self.chest_group = pygame.sprite.Group()
        self.apple_sprites = pygame.sprite.Group()
        self.floor_items = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        # set up sprites and create map
        self.setup(actions)

    def setup(self, actions):
        # Initialize tmx data
        self.screen.fill((114, 117, 27))
        tmx_data = load_pygame('./data/tmx/fuki4.tmx')

        # TILE LAYERS

        # Map borders made with stone walls
        # for x, y, surf in tmx_data.get_layer_by_name("Borders").tiles():
        #     pos = (x * 32, y * 32)
        #     Tile(position=pos, surface=surf, groups=[self.sprite_group, self.obstacle_sprites], z=LAYERS['Borders'])

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

        for obj in tmx_data.get_layer_by_name('Chests'):
            Chest((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites])

        self.player = player.Player((200, 200), self.sprite_group, self.obstacle_sprites, self.screen)
        Tile(
            position=(0, 0),
            surface=pygame.image.load('./graphics/map_bg.png'),
            groups=self.sprite_group,
            z=LAYERS['Ground']
        )
        if actions["Level1"]:
            num_guards = 10
        else:
            num_guards = 20
        for guard in range(num_guards):
            guard = bot.Bot((1600, 1600),
                                       [self.sprite_group, self.bot_group],
                                       self.obstacle_sprites,
                                       self.screen)

            self.bot_group.add(guard)

    def run(self, dt, actions):
        self.screen.fill('black')
        self.sprite_group.custom_draw(self.player)
        mouse_pos = list(pygame.mouse.get_pos())
        mouse_pos[0] += self.sprite_group.offset.x
        mouse_pos[1] += self.sprite_group.offset.y
        for sprite in self.obstacle_sprites.sprites():
            if hasattr(sprite, 'chest'):
                if pygame.mouse.get_pressed()[0] and sprite.chest_rect.collidepoint(mouse_pos):
                    sprite.open()

        # self.screen.blit(self.cursor_image, player.Player.print_crosshair(self.screen))
        self.sprite_group.update(dt, self.bullet_sprites, self.player.hitbox, self.bot_group, self.apple_sprites, actions)
        if self.player.get_hitpoints() <= 0:
            for sprite in self.bot_group:
                sprite.kill()
            self.player.dead = True

    def update(self):
        # self.chest_click()
        self.sprite_group.draw(self.screen)
        self.bullet_sprites.draw(self.screen)
        self.bullet_sprites.update()


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

