import pygame
import os
import random
from pygame import mixer


# Init fonts we use on-screen
pygame.font.init()

# Set main window
WIDTH, HEIGHT = 1000, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GNFOS: vol. II")

# Enemy sprites
ENEMY_DEMON = pygame.image.load(os.path.join("assets", "revenant_one.png"))
ENEMY_DEMON_TWO = pygame.image.load(os.path.join("assets", "cacodemon_2.png"))
ENEMY_BOSS = pygame.image.load(os.path.join("assets", "baron_boss.png"))
# Player sprite
PLAYER_SPRITE = pygame.image.load(os.path.join("assets", "doomguy.gif"))
# Ammo sprites
ENEMY_AMMO = pygame.image.load(os.path.join("assets", "fireball_demon.png"))
BOSS_AMMO = pygame.image.load(os.path.join("assets", "anime_girl.png"))
PLAYER_AMMO = pygame.image.load(os.path.join("assets", "bullet_one.png"))

# Background
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_4.jpg")), (WIDTH, HEIGHT))
# Background music
pygame.mixer.init()
mixer.music.load(os.path.join("assets", "Doot_eternal.MP3"))
mixer.music.set_volume(0.08)
mixer.music.play(-1)


class Ammo:
    def __init__(self, x, y, img):
        self.x = x
        self. y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, bullet_velocity):
        self.x += bullet_velocity

    def off_screen(self, width):
        return not(width > self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Objectoid:
    COOLDOWN = 60

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.obj_img = None
        self.ammo_img = None
        self.ammos = []
        self.cooldown_counter = 0

    def draw(self, window):
        window.blit(self.obj_img, (self.x, self.y))
        for ammo in self.ammos:
            ammo.draw(window)

    def move_ammos(self, bullet_velocity, object):
        self.cooldown()
        for ammo in self.ammos:
            ammo.move(bullet_velocity)
            if ammo.off_screen(WIDTH):
                self.ammos.remove(ammo)
            elif ammo.collision(object):
                object.health -= 10
                self.ammos.remove(ammo)

    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Ammo(self.x, self.y + 25, self.ammo_img)
            self.ammos.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.obj_img.get_width()

    def get_height(self):
        return self.obj_img.get_height()


class Player(Objectoid):
    def __init__(self, x, y, health=100):
        super(Player, self).__init__(x, y, health)
        self.obj_img = PLAYER_SPRITE
        self.ammo_img = PLAYER_AMMO
        self.mask = pygame.mask.from_surface(self.obj_img)
        self.max_health = health

    def move_ammos(self, bullet_velocity, enemies):
        self.cooldown()
        for ammo in self.ammos:
            ammo.move(bullet_velocity)
            if ammo.off_screen(WIDTH):
                self.ammos.remove(ammo)
            else:
                for enemy in enemies:
                    if ammo.collision(enemy):
                        enemies.remove(enemy)
                        if ammo in self.ammos:
                            self.ammos.remove(ammo)

    def ammo_bosses(self, bullet_velocity, bosses):
        self.cooldown()
        for ammo in self.ammos:
            ammo.move(bullet_velocity)
            if ammo.off_screen(WIDTH):
                self.ammos.remove(ammo)
            else:
                for boss in bosses:
                    if ammo.collision(boss):
                        if ammo in self.ammos:
                            self.ammos.remove(ammo)
                            boss.health -= 10
                            if boss.health == 0:
                                bosses.remove(boss)

    def draw(self, window):
        super(Player, self).draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.obj_img.get_height() + 10,
                                               self.obj_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.obj_img.get_height() + 10,
                                               self.obj_img.get_width() * (1 - (self.max_health - self.health)/self.max_health), 10))


class Enemy(Objectoid):
    COLOR_MAP = {
        "caco": (ENEMY_DEMON, ENEMY_AMMO),
        "revenant": (ENEMY_DEMON_TWO, ENEMY_AMMO),
        }

    def __init__(self, x, y, color, health=100):
        super(Enemy, self).__init__(x, y, health)
        self.obj_img, self.ammo_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.obj_img)

    def move(self, enemy_velocity):
        self.x += enemy_velocity

    def shoot(self):
        if self.cooldown_counter == 0:
            ammo = Ammo((self.x - int(self.obj_img.get_width()/2)), self.y, self.ammo_img)
            self.ammos.append(ammo)
            self.cooldown_counter = 1


class Boss(Objectoid):
    def __init__(self, x, y, health=200):
        super(Boss, self).__init__(x, y, health)
        self.obj_img = ENEMY_BOSS
        self.ammo_img = BOSS_AMMO
        self.mask = pygame.mask.from_surface(self.obj_img)
        self.max_health = health

    def move(self, enemy_velocity):
        self.x += enemy_velocity

    def draw(self, window):
        super(Boss, self).draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.obj_img.get_height() + 10,
                                               self.obj_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.obj_img.get_height() + 10,
                                               self.obj_img.get_width() * (1 - (self.max_health - self.health)/self.max_health), 10))


def collide(obj_one, obj_two):
    offset_x = obj_two.x - obj_one.x
    offset_y = obj_two.y - obj_one.y
    return obj_one.mask.overlap(obj_two.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 0
    main_font = pygame.font.SysFont("comicsans", 40)

    lose_font = pygame.font.SysFont("comicsans", 70)
    lose = False
    lose_count = 0

    player_velocity = 5
    player = Player(450, 300)

    enemies = []
    wave_len = 4

    bosses = []
    bosses_wave_len = 0

    enemy_velocity = -1

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))
        # text
        lives_label = main_font.render(f"Demons got to Earth: {lives}", True, (0, 255, 0))
        level_label = main_font.render(f"Level: {level}", True, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (HEIGHT - level_label.get_height(), 10))

        for enemy in enemies:  # cycle to draw enemies on screen
            enemy.draw(WIN)

        for boss in bosses:    #cycle to draw bosses on screen
            boss.draw(WIN)

        player.draw(WIN)

        if lose:
            lose_label = lose_font.render(f"YOU FAILED!", True, (255, 0, 0))
            WIN.blit(lose_label, (WIDTH/2 - lose_label.get_width()/2,
                                  (HEIGHT - lose_label.get_height())/2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives == 5:
            lose = True
            lose_count += 1

        if player.health <= 0:
            lose = True
            lose_count += 1

        if lose:
            if lose_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0 and len(bosses) == 0:
            level += 1

            if level % 5 != 0:
                wave_len += 2
                for i in range(wave_len):
                    enemy = Enemy(random.randrange(WIDTH + 100, WIDTH + 300), random.randrange(50, HEIGHT - 100), #chooses position
                                  random.choice(["caco", "revenant"])) #chooses type of enemy
                    enemies.append(enemy)

            else:
                bosses_wave_len += 1
                for i in range(bosses_wave_len):
                    boss = Boss(random.randrange(WIDTH + 200, 1500), random.randrange(50, HEIGHT - 100))
                    bosses.append(boss)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for enemy in enemies:
            enemy.move(enemy_velocity)
            enemy.move_ammos(bullet_velocity=-4, object=player)

            if random.randrange(1, 5*FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.x + enemy.get_width() < 0:
                lives += 1
                enemies.remove(enemy)

        for boss in bosses:
            boss.move(enemy_velocity)
            boss.move_ammos(bullet_velocity=-5, object=player)

            if random.randrange(1, 5*FPS) == 1:
                boss.shoot()

            if collide(boss, player):
                player.health -= 100
                bosses.remove(boss)

            elif boss.x + boss.get_width() < 0:
                lives += 2
                bosses.remove(boss)

        player.move_ammos(bullet_velocity=4, enemies=enemies)
        player.ammo_bosses(bullet_velocity=0, bosses=bosses)

        # CONTROL KEYS FOR PLAYER
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0:  # move left
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH:  # move right
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0:  # move up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 15 < HEIGHT:  # move down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()


def intro():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    FPS = 60
    clock = pygame.time.Clock()

    while run:
        WIN.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press the mouse button to RIP AND TEAR.", True, (255, 0, 0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, (HEIGHT - title_label.get_height())/2))
        pygame.display.update()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


intro()
