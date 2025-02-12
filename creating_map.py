import json
import random


def create_and_save_map(filename):
    map_dat = []
    key_parts_positions = []
    door_position = None

    # Генерация 4 случайных позиций для частей ключа на всей карте
    while len(key_parts_positions) < 4:
        part_pos = (random.randint(0, 4), random.randint(0, 4), random.randint(0, 9), random.randint(0, 9))
        if part_pos not in key_parts_positions:
            key_parts_positions.append(part_pos)

    # Генерация случайной позиции для двери
    while door_position is None:
        door_pos = (random.randint(0, 4), random.randint(0, 4), random.randint(0, 9), random.randint(0, 9))
        if door_pos not in key_parts_positions:
            door_position = door_pos

    for i in range(5):
        rrow = []
        for j in range(5):
            map_data = []
            y_pos = 0
            x_pos = 0
            for y in range(10):
                row = []
                for x in range(10):
                    if (i, j, x, y) in key_parts_positions:
                        key_type = key_parts_positions.index((i, j, x, y)) + 1  # Определение типа ключа
                        row.append([3, x, y, key_type])  # Добавление типа ключа
                    elif (i, j, x, y) == door_position:
                        row.append([4, x, y])  # Добавляем дверь
                    elif not (x_pos in list(range(4, 6)) and y_pos in list(range(4, 6))):
                        ran = random.choice([0, 0, 0, 0, 0, 1])  # Уменьшаем вероятность генерации деревьев
                        if ran == 1:
                            row.append([1, x, y, random.randint(100, 120)])
                        else:
                            row.append([0, x, y])
                    else:
                        row.append([0, x, y])
                    x_pos += 1
                map_data.append(row)
                y_pos += 1
                x_pos = 0
            rrow.append(map_data)
        map_dat.append(rrow)

    with open(filename, 'w') as file:
        json.dump(map_dat, file)


# Название карты
map_filename = 'map.json'

# Создание и сохранение карты
create_and_save_map(map_filename)