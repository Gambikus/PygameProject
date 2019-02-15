import pygame
import os
import math
import sys

FPS = 60
pygame.init()
size = width, height = 448, 576
screen = pygame.display.set_mode(size)
screen.fill((0, 30, 0))
clock = pygame.time.Clock()


def rotate(img, pos, angle):
    w, h = img.get_size()
    img2 = pygame.Surface((w * 2, h * 2), pygame.SRCALPHA)
    img2.blit(img, (w - pos[0], h - pos[1]))
    return pygame.transform.rotate(img2, angle)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["МЯЧ ВЫШИБАЛА", "",
                  "Надо выбить все синие мячи",
                  "С помощью мыши выберите ",
                  "направление мяча",
                  "И запустите мяч с помощью ЛКМ.",
                  "Нажмите любую клавишу для начала"]
    intro_levels = ['Первый уровень', "Второй уровень", "Третий уровень", "Четвертый уровень"]

    fon = load_image('fon.jpg')
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.y = text_coord
        intro_rect.x = 50
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    y = text_coord + 30
    text_coord2 = 20
    level_coords = []
    for line in intro_levels:
        level_coords.append([text_coord2, y])
        for word in line.split():
            string_rendered = font.render(word, 1, pygame.Color('blue'))
            intro_rect = string_rendered.get_rect()
            intro_rect.y = y
            y += 10 + intro_rect.height
            intro_rect.x = text_coord2
            screen.blit(string_rendered, intro_rect)
        text_coord2 += font.render(word, 1, pygame.Color('blue')).get_rect().width
        level_coords[-1].append(text_coord2)
        level_coords[-1].append(y)
        text_coord2 += 15
        y = y - 20 - 2 * font.render(word, 1, pygame.Color('blue')).get_rect().height

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in level_coords:
                    if i[0] < event.pos[0] < i[2] and i[1] < event.pos[1] < i[3]:
                        return levels[level_coords.index(i)]
        pygame.display.flip()
        clock.tick(FPS)


victim_image = load_image("victimBall.png")
arrow_image = load_image("arrow.png")
arrow_image = pygame.transform.scale(arrow_image, (100, 25))
ball_image = load_image("ball.png")
all_sprites = pygame.sprite.Group()
victims = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
levels = [load_level("firstLevel"), load_level("secondLevel"), load_level("thirdLevel"), load_level("fourthLevel")]


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class HunterBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(ball_image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx, self.vy = 0, 0
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = x
        self.pos_y = y

    def changeangle(self, cos1, sin1):
        self.vx = cos1 * 25
        self.vy = sin1 * 25
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.center = (self.pos_x, self.pos_y)

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        for i in victims:
            if pygame.sprite.collide_mask(self, i):
                i.kill()

    def stop(self):
        self.prevX, self.prevY = self.vx, self.vy
        self.vx, self.vy = 0, 0

    def run(self):
        self.vx, self.vy = self.prevX, self.prevY


# class GuideArrow(pygame.sprite.Sprite):
#     def __init__(self, x, y):
#         super().__init__(all_sprites)
#         self.image = arrow_image
#         self.rect = self.image.get_rect()
#         self.rect.x = x
#         self.rect.y = y
#         self.pos = x, y
#         self.mask = pygame.mask.from_surface(self.image)
#
#     def update(self, angle):
#         self.image = pygame.transform.rotate(self.image, angle - 90)
#         self.rect = self.image.get_rect(center=self.rect.center)
#         self.rect.center = (self.pos[0], self.pos[1])
#         self.image = pygame.transform.scale(self.image, (105, 25))
#         self.rect.x = self.pos[0]
#         self.rect.y = self.pos[1]
#         print(self.rect.x, self.rect.y, self.image.get_size())


class VictimBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.add(victims)
        self.image = pygame.transform.scale(victim_image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


arrows = []


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Border(x * 64, y * 64, x * 64 + 64, y * 64)
                Border(x * 64, y * 64, x * 64, y * 64 + 64)
            elif level[y][x] == '2':
                x -= 1
                Border(x * 64, y * 64, x * 64 + 64, y * 64)
                Border(x * 64 + 64, y * 64, x * 64 + 64, y * 64 + 64)
                x += 1
            elif level[y][x] == '3':
                y -= 1
                Border(x * 64, y * 64, x * 64, y * 64 + 64)
                Border(x * 64, y * 64 + 64, x * 64 + 64, y * 64 + 64)
                y += 1
            elif level[y][x] == '4':
                x, y = x - 1, y - 1
                Border(x * 64, y * 64 + 64, x * 64 + 64, y * 64 + 64)
                Border(x * 64 + 64, y * 64, x * 64 + 64, y * 64 + 64)
                x, y = x + 1, y + 1
            elif level[y][x] == '@':
                Border(x * 64, y * 64, x * 64 + 64, y * 64)
            elif level[y][x] == '-':
                Border(x * 64, y * 64, x * 64, y * 64 + 64)
            elif level[y][x] == 'v':
                VictimBall(x * 64 + 16, y * 64 + 16)
            elif level[y][x] == 'g':
                arrows.append(HunterBall(x * 64, y * 64))
                x1, y1 = x, y
    return x1, y1


def restart():
    intro_text = ["Поздравляем, Вы прошли уровень!", "",
                  "Нажмите любую кнопку,",
                  " чтобы перейти к выбору уровня."]

    fon = load_image('fon.jpg')
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def menu():
    intro_text = ["ПАУЗА", "",
                  "НАЧАТЬ ЗАНОВО",
                  "ПРОДОЛЖИТЬ",
                  "ВЫБРАТЬ ДРУГОЙ УРОВЕНЬ"]

    buttons_coords = []
    fon = load_image('fon.jpg')
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('blue'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        if line != "ПАУЗА" and line != "":
            buttons_coords.append([10, intro_rect.top, 10 + intro_rect.width, text_coord])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in buttons_coords:
                    if i[0] <= event.pos[0] <= i[2] and i[1] <= event.pos[1] <= i[3]:
                        if buttons_coords.index(i) == 0:
                            return -1
                        elif buttons_coords.index(i) == 1:
                            for i in arrows:
                                i.run()
                            return 0
                        else:
                            return 1

        pygame.display.flip()
        clock.tick(FPS)


level = start_screen()
x, y = generate_level(level)
k = 0
numberOfBalls = 3
running = True
going = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if numberOfBalls != 0:
                sin_angle = (pos[1] - arrows[k].rect.y - arrows[k].rect.height // 2) / \
                            (((pos[1] - arrows[k].rect.y - arrows[k].rect.height // 2) ** 2 + (
                                    pos[0] - arrows[k].rect.x - arrows[k].rect.width // 2) ** 2) ** .5 + 1)
                cos_angle = (pos[0] - arrows[k].rect.x - arrows[k].rect.width // 2) / \
                            (((pos[1] - arrows[k].rect.y - arrows[k].rect.height // 2) ** 2 + (
                                    pos[0] - arrows[k].rect.x - arrows[k].rect.width // 2) ** 2) ** .5 + 1)
                arrows[k].changeangle(cos_angle, sin_angle)
                arrows.append(HunterBall(x * 64, y * 64))
                k += 1
                numberOfBalls -= 1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                for i in arrows:
                    i.stop()
                decision = menu()
                if decision == -1:
                    all_sprites = pygame.sprite.Group()
                    victims = pygame.sprite.Group()
                    horizontal_borders = pygame.sprite.Group()
                    vertical_borders = pygame.sprite.Group()
                    arrows = []
                    x, y = generate_level(level)
                    k = 0
                    numberOfBalls = 3
                elif decision == 1:
                    all_sprites = pygame.sprite.Group()
                    victims = pygame.sprite.Group()
                    horizontal_borders = pygame.sprite.Group()
                    vertical_borders = pygame.sprite.Group()
                    arrows = []
                    level = start_screen()
                    x, y = generate_level(level)
                    k = 0
                    numberOfBalls = 3
    for arrow in arrows:
        if arrow.vx != 0:
            arrow.update()
    all_sprites.draw(screen)
    font = pygame.font.Font(None, 30)
    string_rendered = font.render("Мячей: " + str(numberOfBalls), 1, pygame.Color('blue'))
    intro_rect = string_rendered.get_rect()
    intro_rect.y = 64 * 7 + 32
    intro_rect.x = 10
    screen.blit(string_rendered, intro_rect)
    isPlayerWin = True
    for i in victims:
        isPlayerWin = False
    if isPlayerWin:
        restart()
        all_sprites = pygame.sprite.Group()
        victims = pygame.sprite.Group()
        horizontal_borders = pygame.sprite.Group()
        vertical_borders = pygame.sprite.Group()
        arrows = []
        level = start_screen()
        x, y = generate_level(level)
        k = 0
        numberOfBalls = 3
    pygame.display.flip()
    screen.fill((100, 30, 0))
    clock.tick(20)
