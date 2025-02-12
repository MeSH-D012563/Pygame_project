import json
import random
import sys
import pygame as pg
import sqlite3
from creating_map import create_and_save_map

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


class Door(pg.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.image = pg.image.load('door_image.png').convert_alpha()  # Загрузка изображения двери
        self.image = pg.transform.scale(self.image, (100, 200))  # Масштабирование изображения
        self.rect = self.image.get_rect()
        self.rect.center = (
            screen_width // 10 * x_pos + screen_width // 10 // 2,
            screen_height // 10 * y_pos + screen_height // 10 // 2)


class KeyPart(pg.sprite.Sprite):
    def __init__(self, x_pos, y_pos, key_type):
        super().__init__()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.key_type = key_type
        self.image = pg.image.load(f'key_{key_type}.png').convert_alpha()  # Загрузка изображения ключа
        self.image = pg.transform.scale(self.image, (50, 100))  # Масштабирование изображения
        self.rect = self.image.get_rect()
        self.rect.center = (
            screen_width // 10 * x_pos + screen_width // 10 // 2,
            screen_height // 10 * y_pos + screen_height // 10 // 2)


# Класс игрока
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images_up = [pg.image.load(f'player_up_{i}.png').convert_alpha() for i in
                          range(1, 7)]  # Загрузка изображений игрока, смотрящего вверх
        self.images_down = [pg.image.load(f'player_down_{i}.png').convert_alpha() for i in
                            range(1, 7)]  # Загрузка изображений игрока, смотрящего вниз
        self.images_left = [pg.image.load(f'player_left_{i}.png').convert_alpha() for i in
                            range(1, 7)]  # Загрузка изображений игрока, смотрящего влево
        self.images_right = [pg.image.load(f'player_right_{i}.png').convert_alpha() for i in
                             range(1, 7)]  # Загрузка изображений игрока, смотрящего вправо
        self.images_up = [pg.transform.scale(image, (80, 80)) for image in
                          self.images_up]  # Масштабирование изображений
        self.images_down = [pg.transform.scale(image, (80, 80)) for image in
                            self.images_down]  # Масштабирование изображений
        self.images_left = [pg.transform.scale(image, (80, 80)) for image in
                            self.images_left]  # Масштабирование изображений
        self.images_right = [pg.transform.scale(image, (80, 80)) for image in
                             self.images_right]  # Масштабирование изображений
        self.image_index = 0
        self.image = self.images_up[self.image_index]  # Начальное изображение (смотрит вверх)
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.speed = 5
        self.is_del = [[[] for _ in range(5)] for _ in range(5)]
        self.key_parts_collected = 0  # Счетчик собранных частей ключа
        self.floors_completed = 0  # Счетчик пройденных этажей
        self.near_key = False  # Флаг для отслеживания близости к ключу
        self.animation_timer = 0
        self.animation_speed = 10  # Скорость анимации (количество кадров между сменой изображения)
        self.direction = 'up'  # Начальное направление (смотрит вверх)
        self.moving = False  # Флаг для отслеживания движения

    def update(self, trees, current_map_part, map_parts, key_parts, doors):
        self.current_map_part = current_map_part
        keys = pg.key.get_pressed()
        self.moving = False  # Сбрасываем флаг движения

        if keys[pg.K_w]:
            self.rect.y -= self.speed
            self.direction = 'up'
            self.moving = True
        if keys[pg.K_s]:
            self.rect.y += self.speed
            self.direction = 'down'
            self.moving = True
        if keys[pg.K_a]:
            self.rect.x -= self.speed
            self.direction = 'left'
            self.moving = True
        if keys[pg.K_d]:
            self.rect.x += self.speed
            self.direction = 'right'
            self.moving = True

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

        # Проверка на близость к ключу
        self.near_key = False
        for key_part in key_parts:
            if self.rect.colliderect(key_part.rect):
                self.near_key = True
                break

        # Обновление анимации только если игрок движется
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.image_index = (self.image_index + 1) % len(self.images_up)
                if self.direction == 'up':
                    self.image = self.images_up[self.image_index]
                elif self.direction == 'down':
                    self.image = self.images_down[self.image_index]
                elif self.direction == 'left':
                    self.image = self.images_left[self.image_index]
                elif self.direction == 'right':
                    self.image = self.images_right[self.image_index]

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
    doors.empty()

    map_data = map_parts[current_map_part[0]][current_map_part[1]]
    for y in map_data:
        for x in y:
            if x[0] == 3:
                if check:
                    for i in check:
                        if i[0] == x[1] and i[1] == x[2]:
                            x[0] = 0
                key_part = KeyPart(x[1], x[2], x[3])  # Передача типа ключа
                all_sprites.add(key_part)
                key_parts.add(key_part)
            elif x[0] == 4:  # Добавляем проверку для двери
                door = Door(x[1], x[2])
                all_sprites.add(door)
                doors.add(door)
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
doors = pg.sprite.Group()
player = Player()

# Загрузка всех частей карты из JSON файла
with open("map.json") as f:
    map_parts = json.load(f)

# Текущая часть карты (начальная позиция)
current_map_part = [2, 2]

# Загрузка начальной части карты
load_map_part(current_map_part, map_parts, check=player.is_del[current_map_part[0]][current_map_part[1]])


def generate_new_map():
    global map_parts, current_map_part, player
    create_and_save_map('map.json')
    with open("map.json") as f:
        map_parts = json.load(f)
    current_map_part = [2, 2]
    player.key_parts_collected = 0
    player.floors_completed += 1  # Увеличиваем счетчик пройденных этажей
    player.is_del = [[[] for _ in range(5)] for _ in range(5)]
    load_map_part(current_map_part, map_parts, check=player.is_del[current_map_part[0]][current_map_part[1]])


# Функция для отображения начального экрана
# Функция для отображения начального экрана
def show_start_screen():
    screen.fill(WHITE)
    title_text = large_font.render("Начало игры", True, BLACK)
    title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(title_text, title_rect)

    start_button = pg.Rect(screen_width // 2 - 100, screen_height // 2 - 50, 200, 50)
    pg.draw.rect(screen, GRAY, start_button)
    start_text = font.render("Старт", True, BLACK)
    start_text_rect = start_text.get_rect(center=start_button.center)
    screen.blit(start_text, start_text_rect)

    rules_button = pg.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
    pg.draw.rect(screen, GRAY, rules_button)
    rules_text = font.render("Правила", True, BLACK)
    rules_text_rect = rules_text.get_rect(center=rules_button.center)
    screen.blit(rules_text, rules_text_rect)

    results_button = pg.Rect(screen_width // 2 - 100, screen_height // 2 + 150, 200, 50)
    pg.draw.rect(screen, GRAY, results_button)
    results_text = font.render("Результаты", True, BLACK)
    results_text_rect = results_text.get_rect(center=results_button.center)
    screen.blit(results_text, results_text_rect)

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
                elif rules_button.collidepoint(event.pos):
                    show_rules_screen()
                elif results_button.collidepoint(event.pos):
                    show_results_screen()


# Функция для отображения экрана с правилами
def show_rules_screen():
    screen.fill(WHITE)
    rules_text = [
        "Цель игры: Соберите все части ключа и найдите дверь, чтобы перейти на следующий этаж.",
        "Управление:",
        "  - W: Движение вверх",
        "  - S: Движение вниз",
        "  - A: Движение влево",
        "  - D: Движение вправо",
        "  - F: Подобрать часть ключа (когда рядом с ключом)",
        "Игровой процесс:",
        "  - Игрок начинает с центральной части карты.",
        "  - Карта состоит из 25 частей (5x5), каждая часть содержит деревья, 4 ключа и дверь.",
        "  - Деревья являются препятствиями, через которые игрок не может пройти.",
        "  - Ключи находятся в разных частях карты. Соберите все части ключа, чтобы открыть дверь.",
        "  - Дверь переносит игрока на следующий этаж, где карта генерируется заново.",
        "  - Количество собранных ключей и пройденных этажей отображается в верхнем левом углу экрана.",
        "Советы:",
        "  - Внимательно исследуйте карту, чтобы найти все части ключа.",
        "  - Следите за количеством собранных ключей."
    ]

    y_offset = 50
    for line in rules_text:
        text_surface = font.render(line, True, BLACK)
        text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 40

    back_button = pg.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pg.draw.rect(screen, GRAY, back_button)
    back_text = font.render("Назад", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)

    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    waiting = False
                    show_start_screen()


# Функция для отображения экрана с результатами
def show_results_screen():
    screen.fill(WHITE)
    results_text = [
        "Результаты прошлых игроков:",
        "Ник",
        "Этажи"
    ]

    conn = sqlite3.connect('game_results.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, floors_completed FROM results ORDER BY floors_completed DESC')
    results = cursor.fetchall()
    conn.close()

    y_offset = 100
    for nickname, floors_completed in results:
        result_text = f"{nickname}: {floors_completed}"
        text_surface = font.render(result_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 40

    back_button = pg.Rect(screen_width // 2 - 100, screen_height - 100, 200, 50)
    pg.draw.rect(screen, GRAY, back_button)
    back_text = font.render("Назад", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_button.center)
    screen.blit(back_text, back_text_rect)

    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    waiting = False
                    show_start_screen()


# Функция для сохранения результата в базу данных
def save_result(nickname, floors_completed):
    conn = sqlite3.connect('game_results.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            floors_completed INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        INSERT INTO results (nickname, floors_completed)
        VALUES (?, ?)
    ''', (nickname, floors_completed))
    conn.commit()
    conn.close()


# Функция для ввода ника
def input_nickname():
    screen.fill(WHITE)
    input_text = font.render("Введите ваш ник:", True, BLACK)
    input_rect = input_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(input_text, input_rect)

    input_box = pg.Rect(screen_width // 2 - 100, screen_height // 2, 200, 50)
    pg.draw.rect(screen, GRAY, input_box)
    nickname = ''

    pg.display.flip()

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    waiting = False
                elif event.key == pg.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    nickname += event.unicode

        screen.fill(WHITE)
        screen.blit(input_text, input_rect)
        pg.draw.rect(screen, GRAY, input_box)
        text_surface = font.render(nickname, True, BLACK)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        pg.display.flip()

    return nickname


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
            if event.key == pg.K_q:  # Закрытие игры на клавишу "Q"
                running = False
            elif event.key == pg.K_f:  # Обработка нажатия кнопки "F"
                for key_part in key_parts:
                    if player.rect.colliderect(key_part.rect):
                        player.key_parts_collected += 1
                        key_part.kill()
                        player.is_del[current_map_part[0]][current_map_part[1]].append([key_part.x_pos, key_part.y_pos])

    player.update(trees, current_map_part, map_parts, key_parts, doors)
    all_sprites.update(trees, current_map_part, map_parts, key_parts, doors)

    screen.blit(background, (0, 0))  # Отображение фона
    all_sprites.draw(screen)

    # Отображение количества собранных ключей и пройденных этажей
    keys_text = font.render(f"Ключи: {player.key_parts_collected}/4", True, BLACK)
    floors_text = font.render(f"Этажи: {player.floors_completed}", True, BLACK)
    screen.blit(keys_text, (10, 10))
    screen.blit(floors_text, (10, 40))

    # Отображение подсказки, если игрок рядом с ключом
    if player.near_key:
        hint_text = font.render("Нажмите 'F', чтобы подобрать ключ", True, BLACK)
        screen.blit(hint_text, (screen_width // 2 - hint_text.get_width() // 2, screen_height - 50))

    # Проверка на взаимодействие с дверью
    for door in doors:
        if player.rect.colliderect(door.rect) and player.key_parts_collected >= 4:
            generate_new_map()
            player.key_parts_collected = 0
            player.floors_completed += 1

    pg.display.flip()

    pg.time.Clock().tick(60)

# Сохранение результата при закрытии игры
nickname = input_nickname()
save_result(nickname, player.floors_completed)

pg.quit()
sys.exit()
