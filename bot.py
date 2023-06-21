"""
date: june 19th, 2023
name: christine wei and william yang
description: this module contains all information about any certain bot guard, including position, inventory, items, etc.
"""

import random

import pygame

from settings import LAYERS


class Bot(pygame.sprite.Sprite):
    """
    main bot class for our game, contains information about the inventory, status, health, objectives and position
    of where the bot is and also detects events and moves the bot in a patrol pattern - thus encompasses Entities,
    Actions, and Events within the IDEA and ALTER frameworks
    """

    def __init__(self, position, sprite_group, obstacle_sprites, screen, bullet_sprites, z):
        super().__init__(sprite_group)
        self.bot_dead = False
        self.dead = None
        self.bullet_sprites = bullet_sprites
        self.engage_sounds = [pygame.mixer.Sound("./audio/Enemy_Contact.mp3"),
                              pygame.mixer.Sound("./audio/Enemy_Contact_2.mp3")]
        self.already_said_enemy_contact = False
        self.return_fire = False
        self.return_fire_counter = 0

        self.position = position
        self.screen = screen
        self.mouse_clicked = False
        self.clock = pygame.time.Clock()
        self.player_hitpoints = 100
        self.armor_value = 0
        self.inventory = Inventory(self.player_hitpoints, self.armor_value)
        self.sprite_right = pygame.image.load("./graphics/player/right/right_0.png")
        self.hit_marker_sound = pygame.mixer.Sound("./audio/hit_marker.mp3")

        self.image = self.sprite_right
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.x_direction = None
        self.y_direction = None

        self.speed = 30
        self.directions = [
            (0, -1),  # Up
            (1, 0),  # Right
            (0, 1),  # Down
            (-1, 0)  # Left
        ]
        self.change_direction_timer = pygame.time.get_ticks()
        self.patrol_timer = pygame.time.get_ticks()
        self.patrol_duration = 2000  # 2 seconds
        self.walking_direction = random.randint(0, 3)

        self.obstacle_sprites = obstacle_sprites
        self.death_sounds = [pygame.mixer.Sound("./audio/death_sound.wav"),
                             pygame.mixer.Sound("./audio/death_sound_2.wav"),
                             pygame.mixer.Sound("./audio/death_sound_3.wav")]
        self.gun_reloading_sound = pygame.mixer.Sound("./audio/gun_reload.mp3")
        self.hitbox = self.rect
        self.reloading_sound_played = None
        self.z = LAYERS['main']

    def move_ai(self):
        if self.inventory.weapon is not None:
            self.image = self.sprite_right

        if pygame.time.get_ticks() - self.change_direction_timer >= self.patrol_duration:
            self.change_direction_timer = pygame.time.get_ticks()
            self.patrol_timer = pygame.time.get_ticks()
            self.walking_direction = random.randint(0, 3)

        else:
            if not self.return_fire:
                self.x_direction = self.speed * self.directions[self.walking_direction][0]
                self.y_direction = self.speed * self.directions[self.walking_direction][1]
            else:
                self.x_direction = 0 * self.directions[self.walking_direction][0]
                self.y_direction = 0 * self.directions[self.walking_direction][1]

    def collisions(self, direction):
        for sprite in self.bullet_sprites.sprites():
            if sprite.rect.colliderect(self.image_position):
                if self.inventory.armor_value == 0:
                    self.inventory.player_hitpoints -= sprite.bullet_damage
                else:
                    self.inventory.armor_value -= sprite.bullet_damage
                    if self.inventory.armor_value < 0:
                        self.inventory.player_hitpoints += sprite.bullet_damage
                        self.inventory.armor_value = 0
                sprite.kill()
                # return fire by the AI
                self.return_fire = True
                if self.already_said_enemy_contact is False:
                    if self.inventory.player_hitpoints > 0:
                        channel6 = pygame.mixer.Channel(5)
                        channel6.play(self.engage_sounds[random.randint(0, 1)])
                    self.already_said_enemy_contact = True
                channel4 = pygame.mixer.Channel(3)
                channel4.play(self.hit_marker_sound)

        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.x_direction > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.x_direction < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.y_direction > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.y_direction < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    def update(self, dt, bullet_sprites, player_position, bot_group, actions):
        if self.return_fire:
            for bot in bot_group:
                if bot.hitbox.colliderect(pygame.Rect(player_position[0] - 500, player_position[1] - 500, 1000, 1000)):
                    bot.return_fire = True
                    bot.already_said_enemy_contact = True

            self.return_fire_counter += 1
            if self.return_fire_counter % 45 == 0:
                self.inventory.weapon.shoot(self.screen, player_position, bullet_sprites, self.obstacle_sprites,
                                            self.image_position)
        if self.inventory.player_hitpoints <= 0:
            print(self.inventory.player_hitpoints)
            channel7 = pygame.mixer.Channel(6)
            channel7.play(self.death_sounds[random.randint(0, 2)])
            self.bot_dead = True

        if self.inventory.weapon is not None:
            if self.change_direction_timer == 0:
                self.change_direction_timer = pygame.time.get_ticks()

            if pygame.time.get_ticks() - self.change_direction_timer >= 10000:
                self.change_direction_timer = pygame.time.get_ticks()
                self.walking_direction = random.randint(1, 4)

            self.move_ai()

        elif self.inventory.weapon:
            if self.inventory.weapon.bullet_capacity <= 0:
                if not self.reloading_sound_played:
                    channel = pygame.mixer.Channel(6)
                    channel.play(self.gun_reloading_sound)
                    self.reloading_sound_played = True
                self.inventory.weapon.reload()

        if not self.return_fire:
            self.hitbox.x += self.x_direction
            self.hitbox.y += self.y_direction
            self.position = self.hitbox.topleft  # Update image position

        self.rect.center = self.hitbox.center
        self.inventory.weapon.display_gun(self.screen, self.image_position)

        self.collisions("horizontal")
        self.collisions("vertical")


class Inventory(Bot):
    def __init__(self, player_hitpoints, armor_value):
        self.player_hitpoints = player_hitpoints
        self.armor_value = armor_value
        self.weapon = Gun("rifle")


class Item(Bot):
    def __init__(self, item_type, item_subtype, item_images, inventory_image):
        self.item_info = [item_type, item_subtype, [item_images, inventory_image]]

    def get_item_info(self):
        return self.item_info


class Armor(Item):
    def __init__(self):
        item_type = "armor"
        item_subtype = 50
        item_image = "./graphics/sprites/item_sprites/armor.png"
        inventory_image = "./graphics/sprites/item_sprites/armor_inventory.png"
        super().__init__(item_type, item_subtype, item_image, inventory_image)


class Gun(Item):
    def __init__(self, gun_type):
        self.item_type = "gun"
        self.gun_type = gun_type
        gun_types = {
            "sniper": {
                "gun_idle": "./graphics/sprites/gun_sprites/PNG/sniper_rifle_idle.png",
                "gun_firing": "./graphics/sprites/gun_sprites/PNG/sniper_rifle_idle.png",
                "gun_reloading": "./graphics/sprites/gun_sprites/PNG/sniper_rifle_idle.png",
                "inventory_image": "./graphics/sprites/gun_sprites/PNG/sniper_inventory.png",
                "bullet_capacity": 1,
                "bullet_damage": 150,
                "reload_time": 180
            },
            "rifle": {
                "gun_idle": "./graphics/sprites/gun_sprites/PNG/assault_rifle_idle.png",
                "gun_firing": "./graphics/sprites/gun_sprites/PNG/assault_rifle_idle.png",
                "gun_reloading": "./graphics/sprites/gun_sprites/PNG/assault_rifle_idle.png",
                "inventory_image": "./graphics/sprites/gun_sprites/PNG/assault_rifle_inventory.png",
                "bullet_capacity": 30,
                "bullet_damage": 28,
                "reload_time": 180
            },
            "pistol": {
                "gun_idle": "./graphics/sprites/gun_sprites/PNG/pistol_idle.png",
                "gun_firing": "./graphics/sprites/gun_sprites/PNG/pistol_idle.png",
                "gun_reloading": "./graphics/sprites/gun_sprites/PNG/pistol_idle.png",
                "inventory_image": "./graphics/sprites/gun_sprites/PNG/pistol_inventory.png",
                "bullet_capacity": 15,
                "bullet_damage": 15,
                "reload_time": 120
            },
            "shotgun": {
                "gun_idle": "./graphics/sprites/gun_sprites/PNG/shotgun_idle.png",
                "gun_firing": "./graphics/sprites/gun_sprites/PNG/shotgun_idle.png",
                "gun_reloading": "./graphics/sprites/gun_sprites/PNG/shotgun_idle.png",
                "inventory_image": "./graphics/sprites/gun_sprites/PNG/shotgun_inventory.png",
                "bullet_capacity": 6,
                "bullet_damage": 25,
                "reload_time": 300
            }
        }

        self.gun_idle = gun_types.get(self.gun_type, {}).get("gun_idle")
        self.gun_firing = gun_types.get(self.gun_type, {}).get("gun_firing")
        self.gun_reloading = gun_types.get(self.gun_type, {}).get("gun_reloading")
        self.gun_inventory = gun_types.get(self.gun_type, {}).get("inventory_image")
        self.gun_firing_sound = pygame.mixer.Sound("./audio/gun_firing.mp3")
        self.max_bullet_capacity = self.bullet_capacity = gun_types.get(self.gun_type, {}).get("bullet_capacity")
        self.bullet_damage = gun_types.get(self.gun_type, {}).get("bullet_damage")
        self.reload_time = gun_types.get(self.gun_type, {}).get("reload_time")
        self.gun_font = pygame.font.SysFont("arial", 35)
        self.bullet_capacity_text = self.gun_font.render(str(self.bullet_capacity), True, (255, 255, 255))
        self.reload_start_time = 0
        super().__init__(self.item_type, self.gun_type, [self.gun_idle, self.gun_firing, self.gun_reloading],
                         self.gun_inventory)

    def display_gun(self, screen, bot_location):
        gun_idle_png = pygame.image.load(self.gun_idle)
        screen.blit(gun_idle_png, bot_location)

    def shoot(self, screen, player_position, bullet_sprite_group, obstacle_sprites, bot_location):
        if self.bullet_capacity > 0:
            channel = pygame.mixer.Channel(7)
            channel.set_volume(0.5)
            channel.play(self.gun_firing_sound)
            self.bullet_capacity -= 1
            gun_firing_png = pygame.image.load(self.gun_firing)
            screen.blit(gun_firing_png, bot_location)
            # mouse position replaced with player position
            bullet = Bullet(player_position, gun_firing_png, obstacle_sprites, screen, None, bot_location,
                            self.bullet_damage)
            bullet_sprite_group.add(bullet)
            bullet.update()

    def reload(self):
        self.reload_start_time += 1
        print(self.reload_start_time)
        self.image = self.gun_reloading
        # make sure that they can't shoot if reloading
        self.bullet_capacity = 0
        if self.reload_start_time >= self.reload_time:
            self.bullet_capacity = self.max_bullet_capacity
            self.image = self.gun_idle
            self.reload_start_time = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, mouse_position, gun_image, obstacle_sprites, screen, custom_direction, hitbox, damage):
        super().__init__()
        self.bullet_damage = damage
        self.screen = screen
        self.obstacle_sprites = obstacle_sprites
        self.image = pygame.Surface([12, 6])
        self.image.fill((255, 204, 0))
        self.rect = self.image.get_rect()
        self.hitbox = hitbox
        self.rect.center = (self.hitbox.x + gun_image.get_width(), self.hitbox.y + 4)
        if custom_direction is None:
            # calculate custom direction:
            original_direction = pygame.math.Vector2(mouse_position[0] - self.hitbox.x,
                                                     mouse_position[1] - self.hitbox.y)
            deviation_x = random.uniform(-30, 30)
            deviation_y = random.uniform(-30, 30)
            direction = original_direction + pygame.math.Vector2(deviation_x, deviation_y)
        else:
            direction = custom_direction
        self.direction = direction.normalize()

    def update(self):
        speed = 7
        self.direction.normalize()
        self.rect.x += self.direction.x * speed
        self.rect.y += self.direction.y * speed

        if self.rect.centerx < 0 or self.rect.centerx > 1080 or self.rect.centery < 0 or self.rect.centery > 720:
            self.kill()
