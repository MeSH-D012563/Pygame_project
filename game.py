import json
import random
import sys
import pygame as pg

# Инициализация Pygame
pg.init()

# Определение размеров экрана
screen_info = pg.display.Info()
screen_width = int(screen_info.current_w)
screen_height = int(screen_info.current_h)

# Создание окна на весь экран
screen = pg.display.set_mode((screen_width, screen_height))

# Определение цветов
WHITE = (255, 255, 255)
DARK_GREEN = (0, 100, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Инициализация шрифта
font = pg.font.Font(None, 36)
large_font = pg.font.Font(None, 72)

# Загрузка изображения фона
background_image = pg.image.load('background_image.png').convert()
background_image = pg.transform.scale(background_image, (screen_width, screen_height))

# Функция для создания фона с травой
def create_background():
    return background_image

# Создание фона
background = create_background()


class KeyPart(pg.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pg.Surface((50, 50))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (
            screen_width // 10 * x_pos + screen_width // 10 // 2,
            screen_height // 10 * y_pos + screen_height // 10 // 2)


# Класс игрока
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((50, 50))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.speed = 5
        self.is_del = [[[] for _ in range(5)] for _ in range(5)]

    def update(self, trees, current_map_part, map_parts):
        self.current_map_part = current_map_part
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.rect.y -= self.speed
        if keys[pg.K_s]:
            self.rect.y += self.speed
        if keys[pg.K_a]:
            self.rect.x -= self.speed
        if keys[pg.K_d]:
            self.rect.x += self.speed

        for tree in trees:
            if self.rect.colliderect(tree.hitbox):
                if keys[pg.K_w]:
                    self.rect.y += self.speed
                if keys[pg.K_s]:
                    self.rect.y -= self.speed
                if keys[pg.K_a]:
                    self.rect.x += self.speed
                if keys[pg.K_d]:
                    self.rect.x -= self.speed

        if self.rect.left < 0:
            if current_map_part[1] > 0:
                current_map_part[1] -= 1
                self.rect.right = screen_width
                self.adjust_position(current_map_part, map_parts)
            else:
                self.rect.left = 0
        if self.rect.right > screen_width:
            if current_map_part[1] < 4:
                current_map_part[1] += 1
                self.rect.left = 0
                self.adjust_position(current_map_part, map_parts)
            else:
                self.rect.right = screen_width
        if self.rect.top < 0:
            if current_map_part[0] > 0:
                current_map_part[0] -= 1
                self.rect.bottom = screen_height
                self.adjust_position(current_map_part, map_parts)
            else:
                self.rect.top = 0
        if self.rect.bottom > screen_height:
            if current_map_part[0] < 4:
                current_map_part[0] += 1
                self.rect.top = 0
                self.adjust_position(current_map_part, map_parts)
            else:
                self.rect.bottom = screen_height

        load_map_part(current_map_part, map_parts, self.is_del[current_map_part[0]][current_map_part[1]])

    def adjust_position(self, current_map_part, map_parts):
        map_data = map_parts[current_map_part[0]][current_map_part[1]]
        player_x = self.rect.centerx // (screen_width // 10)
        player_y = self.rect.centery // (screen_height // 10)

        if map_data[player_y][player_x][0] == 1:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    new_x = player_x + dx
                    new_y = player_y + dy
                    if 0 <= new_x < 10 and 0 <= new_y < 10 and map_data[new_y][new_x][0] == 0:
                        self.rect.centerx = (new_x + 0.5) * (
                                screen_width // 10)
                        self.rect.centery = (new_y + 0.5) * (
                                screen_height // 10)
                        return


class Tree(pg.sprite.Sprite):
    def __init__(self, x_pos, y_pos, rand_sqwer):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pg.image.load('tree_image.png').convert_alpha()  # Загрузка изображения дерева
        self.image = pg.transform.scale(self.image, (rand_sqwer, rand_sqwer))  # Масштабирование изображения
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 10 * x_pos + rand_sqwer // 2,
                            screen_height // 10 * y_pos + rand_sqwer // 2)
        self.hitbox = self.rect.inflate(-rand_sqwer // 2, -rand_sqwer // 2)


# Функция для загрузки части карты
def load_map_part(current_map_part, map_parts, check=[]):
    all_sprites.empty()
    trees.empty()
    key_parts.empty()

    map_data = map_parts[current_map_part[0]][current_map_part[1]]
    for y in map_data:
        for x in y:
            if x[0] == 3:
                if check:
                    for i in check:
                        if i[0] == x[1] and i[1] == x[2]:
                            x[0] = 0
                key_part = KeyPart(x[1], x[2])
                all_sprites.add(key_part)
                key_parts.add(key_part)
    all_sprites.add(player)
    for y in map_data:
        for x in y:
            if x[0] == 1:
                tree = Tree(x[1], x[2], x[3])
                all_sprites.add(tree)
                trees.add(tree)


# Создание группы спрайтов и добавление игрока
all_sprites = pg.sprite.Group()
trees = pg.sprite.Group()
key_parts = pg.sprite.Group()
player = Player()

# Загрузка всех частей карты из JSON файла
with open("map.json") as f:
    map_parts = json.load(f)

# Текущая часть карты (начальная позиция)
current_map_part = [2, 2]

# Загрузка начальной части карты
load_map_part(current_map_part, map_parts, check=player.is_del[current_map_part[0]][current_map_part[1]])


# Функция для отображения катсцены
def show_cutscene(image_paths):
    for image_path in image_paths:
        cutscene_image = pg.image.load(image_path)
        cutscene_image = pg.transform.scale(cutscene_image, (
            screen_width, screen_height))
        screen.blit(cutscene_image, (0, 0))

        text_background = pg.Surface((screen_width // 3, 50),
                                     pg.SRCALPHA)
        text_background.fill((255, 255, 255, 128))
        text_background_rect = text_background.get_rect(
            bottomright=(screen_width - 10, screen_height - 10))
        screen.blit(text_background, text_background_rect)

        text = font.render("Для пролистывания нажмите Enter", True, BLACK)
        text_rect = text.get_rect(center=text_background_rect.center)
        screen.blit(text, text_rect)

        pg.display.flip()
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    waiting = False


# Функция для отображения начального экрана
def show_start_screen():
    screen.fill(WHITE)
    title_text = large_font.render("Начало игры", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(title_text, title_rect)

    start_button = pg.Rect(screen_width // 2 - 100, screen_height // 2, 200,
                           50)
    pg.draw.rect(screen, GRAY, start_button)
    start_text = font.render("Старт", True, BLACK)
    start_text_rect = start_text.get_rect(center=start_button.center)
    screen.blit(start_text, start_text_rect)

    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    waiting = False


# Основной игровой цикл
running = True
cutscene_triggered = False
cutscene_shown = False
alpha_value = 0
fade_speed = 5

# Отображение начального экрана
show_start_screen()

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_F11:
                running = False

    player.update(trees, current_map_part, map_parts)
    all_sprites.update(trees, current_map_part, map_parts)

    screen.blit(background, (0, 0))  # Отображение фона
    all_sprites.draw(screen)

    if cutscene_triggered:
        alpha_value += fade_speed
        if alpha_value >= 255:
            alpha_value = 255
            show_cutscene(["1.jpeg", "2.jpeg", "3.jpeg"])
            cutscene_shown = True
            cutscene_triggered = False

    pg.display.flip()

    pg.time.Clock().tick(60)

pg.quit()
sys.exit()
