import pygame


class Sprites:
    def __init__(self):
        # visible sprites = seen ones that don't have collision, obstacles = collisions
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

    def update(self):
        print("hiu")
        # update and draw the game
    # sprite_interactions
