import pygame
import os
import player
import sprites

pygame.init()
os.chdir(os.getcwd())

# ENTITIES
font = pygame.font.Font('graphics/Retro Gaming.ttf', 24)


class Button:
    def __init__(self, screen, txt, pos):
        self.text = txt
        self.pos = pos
        self.screen = screen

        self.button = pygame.image.load("graphics/UI/button1.png").convert_alpha()
        self.button_rect = self.button.get_rect()
        self.button_rect.centerx = self.pos[0]
        self.button_rect.centery = self.pos[1]

        self.big_button = pygame.transform.scale(self.button,
                                                 (self.button.get_width() * 1.1, self.button.get_height() * 1.1))
        self.big_button_rect = self.big_button.get_rect()
        self.big_button_rect.centerx = self.pos[0]
        self.big_button_rect.centery = self.pos[1]

    def draw(self):
        if self.button_rect.collidepoint(pygame.mouse.get_pos()):
            self.screen.blit(self.button, self.button_rect)
        else:
            self.screen.blit(self.button, self.button_rect)

        text = font.render(self.text, True, 'black')
        text_rect = text.get_rect(center=self.button_rect.center)
        self.screen.blit(text, text_rect)

    def press(self):
        if self.button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            return True
        else:
            return False


class State:
    def __init__(self, game):
        self.game = game
        self.prev_state = None

    def update(self, delta_time, actions):
        pass

    def render(self, surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()


class Title(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)

        pygame.mixer.init()
        pygame.mixer.music.load("audio/title_bg.mp3")
        pygame.mixer.music.play(loops=-1)

        self.background = pygame.image.load('graphics/fuki4.png')
        self.title_text = pygame.image.load('./graphics/UI/title_text.png')
        self.title_text = pygame.transform.scale(self.title_text,
                                                 (
                                                     self.title_text.get_width() * 0.7,
                                                     self.title_text.get_height() * 0.7))

    def update(self, delta_time, actions):
        if actions["Level1"]:
            new_state = Level1(self.game, actions)
            new_state.enter_state()
        if actions["Level2"]:
            new_state = Level2(self.game, actions)
            new_state.enter_state()
        if actions["return"]:
            new_state = HowTo(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, screen):
        # Draw manu
        screen.fill((114, 117, 27))
        screen.blit(self.background, (0, 0))
        screen.blit(self.title_text, (70, 50))

        # Level 1
        level1_btn = Button(screen, "LEVEL 1", [screen.get_width() / 2, screen.get_height() / 2 + 50])
        level1_btn.draw()

        # Level 2
        level2_btn = Button(screen, "LEVEL 2", [screen.get_width() / 2, screen.get_height() / 2 + 150])
        level2_btn.draw()

        # How to play button
        how_btn = Button(screen, "HOW TO", [screen.get_width() / 2, screen.get_height() / 2 + 250])
        how_btn.draw()

        # Events
        if level1_btn.press():
            self.game.actions["Level1"] = True
        if level2_btn.press():
            self.game.actions["Level2"] = True
        if how_btn.press():
            print("Hi")
            self.game.actions["return"] = True


class HowTo(State):
    def __init__(self, game):
        self.game = game

        self.screen = self.game.screen
        State.__init__(self, game)

        # Load how to image
        self.image = pygame.image.load('./graphics/UI/howto.png')
        self.rect = self.image.get_rect()
        self.rect.centery = game.screen.get_height()/2
        self.rect.centerx = game.screen.get_width()/2 + 100

        # Resume game / exit menu Button
        self.close_btn = Button(self.screen, "CLOSE", [150, self.screen.get_height() / 2 - 50])

    def update(self, delta_time, actions):
        if actions["return"]:
            self.exit_state()

        self.game.reset_keys()

    def render(self, screen):
        screen.fill((114, 117, 27))

        # Render the how to image
        screen.blit(self.image, self.rect)

        # Close the how to play guide
        self.close_btn.draw()

        # Check for events
        if self.close_btn.press():
            self.game.actions["return"] = True


class GameOver(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)

        pygame.mixer.init()
        pygame.mixer.music.load("audio/title_bg.mp3")
        pygame.mixer.music.play(loops=-1)

        self.background = pygame.image.load('graphics/fuki4.png')
        self.gameover_text = pygame.image.load('./graphics/UI/gameover.png')
        self.gameover_text = pygame.transform.scale(self.gameover_text,
                                                    (self.gameover_text.get_width() * 0.7,
                                                     self.gameover_text.get_height() * 0.7))

    def update(self, delta_time, actions):
        if actions["Title"]:
            new_state = Title(self.game)
            new_state.enter_state()

        self.game.reset_keys()

    def render(self, screen):
        # Draw manu
        screen.fill((114, 117, 27))
        screen.blit(self.background, (0, 0))
        screen.blit(self.gameover_text, (100, 100))

        # Restart
        menu_btn = Button(screen, "RESTART", [150, screen.get_height() / 2 - 50])
        menu_btn.draw()

        # Quit
        quit_btn = Button(screen, "QUIT", [150, screen.get_height() / 2 + 50])
        quit_btn.draw()

        # Events
        if menu_btn.press():
            self.game.actions["Title"] = True
        if quit_btn.press():
            self.game.keepGoing = False


class GameWon(State):
    """
    renders menu when game has been won by player - triggered by an event
    """

    def __init__(self, game):
        self.game = game
        State.__init__(self, game)

        pygame.mixer.init()
        pygame.mixer.music.load("audio/title_bg.mp3")
        pygame.mixer.music.play(loops=-1)

        self.background = pygame.image.load('graphics/fuki4.png')
        self.gameover_text = pygame.image.load('./graphics/UI/you_won.png')
        self.gameover_text = pygame.transform.scale(self.gameover_text,
                                                    (self.gameover_text.get_width() * 0.7,
                                                     self.gameover_text.get_height() * 0.7))

    def update(self, delta_time, actions):
        if actions["Title"]:
            new_state = Title(self.game)
            new_state.enter_state()

        self.game.reset_keys()

    def render(self, screen):
        # Draw manu
        screen.fill((114, 117, 27))
        screen.blit(self.background, (0, 0))
        screen.blit(self.gameover_text, (100, 100))

        # Back to Main Menu
        menu_btn = Button(screen, "MAIN MENU", [150, screen.get_height() / 2 - 50])
        menu_btn.draw()

        # Quit
        quit_btn = Button(screen, "QUIT", [150, screen.get_height() / 2 + 50])
        quit_btn.draw()

        # Events
        if menu_btn.press():
            self.game.actions["Title"] = True
        if quit_btn.press():
            self.game.keepGoing = False


class PauseMenu(State):
    """
    renders menu when game is paused by player - triggered by an event
    """

    def __init__(self, game):
        self.game = game

        self.screen = self.game.screen
        State.__init__(self, game)

        # Resume game / exit menu Button
        self.resume_btn = Button(self.screen, "RESUME", [150, self.screen.get_height() / 2 - 50])

        # Return to main menu button
        self.title_btn = Button(self.screen, "TITLE", [150, self.screen.get_height() / 2 + 50])

        # Quit Menu Button
        self.quit_btn = Button(self.screen, "QUIT", [150, self.screen.get_height() / 2 + 150])

    def update(self, delta_time, actions):
        if actions["Title"]:
            self.exit_state()
            new_state = Title(self.game)
            new_state.enter_state()
        if actions["return"]:
            self.exit_state()

        self.game.reset_keys()

    def render(self, screen):
        # Render game screen
        self.prev_state.render(screen)

        # Render the menu
        self.resume_btn.draw()
        self.title_btn.draw()
        self.quit_btn.draw()

        # Check for events
        if self.resume_btn.press():
            self.game.actions["return"] = True
        if self.title_btn.press():
            self.game.actions["Title"] = True
        if self.quit_btn.press():
            self.game.keepGoing = False


class Level1(State):
    """
    first level of the game, starts playing music and also causes game to render in properly
    """

    def __init__(self, game, actions):
        self.game = game
        State.__init__(self, game)
        pygame.mixer.init()

        pygame.mixer.init()
        pygame.mixer.music.load("./audio/background-ambience.mp3")
        pygame.mixer.music.play(loops=-1)

        self.screen = game.screen
        self.clock = pygame.time.Clock()
        self.sprites = sprites.Sprites(self.screen, actions)
        self.cursor_image = pygame.image.load('./graphics/UI/crosshair.png')
        self.cursor_image = pygame.transform.scale(self.cursor_image, (50, 50))

    def print_crosshair(self):
        cursor_pos = pygame.mouse.get_pos()
        cursor_center_x = cursor_pos[0] - 11
        cursor_center_y = cursor_pos[1] - 11
        pygame.mouse.set_visible(False)
        return cursor_center_x, cursor_center_y

    def update(self, delta_time, actions):
        # 'Events' part of ALTER framework, Action in IDEA, checks for all pause/win/lose events occurring from the game
        actions["Level1"] = True
        if actions["Pause"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        if actions["Game over"]:
            for group in [self.sprites.obstacle_sprites, self.sprites.bot_group, self.sprites.chest_group,
                          self.sprites.floor_items,
                          self.sprites.bullet_sprites]:
                for sprite in group:
                    sprite.kill()
            self.sprites.player.kill()
            new_state = GameOver(self.game)
            new_state.enter_state()
        if actions["Game won"]:
            new_state = GameWon(self.game)
            new_state.enter_state()

        self.sprites.update()

        dt = self.clock.tick() / 1000
        self.sprites.run(dt, actions)
        self.game.reset_keys()

    def render(self, screen):
        menu_btn = Button(screen, "Menu", [100, 100])
        menu_btn.button = pygame.transform.scale(menu_btn.button, (
            menu_btn.button.get_width() * 0.7, menu_btn.button.get_height() * 0.7))
        menu_btn.button_rect = menu_btn.button.get_rect()
        menu_btn.draw()

        if self.game.state_stack[0] == "Pause":
            self.screen.blit(self.cursor_image, self.print_crosshair(screen))

        # Events (Check button presses)
        if menu_btn.press():
            self.game.actions["Pause"] = True
        if self.sprites.player.dead:
            self.game.actions["Game over"] = True
        if self.sprites.player.won:
            self.game.actions["Game won"] = True

    def render_cursor(self, screen):
        self.screen.blit(self.cursor_image, self.print_crosshair(screen))


class Level2(State):
    """
    second level of the game, starts playing music and also causes game to render in properly
    """

    def __init__(self, game, actions):
        self.game = game
        State.__init__(self, game)
        pygame.mixer.init()

        pygame.mixer.init()
        pygame.mixer.music.load("./audio/background-ambience.mp3")
        pygame.mixer.music.play(loops=-1)

        self.screen = game.screen
        self.clock = pygame.time.Clock()
        self.sprites = sprites.Sprites(self.screen, actions)
        self.cursor_image = pygame.image.load('./graphics/UI/crosshair.png')
        self.cursor_image = pygame.transform.scale(self.cursor_image, (50, 50))

    def update(self, delta_time, actions):
        # 'Events' part of ALTER framework, Action in IDEA, checks for all pause/win/lose events occurring from the game
        actions["Level2"] = True
        if actions["Pause"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        if actions["Game over"]:
            for group in [self.sprites.obstacle_sprites, self.sprites.bot_group, self.sprites.chest_group,
                          self.sprites.floor_items,
                          self.sprites.bullet_sprites]:
                for sprite in group:
                    sprite.kill()
            self.sprites.player.kill()
            new_state = GameOver(self.game)
            new_state.enter_state()
        if actions["Game won"]:
            new_state = GameWon(self.game)
            new_state.enter_state()

        self.sprites.update()

        dt = self.clock.tick() / 1000
        self.sprites.run(dt, actions)
        self.game.reset_keys()

    def render(self, screen):
        menu_btn = Button(screen, "Menu", [100, 100])
        menu_btn.button = pygame.transform.scale(menu_btn.button, (
            menu_btn.button.get_width() * 0.7, menu_btn.button.get_height() * 0.7))
        menu_btn.button_rect = menu_btn.button.get_rect()
        menu_btn.draw()

        if self.game.state_stack[0] == "Pause":
            self.screen.blit(self.cursor_image, player.Player.print_crosshair(screen))

        # Events (Check button presses)
        if menu_btn.press():
            self.game.actions["Pause"] = True
        if self.sprites.player.dead:
            self.game.actions["Game over"] = True
        if self.sprites.player.won:
            self.game.actions["Game won"] = True

    def render_cursor(self, screen):
        self.screen.blit(self.cursor_image, player.Player.print_crosshair(screen))
