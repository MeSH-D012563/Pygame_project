import json
import random


# Функция для создания и сохранения карты
def create_and_save_map(filename):
    map_dat = []
    for i in range(5):
        rrow = []
        for j in range(5):
            map_data = []
            y_pos = 0
            x_pos = 0
            for y in range(10):
                row = []
                for x in range(10):
                    if not (x_pos in list(range(4, 6)) and y_pos in list(range(4, 6))):
                        ran = random.choice([0, 1, 1, 1, 3])
                        if ran == 1:
                            row.append([1, x_pos, y_pos, random.randint(100, 120)])
                        if ran == 3:
                            row.append([3, x_pos, y_pos])
                        if ran == 0:
                            row.append([0, x_pos, y_pos])
                    else:
                        row.append((0, x_pos, y_pos))
                    x_pos += 1
                map_data.append(row)
                y_pos += 1
                x_pos = 0
            rrow.append(map_data)
        map_dat.append(rrow)

    with open(filename, 'w') as file:
        json.dump(map_dat, file)

# Параметры карты
map_filename = 'map.json'

# Создание и сохранение карты
create_and_save_map(map_filename)

print(f"Карта успешно создана и сохранена в файл {map_filename}")
