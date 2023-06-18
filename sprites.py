import os
import player
import pygame
from pytmx.util_pygame import load_pygame

from settings import *

os.chdir(os.getcwd())


def draw_rect_outline(surface, screen, rect, color, width=1):
    x, y, w, h = rect
    width = max(width, 1)  # Draw at least one rect.
    width = min(min(width, w//2), h//2)  # Don't overdraw.

    # This draws several smaller outlines inside the first outline. Invert
    # the direction if it should grow outwards.
    for i in range(width):
        pygame.gfxdraw.rect(screen, (x+i, y+i, w-i*2, h-i*2), color)


class Tile(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.8, -self.rect.height*0.8)


class Trees(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.01, -self.rect.height * 0.01)


class City(Tile):
    def __init__(self, position, surface, groups, name):
        super().__init__(position, surface, groups)


class Fence(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)


class Chest(Tile):
    def __init__(self, position, surface, groups):
        super().__init__(position, surface, groups)


class Sprites:
    def __init__(self, screen):
        # visible sprites = seen ones that don't have collision, obstacles = collisions

        # Get the screen sprites will be displayed on
        self.player = None
        self.screen = screen

        # Sprite Groups
        self.sprite_group = CameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # set up sprites and create map
        self.setup()

    def setup(self):
        # Initialize tmx data
        tmx_data = load_pygame('./data/tmx/fuki4.tmx')

        # TILE LAYERS
        # Map borders made with stone walls
        for x, y, surf in tmx_data.get_layer_by_name("Borders").tiles():
            pos = (x * 32, y * 32)
            Tile(position=pos, surface=surf, groups=[self.sprite_group], z=LAYERS['Borders'])

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

    def run(self, dt):
        self.screen.fill('black')
        self.sprite_group.custom_draw(self.player)
        self.sprite_group.update(dt)

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

