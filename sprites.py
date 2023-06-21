"""
date: june 19th, 2023
name: christine wei and william yang
description: this module is meant to contain all the world data and set up the in-game world, along with the player
centered camera
"""

# I - import
import os
import random

import pygame
from pytmx.util_pygame import load_pygame

import bot
import player
from settings import *

# Set working directory to current directory so that it is easier to find files
os.chdir(os.getcwd())


# CLASSES
class Tile(pygame.sprite.Sprite):
    """
    Generic class tile. Parent class for all the tile objects
    """

    def __init__(self, position, surface, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.7, -self.rect.height * 0.7)


class Apple(pygame.sprite.Sprite):
    """
    One of the very nice items in our game. When used, gives user extra health
    """

    def __init__(self, position, groups=None):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/sprites/item_sprites/apple_inventory.png")
        self.is_apple = True
        self.apple_pos = position
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)
        self.z = LAYERS['apple']


class Armor(pygame.sprite.Sprite):
    """
    One of the very nice items in our game. When used, gives user partial immunity from gunshots
    """

    def __init__(self, position, groups):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/sprites/item_sprites/armor.png")
        self.is_armor = True
        self.apple_pos = position
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)
        # No it is not an apple
        self.z = LAYERS['apple']


class Trees(Tile):
    """
    this class contains the tree tiles that are present in the in game world
    """

    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 1, -self.rect.height * 1)


class City(Tile):
    """
    this class contains the city (building) tiles that are present in the in game world
    """

    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.3, -self.rect.height * 0.4)


class Chest(Tile):
    """
    this class contains the chest tiles that are present in the in game world (spawn open objects)
    """

    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.65)
        self.chest = True
        self.chest_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.x, self.rect.y)

        self.apples_surf = pygame.image.load("./graphics/sprites/item_sprites/apple_inventory.png")
        self.apple_pos = position
        self.chest_is_open = False

    def open(self):
        self.image = pygame.image.load("./graphics/chests/chest_open.png")
        self.create_apple()

    def create_apple(self):
        self.chest_is_open = True
        Apple(position=self.apple_pos, groups=[self.groups()[0], self.groups()[2]])


class Sprites:
    """
    this is the main setup and update area for any sprite within the game, emphasizing Entities in the IDEA framework
    """

    def __init__(self, screen, actions):
        """
        Dunder function, initializes all the attributes
        :param screen:
        :param actions:
        """

        # Initialize the player (PyCharm thing)
        self.player = None

        # Get the screen sprites will be displayed on
        self.screen = screen

        # SPRITE GROUPS
        # All the sprites in this group so that we can update all the sprites at the same time
        self.sprite_group = CameraGroup()
        # All the apples and their chests
        self.apple_sprites = pygame.sprite.Group()
        # All sprites that must be checked for collision
        self.obstacle_sprites = pygame.sprite.Group()
        # All the bot guards
        self.bot_group = pygame.sprite.Group()
        # All bullet sprites
        self.bullet_sprites = pygame.sprite.Group()

        # set up sprites and create map
        self.setup(actions)

    def setup(self, actions):
        """
        This is where the map is creates
        :param actions:
        :return:
        """

        # E - Entities and initializing
        #  initialize tmx data
        self.screen.fill((114, 117, 27))
        tmx_data = load_pygame('./data/tmx/fuki4.tmx')

        # Create the facility
        for x, y, surf in tmx_data.get_layer_by_name("Facility").tiles():
            pos = (x * 32, y * 32)
            Tile(position=pos, surface=surf, groups=[self.sprite_group, self.obstacle_sprites],
                 z=LAYERS['Facility'])

        # Add facility Decorations
        for layer in ["Facility Deco", "Facility Deco 2"]:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                pos = (x * 32, y * 32)
                Tile(position=pos, surface=surf, groups=[self.sprite_group],
                     z=LAYERS['Facility'])

        # OBJECT LAYERS
        # tree layers
        for obj in tmx_data.get_layer_by_name('Trees'):
            Trees((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites], obj.name)

        # house layers
        for obj in tmx_data.get_layer_by_name('Houses'):
            City((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites], obj.name)

        # chest layers
        for obj in tmx_data.get_layer_by_name('Chests'):
            Chest((obj.x, obj.y), obj.image, [self.sprite_group, self.obstacle_sprites, self.apple_sprites])

        # MAP BACKGROUND (THE GROUND)
        Tile(
            position=(0, 0),
            surface=pygame.image.load('./graphics/map_bg.png'),
            groups=self.sprite_group,
            z=LAYERS['Ground']
        )

        # Create the player
        self.player = player.Player((1600, 1600), self.sprite_group, self.obstacle_sprites, self.bullet_sprites,
                                    self.apple_sprites, self.screen)

        # Initialize AI guard entities based on the current level
        # Initialize AI for level 1
        if actions["Level1"]:
            num_guards = 10
        # Initialize AI for level 2
        elif actions["Level2"]:
            num_guards = 20
        for guard in range(num_guards):
            guard = bot.Bot((random.randint(600, 2600), random.randint(600, 2600)),
                            [self.sprite_group, self.obstacle_sprites, self.bot_group],
                            self.obstacle_sprites,
                            self.screen, self.bullet_sprites,
                            z=LAYERS["main"])

            self.bot_group.add(guard)

    def run(self, dt, actions):
        """
        A - ACTIONS. Whate occurs in the loop
        :param dt:
        :param actions:
        :return:
        """

        # R - Refresh screen and update all sprites
        self.screen.fill('black')
        self.sprite_group.custom_draw(self.player)

        # Get mouse position on the screen
        mouse_pos = list(pygame.mouse.get_pos())

        # Calculate mouse position on the map
        mouse_pos[0] += self.sprite_group.offset.x
        mouse_pos[1] += self.sprite_group.offset.y

        # Check if a chest has been clicked
        for chest in self.apple_sprites.sprites():
            if hasattr(chest, 'chest') and not chest.chest_is_open:
                if pygame.mouse.get_pressed()[0] and chest.chest_rect.collidepoint(mouse_pos):
                    print(chest.apple_pos, chest.chest_is_open)
                    chest.open()

        self.sprite_group.update(dt, self.bullet_sprites, self.player.image_position, self.bot_group, actions)
        if self.player.get_hitpoints() <= 0:
            for sprite in self.bot_group:
                sprite.kill()
            self.player.dead = True

        # Check for dead sprites
        for sprite in self.bot_group:
            if sprite.bot_dead:
                Armor(sprite.position, [self.sprite_group, self.apple_sprites])
                sprite.kill()

    def update(self):
        """
        R - Refresh screen and draw all the sprites
        :return:
        """
        self.sprite_group.draw(self.screen)
        self.bullet_sprites.draw(self.screen)
        self.bullet_sprites.update()


class CameraGroup(pygame.sprite.Group):
    """
    this class contains the player-centered camera in the game, keeping the player visible at all times, representing
    the Refresh Screen part of the ALTER framework or the Display/Action part of the IDEA framework
    """

    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()

        # value the map will move by
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        # draws all visible sprites
        self.offset.x = player.rect.centerx - self.screen.get_width() / 2
        self.offset.y = player.rect.centery - self.screen.get_height() / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    sprite.image_position = offset_rect
                    self.screen.blit(sprite.image, offset_rect)
