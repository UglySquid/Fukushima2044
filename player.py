"""
date: june 19th, 2023
name: christine wei and william yang
description: this module contains all information about the player, including position, inventory, items, etc.
"""

# IMPORTS
import os
import random

import pygame

from settings import *

# Set working directory to current directory so that it is easier to find files
os.chdir(os.getcwd())


def import_folder(path):
    """
    description: better optimizes imports for certain variables
    :param path:
    :return surface_list:
    """
    surface_list = []

    for _, __, img_files in os.walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list


class Player(pygame.sprite.Sprite):
    """
    main player class for our game, contains information about the inventory, status, health, objectives and position
    of where the player is and also detects events and moves the player - thus encompasses Entities, Actions, and Events
    within the IDEA and ALTER frameworks
    """

    def __init__(self, position, sprite_group, obstacle_sprites, bullet_sprites, apple_sprites, screen):
        super().__init__(sprite_group)

        # alive or dead or won
        self.mouse_clicked = False
        self.dead = False
        self.won = False

        # Create screen
        self.screen = screen
        self.reload_pressed = None

        # Sounds
        self.pain_sounds = [pygame.mixer.Sound("./audio/pain_sound.wav"),
                            pygame.mixer.Sound("./audio/pain_sound_2.wav"),
                            pygame.mixer.Sound("./audio/pain_sound_3.wav")]
        self.death_sounds = [pygame.mixer.Sound("./audio/death_sound.wav"),
                             pygame.mixer.Sound("./audio/death_sound_2.wav"),
                             pygame.mixer.Sound("./audio/death_sound_3.wav")]

        # Create bullets
        self.bullet_sprites = bullet_sprites
        self.player_hitpoints = 100
        self.armor_value = 0

        # create inventory
        self.inventory = Inventory(self.player_hitpoints, self.armor_value, self.screen)
        self.apple_sprites = apple_sprites

        # Animation things
        self.player_animations = None
        self.import_assets()
        self.status = 'down'
        self.frame_index = 0

        # General stuff
        self.image = self.player_animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=position)
        self.z = LAYERS['main']

        self.clock = pygame.time.Clock()
        self.player_hitpoints = 100
        self.armor_value = 0

        self.walking_sounds_outdoors = [pygame.mixer.Sound("./audio/footstep-outdoors-1.mp3"),
                                        pygame.mixer.Sound("./audio/footstep-outdoors-2.mp3"),
                                        pygame.mixer.Sound("./audio/footstep-outdoors-3.mp3"),
                                        pygame.mixer.Sound("./audio/footstep-outdoors-4.mp3")]

        # Movement
        self.move_timer = 0
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        # Collision
        self.obstacle_sprites = obstacle_sprites

        # new method I found online to change the hitbox so that its smaller
        self.hitbox = self.rect.inflate(-4, -4)

        self.reload_pressed = None

    def import_assets(self):
        self.player_animations = {'up': [], 'down': [], 'right': [], 'left': [],
                                  'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],
                                  'up_attack': [], 'down_attack': [], 'right_attack': [], 'left_attack': []}

        for animation in self.player_animations.keys():
            full_path = "./graphics/player/" + animation
            self.player_animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.player_animations[self.status]):
            self.frame_index = 0

        self.image = self.player_animations[self.status][int(self.frame_index)]

    def keyboard_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            if self.inventory.weapon is not None:
                self.reload_pressed = True
                self.gun_reloading_sound = pygame.mixer.Sound("./audio/gun_reload.mp3")
                channel3 = pygame.mixer.Channel(2)
                channel3.play(self.gun_reloading_sound)
        if keys[pygame.K_a]:
            self.direction.x = -5
            self.status = 'left'
            self.walking_sounds_outdoors[random.randint(0, 3)].play()
        elif keys[pygame.K_d]:
            self.direction.x = 5
            self.status = 'right'
            self.walking_sounds_outdoors[random.randint(0, 3)].play()
        else:
            self.direction.x = 0

        if keys[pygame.K_w]:
            self.direction.y = -5
            self.status = 'up'
            self.walking_sounds_outdoors[random.randint(0, 3)].play()

        elif keys[pygame.K_s]:
            self.direction.y = 5
            self.status = 'down'
            self.walking_sounds_outdoors[random.randint(0, 3)].play()
        else:
            self.direction.y = 0

        if keys[pygame.K_1]:
            pass
        if pygame.mouse.get_pressed()[0]:
            # hm?
            if (self.direction.magnitude() == 0) and (self.status != 'attack'):
                self.status = self.status.split('_')[0] + '_attack'

            mouse_pos = pygame.mouse.get_pos()
            for i in range(6):
                if mouse_pos[0] in range(245 + 95 * i, 340 + 95 * i):
                    if mouse_pos[1] in range(600, 695):
                        if self.inventory.player_items[i] is not None and not self.mouse_clicked:

                            if self.inventory.player_items[i].get_item_info()[0] == "gun" and self.inventory.weapon is not None:
                                self.inventory.weapon = None
                                continue
                            self.inventory.use_inventory_item(i, self.inventory.player_items[i].get_item_info())
                            self.animation_num = 1
            # Mouse cursor is not over the inventory area
            if self.inventory.weapon is not None and (not (245 <= mouse_pos[0] <= 815 and 600 <= mouse_pos[1] <= 695)):
                if self.mouse_clicked is False:
                    self.inventory.weapon.shoot(self.screen, mouse_pos, self.bullet_sprites, self.obstacle_sprites)
            # for if you click menu button
            if True:
                pass

            # Set mouse clicked to True
            self.mouse_clicked = True
        else:
            # Mouse button is not pressed
            # Reset mouse clicked to False
            self.mouse_clicked = False

        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            for i in range(6):
                if mouse_pos[0] in range(245 + 95 * i, 340 + 95 * i):
                    if mouse_pos[1] in range(600, 695):
                        if self.inventory.player_items[i] is not None:
                            self.inventory.remove_inventory_item(i)

    def collisions(self, direction):
        for item in self.apple_sprites.sprites():
            if hasattr(item, 'is_apple'):
                if item.hitbox.colliderect(self.hitbox):
                    self.inventory.add_inventory_item(Apple())
                    item.kill()
            elif hasattr(item, 'is_armor'):
                if item.hitbox.colliderect(self.hitbox):
                    self.inventory.add_inventory_item(Apple())
                    item.kill()
        for sprite in self.bullet_sprites.sprites():
            if sprite.rect.colliderect(self.image_position):
                channel5 = pygame.mixer.Channel(4)
                channel5.play(self.pain_sounds[random.randint(0, 2)])
                if self.inventory.armor_value == 0:
                    self.inventory.player_hitpoints -= sprite.bullet_damage
                else:
                    self.inventory.armor_value -= sprite.bullet_damage
                    if self.inventory.armor_value < 0:
                        self.inventory.player_hitpoints += self.inventory.armor_value
                        self.inventory.armor_value = 0
                sprite.kill()

        for sprite in self.obstacle_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal":
                        # moving right
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        # moving left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction == "vertical":
                        # moving down
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        # moving up
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def get_status(self):
        # when player is not moving
        if (self.direction.magnitude() == 0) and ('attack' not in self.status):
            self.status = self.status.split('_')[0] + '_idle'

    def get_hitpoints(self):
        return self.player_hitpoints

    def move(self, dt):
        # Make sure vector direction is always 1
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        # Horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collisions('horizontal')

        # Vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collisions('vertical')

    def update(self, dt, bullet_sprites, player_position, bot_group, actions):
        if self.inventory.weapon and self.reload_pressed is not None:
            if self.inventory.weapon.bullet_capacity != self.inventory.weapon.max_bullet_capacity:
                self.inventory.weapon.reload()
            else:
                self.reload_pressed = None
        if self.inventory.player_hitpoints <= 0:
            channel6 = pygame.mixer.Channel(5)
            channel6.play(self.death_sounds[random.randint(0, 2)])
            self.dead = True
        if self.inventory.check_win_condition():
            self.won = True

        if self.inventory.weapon and self.reload_pressed is not None:
            if self.inventory.weapon.bullet_capacity != self.inventory.weapon.max_bullet_capacity:
                self.inventory.weapon.reload()
            else:
                self.reload_pressed = None

        # Check keyboard input
        self.keyboard_input()
        self.get_status()

        self.move(dt)
        self.animate(dt)

        self.rect.center = self.hitbox.center
        self.inventory.render_player_items(actions, bot_group)

        # draws bullet sprites
        self.bullet_sprites.draw(self.screen)
        self.bullet_sprites.update()


class Inventory(Player):
    def __init__(self, player_hitpoints, armor_value, screen):
        self.won = False
        self.screen = screen
        self.player_hitpoints = player_hitpoints
        self.hp_bars = pygame.transform.scale(pygame.image.load("./graphics/UI/health_bar.png"), (333, 45))
        self.hp_bars_bg = pygame.Surface((333, 45))
        self.hp_bars_bg.fill((64, 64, 64))
        self.quest_bar_bg = pygame.transform.scale(pygame.image.load("./graphics/UI/quest_completion_bar.png"),
                                                   (181, 30))
        self.objective_background_bar = pygame.transform.scale(
            pygame.image.load("./graphics/sprites/item_sprites/inventory_back.png"), (270, 100))
        self.objective_font = pygame.font.SysFont("Arial", 20)
        self.objective_text = self.objective_font.render(" Objective: Kill 10 AI", True, (255, 255, 255))
        self.objective_text_2 = self.objective_font.render(" Objective: Kill 20 AI, Get Armor", True, (255, 255, 255))
        self.armor_value = armor_value
        self.player_items = [Apple(), Gun("shotgun"), Gun("rifle"), Gun("sniper"), Gun("pistol"), Armor()]
        self.inventory_sprite = pygame.transform.scale(
            pygame.image.load("./graphics/sprites/item_sprites/inventory_back.png"), (80, 80))
        self.weapon = None

    def check_win_condition(self):
        return self.won

    def add_inventory_item(self, item):
        for inventory_slot in range(len(self.player_items)):
            if self.player_items[inventory_slot] is None:
                # item should be an object
                self.player_items[inventory_slot] = item
            else:
                pass

    def remove_inventory_item(self, item_pos):
        self.player_items[item_pos] = None

    def use_inventory_item(self, item_pos, item_type):
        # item_type should be a 2 item list with the first one being the general type, and the second being specific
        # value
        if item_type[0] == "heal":
            self.player_hitpoints += item_type[1]
            if self.player_hitpoints > 100:
                self.player_hitpoints = 100
            self.remove_inventory_item(item_pos)
            # remove inventory item
        elif item_type[0] == "armor":
            self.armor_value += item_type[1]
            if self.armor_value > item_type[1]:
                self.armor_value = item_type[1]
            self.remove_inventory_item(item_pos)
        elif item_type[0] == "gun":
            self.weapon = self.player_items[item_pos]

        else:
            pass

    def unequip_gun(self):
        self.weapon = None

    def render_player_items(self, actions, bot_group):
        inventory_x = 150
        for i in range(6):
            inventory_x += 95
            self.screen.blit(self.inventory_sprite, (inventory_x, 600))
        inventory_x = 253
        for item in self.player_items:
            if item is not None:
                inventory_image = pygame.image.load(item.get_item_info()[2][1])
                if item.get_item_info()[0] == "armor":
                    self.screen.blit(inventory_image, (inventory_x + 12, 620))
                else:
                    self.screen.blit(inventory_image, (inventory_x, 607))
            inventory_x += 95
        if self.weapon is not None:
            self.weapon.display_gun(self.screen)

        # calculate armor and HP bar
        # Calculate the length of the health and armor bars based on player's hit points
        health_length = int((self.player_hitpoints / 100) * 333)
        armor_length = int((self.armor_value / 100) * 333)

        # Create the health value and armor bar based on the calculated lengths
        if health_length > 0:
            health_value_bar = pygame.Surface((health_length, 22))
        else:
            health_value_bar = pygame.Surface((0, 22))
        health_value_bar.fill((0, 255, 0))  # Green color

        armor_value_bar = pygame.Surface((armor_length, 22))
        armor_value_bar.fill((70, 130, 180))  # Cyan color

        # Render the health and armor bars on the screen
        self.screen.blit(self.hp_bars_bg, (356, 30))
        self.screen.blit(health_value_bar, (356, 30))
        self.screen.blit(armor_value_bar, (356, 30 + 22))
        self.screen.blit(self.hp_bars, (356, 30))

        if actions["Level1"]:
            objective_text = self.objective_text
            total_kills = 10
            has_armor = 0
        else:
            objective_text = self.objective_text_2
            total_kills = 20
            has_armor = 1
        for item in self.player_items:
            if item is not None:
                if item.get_item_info()[0] == "armor":
                    has_armor = 0

        quest_completion_amount = (total_kills - len(bot_group)) / (total_kills + has_armor)
        quest_completion_bar = pygame.Surface((quest_completion_amount * 181, 30))
        if quest_completion_amount == 1:
            self.won = True
        quest_completion_bar.fill((0, 255, 0))
        self.screen.blit(self.objective_background_bar, (750, 30))
        self.screen.blit(objective_text, (762, 50))
        self.screen.blit(quest_completion_bar, (796, 90))
        self.screen.blit(self.quest_bar_bg, (795, 90))


class Item(Player):
    def __init__(self, item_type, item_subtype, item_images, inventory_image):
        self.item_info = [item_type, item_subtype, [item_images, inventory_image]]

    def get_item_info(self):
        return self.item_info


class Armor(Item):
    def __init__(self):
        item_type = "armor"
        item_subtype = 50
        item_image = "./graphics/sprites/item_sprites/armor.png"
        inventory_image = "./graphics/sprites/item_sprites/armor.png"
        super().__init__(item_type, item_subtype, item_image, inventory_image)


class Apple(Item):
    def __init__(self):
        item_type = "heal"
        item_subtype = 20
        item_image = "./graphics/sprites/item_sprites/apple.png"
        inventory_image = "./graphics/sprites/item_sprites/apple_inventory.png"
        super().__init__(item_type, item_subtype, item_image, inventory_image)


class Gun(Item):
    def __init__(self, gun_type):
        self.item_type = "gun"
        self.gun_type = gun_type
        self.gun_firing_sound = pygame.mixer.Sound("./audio/gun_firing.mp3")
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
        self.bullet_capacity = gun_types.get(self.gun_type, {}).get("bullet_capacity")
        self.max_bullet_capacity = self.bullet_capacity
        self.bullet_damage = gun_types.get(self.gun_type, {}).get("bullet_damage")
        self.reload_time = gun_types.get(self.gun_type, {}).get("reload_time")
        self.gun_font = pygame.font.SysFont("arial", 35)
        self.bullet_capacity_text = self.gun_font.render(str(self.bullet_capacity), True, (255, 255, 255))
        self.reload_start_time = 0
        super().__init__(self.item_type, self.gun_type, [self.gun_idle, self.gun_firing, self.gun_reloading],
                         self.gun_inventory)

    def display_gun(self, screen):
        """
        Displays the gun on the screen beside the player
        :param screen:
        :return:
        """
        gun_name_text = self.gun_font.render(self.gun_type, True, (255, 255, 255))
        bullet_count_text = self.gun_font.render(str(self.bullet_capacity), True, (255, 255, 255))
        forward_slash = self.gun_font.render("/", True, (255, 255, 255))
        gun_idle_png = pygame.image.load(self.gun_idle)
        screen.blit(gun_idle_png, (555, 364))
        screen.blit(gun_name_text, (50, 550))
        screen.blit(bullet_count_text, (35, 590))
        screen.blit(forward_slash, (67, 590))
        screen.blit(self.bullet_capacity_text, (75, 590))

    def shoot(self, screen, mouse_position, bullet_sprite_group, obstacle_sprites):
        """
        When this method is run and when the player has bullets, it will shoot bullets and play shooting sound
        :param screen:
        :param mouse_position:
        :param bullet_sprite_group:
        :param obstacle_sprites:
        :return:
        """
        if self.bullet_capacity > 0:
            channel2 = pygame.mixer.Channel(1)
            channel2.play(self.gun_firing_sound)
            self.bullet_capacity -= 1

            gun_firing_png = pygame.image.load(self.gun_firing)
            screen.blit(gun_firing_png, (555, 364))
            if self.gun_type == "shotgun":
                for i in range(3):
                    if i == 0:  # Deviated bullets for spread effect
                        deviation = 75
                        # Deviation for y-component
                        bullet_direction = pygame.Vector2(mouse_position[0] - 555 + deviation,
                                                          mouse_position[1] - 364 + deviation)
                        bullet = Bullet(mouse_position, gun_firing_png, obstacle_sprites, screen, bullet_direction,
                                        (555, 364), self.bullet_damage)
                    elif i == 2:
                        deviation = 45  # Deviation for x-component
                        # Deviation for y-component
                        bullet_direction = pygame.Vector2(mouse_position[0] - 555 - deviation,
                                                          mouse_position[1] - 364 - deviation)
                        bullet = Bullet(mouse_position, gun_firing_png, obstacle_sprites, screen, bullet_direction,
                                        (555, 364), self.bullet_damage)
                    else:  # Center bullet, no deviation
                        bullet = Bullet(mouse_position, gun_firing_png, obstacle_sprites, screen, None, (555, 364),
                                        self.bullet_damage)
                    bullet_sprite_group.add(bullet)
                    bullet.update()
            else:
                bullet = Bullet(mouse_position, gun_firing_png, obstacle_sprites, screen, None, (555, 364),
                                self.bullet_damage)
                bullet_sprite_group.add(bullet)
                bullet.update()

    def reload(self):
        # Allows player to reload gun
        self.reload_start_time += 1
        self.image = self.gun_reloading
        # Makes sure that they can't shoot if they are reloading
        self.bullet_capacity = 0
        if self.reload_start_time >= self.reload_time:
            self.bullet_capacity = self.max_bullet_capacity  # refill the magazine after reload
            self.image = self.gun_idle
            self.reload_start_time = 0


class Bullet(pygame.sprite.Sprite):
    """
    Bullet class, called everytime the player shoots
    """
    def __init__(self, mouse_position, gun_image, obstacle_sprites, screen, custom_direction, hitbox, damage):
        super().__init__()
        self.bullet_damage = damage
        self.screen = screen
        self.obstacle_sprites = obstacle_sprites
        self.image = pygame.Surface([12, 6])
        self.image.fill((255, 204, 0))
        self.rect = self.image.get_rect()
        self.hitbox = hitbox
        self.rect.center = (self.hitbox[0] + gun_image.get_width() - 10, self.hitbox[1] + gun_image.get_height() - 20)
        if custom_direction is None:
            direction = pygame.math.Vector2(mouse_position[0] - self.hitbox[0], mouse_position[1] - self.hitbox[1])
        else:
            direction = custom_direction
        self.direction = direction.normalize()

    def update(self):
        speed = 7.0
        self.direction.normalize()
        self.rect.x += self.direction.x * speed
        self.rect.y += self.direction.y * speed

        if self.rect.centerx < 0 or self.rect.centerx > 1080 or self.rect.centery < 0 or self.rect.centery > 720:
            self.kill()
