import pygame
import classes
import time
import math
import numpy as np

pygame.font.init()

pygame.init()
GUI = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Turbo Racer")
clock = pygame.time.Clock()

start_img = pygame.image.load('start_button.png').convert_alpha()
exit_img = pygame.image.load('quit_button.png').convert_alpha()
title_img = pygame.image.load('title_button.png').convert_alpha()

track_img = pygame.image.load('race_track.png')
track_border = pygame.image.load('track_border.png')
track_border_mask = pygame.mask.from_surface(track_border)

car_img = classes.scale_image(pygame.image.load('red-car.png'), 0.5)

finish_line = pygame.image.load('finish.png')
finish_mask = pygame.mask.from_surface(finish_line)
finish_pos = (748, 480)


start_button = classes.Button(500, 300, start_img, 1)
exit_button = classes.Button(500, 420, exit_img, 1)
title = classes.Button(300, 100, title_img, 1)

main_font = pygame.font.SysFont('arial', 44)


class GameInfo:
    def __init__(self):
        self.finish = False
        self.started = False
        self.level_start_time = 0

    def start(self):
        self.started = True
        self.level_start_time = time.time()

    def race_done(self):
        self.finish = True

    def finished(self):
        return self.finish

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)\

    def reset(self):
        self.started = False


class CarActions:
    IMG = car_img
    START_POS = (780, 430)

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.2

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        classes.blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        intersection = mask.overlap(car_mask, offset)
        return intersection

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def reset(self):
        self.x, self.y = self.START_POS
        self.vel = 0


def objects(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    time_text = main_font.render(f'Time Elapsed: {game_info.get_level_time()}s', True, (0, 0, 0))
    GUI.blit(time_text, (10, track_img.get_height() - time_text.get_height() - 40))

    player_car.draw(win)
    pygame.display.update()


def leaderboard(leaderboard_dict):
    x = 400
    y = 300
    GUI.fill((107, 200, 250))
    classes.blit_text(GUI, main_font, 'LEADERBOARD', (550, 100))
    for name in leaderboard_dict:
        classes.blit_text(GUI, main_font, name, (x, y))
        classes.blit_text(GUI, main_font, str(leaderboard_dict[name]), ((x + 500), y))
        y += 80


def handle_collision(car, game_info):
    if car.collide(track_border_mask) is not None:
        car.bounce()

    finish_intersection_collide = car.collide(
        finish_mask, *finish_pos)
    if finish_intersection_collide is not None:
        if finish_intersection_collide[1] == 0:
            car.bounce()
        else:
            car.reset()
            game_info.race_done()


running = True
game_start = False
images = [(track_img, (0, 0)), (finish_line, (748, 480))]
car = CarActions(4, 2)
game_info = GameInfo()

records = {
    'Fred': 40,
    'Greg': 38,
    'Tommy': 35,
    'Gilbert': 32,
    'Lana': 33,
    'Patricia': 29
}

while running:
    if game_start:
        clock.tick(60)

        objects(GUI, images, car)

        while not game_info.started:
            classes.blit_text_center(GUI, main_font, f'Press any key to start!')
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game_info.start()
    else:
        GUI.fill((107, 200, 250))

        if start_button.draw(GUI):
            game_start = True
        if exit_button.draw(GUI):
            running = False
        title.draw(GUI)

        pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        car.rotate(left=True)
    if keys[pygame.K_d]:
        car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        car.move_backward()

    if not moved:
        car.reduce_speed()

    handle_collision(car, game_info)

    if game_info.finished():
        records['You'] = game_info.get_level_time()
        keys = list(records.keys())
        values = list(records.values())
        sorted_value_index = np.argsort(values)
        sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
        classes.blit_text_center(GUI, main_font, f'Your Time: {game_info.get_level_time()}')
        game_info.reset()
        # x = 400
        # y = 300
        # GUI.fill((107, 200, 250))
        # classes.blit_text(GUI, main_font, 'LEADERBOARD', (550, 100))
        # for name in sorted_dict:
        #     classes.blit_text(GUI, main_font, name, (x, y))
        #     classes.blit_text(GUI, main_font, str(time), ((x + 500), y))
        #     y += 80

pygame.quit()
