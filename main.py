import os
from collections import deque
import pygame

# Ініціалізація та налаштування
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

# Константи
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
MAZE_CELL_SIZE = 5  # Розмір клітинки лабіринту
FONT_SIZE = 20

# Колірна палітра
BACKGROUND_COLOR = (255, 255, 255)
WALL_COLOR = (0, 0, 0)

# Шляхи до ресурсів
IMG_PATH = 'img/'
LEVEL_FILE_PATH = "levels/"

# Визначений правильний шлях
CORRECT_PATH = ['RIGHT', 'DOWN', 'LEFT', 'DOWN', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'DOWN', 'DOWN', 'RIGHT', 'RIGHT', 'RIGHT', 'RIGHT', 'DOWN', 'LEFT', 'DOWN', 'DOWN', 'LEFT', 'DOWN', 'RIGHT', 'DOWN', 'RIGHT', 'RIGHT']  # приклад правильного шляху
path_index = 0  # індекс для правильного шляху
previous_move = None

# Глобальні змінні для стану гри і повідомлень
GAME_OVER = False
game_result = None  # 'WIN', 'HIT_WALL', 'RUN_AWAY', 'LOST'
current_message = ""

# Завантаження зображень
DOG_IMAGE = pygame.transform.scale(pygame.image.load('img/dog.jpg').convert_alpha(), (40, 50))
BONE_IMAGE = pygame.transform.scale(pygame.image.load('img/bone.jpg').convert_alpha(), (50, 40))


class Maze:
    def __init__(self, filepath):
        self.level = self.read_file_to_list(filepath)
        self.maze_length = len(self.level) * 5

    def read_file_to_list(self, filepath):
        try:
            with open(filepath, 'r') as file:
                return [line.rstrip('\n') for line in file.readlines()]
        except FileNotFoundError:
            print(f"Помилка: Файл не знайдено по шляху: {filepath}")
            return []
        except Exception as e:
            print(f"Виникла помилка при читанні файла: {e}")
            return None

    def load_level(self):
        global walls
        walls = []  # очищаємо список перед завантаженням
        x = (SCREEN_WIDTH - self.maze_length) / 2
        y = (SCREEN_HEIGHT - self.maze_length) / 2
        for row in self.level:
            for col in row:
                if col == "W":
                    wall_rect = pygame.Rect(x, y, 5, 5)
                    pygame.draw.rect(SCREEN, WALL_COLOR, wall_rect, 0)
                    walls.append(wall_rect)
                x += 5
            y += 5
            x = (SCREEN_WIDTH - self.maze_length) / 2

labyrinth = Maze(LEVEL_FILE_PATH + '0.txt')

class Player:
    def __init__(self):
        global PLAYER_X, PLAYER_Y
        self.player_rect = pygame.Rect(PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def check_move(self, direction, previous_move=None):
        global path_index, GAME_OVER, game_result, current_message
        if GAME_OVER:
            return
        # Перевірка чи правильний напрямок
        if path_index < len(CORRECT_PATH) and direction == CORRECT_PATH[path_index]:
            print("Шарік знайшов правильний шлях")
            path_index += 1
            previous_move = direction
            # Перевірка чи пройшли весь шлях
            if path_index == len(CORRECT_PATH):
                print("Вітаємо! Шарік пройшов лабіринт! Перемога!")
                current_message = "Перемога! Шарік пройшов лабіринт"
                GAME_OVER = True
                game_result = 'WIN'
        else:
            # Перевірка на зіткнення зі стіною або повернення
            if direction == 'INVALID':
                print("Шарік вдарився об стіну, гра завершена.")
                current_message = "Шарік вдарився об стіну, гра завершена."
                GAME_OVER = True
                game_result = 'HIT_WALL'
            elif previous_move and ((direction == 'LEFT' and previous_move == 'RIGHT') or
                                    (direction == 'RIGHT' and previous_move == 'LEFT') or
                                    (direction == 'UP' and previous_move == 'DOWN') or
                                    (direction == 'DOWN' and previous_move == 'UP')):
                print("Шарік злякався і втік, гра завершена.")
                current_message = "Шарік злякався і втік, гра завершена."
                GAME_OVER = True
                game_result = 'RUN_AWAY'
            else:
                print("Шарік заблукав, гра завершена.")
                current_message = "Шарік заблукав, гра завершена."
                GAME_OVER = True
                game_result = 'LOST'
        return previous_move

#Параметри гравця
PLAYER_WIDTH = PLAYER_HEIGHT = 15
PLAYER_COLOR = (255, 0, 0)
PLAYER_X = (SCREEN_WIDTH - labyrinth.maze_length) / 2 + 15
PLAYER_Y = (SCREEN_HEIGHT - labyrinth.maze_length) / 2 + 10

player = Player()

class Game:
    def move_player(self, dx, dy):
        global previous_move
        new_rect = player.player_rect.move(dx / 2, dy / 2)

        # Перевірка зіткнення зі стінами
        for wall in walls:
            if new_rect.colliderect(wall):
                player.check_move('INVALID')
                return  # рух заборонений, вихід

        # Визначаємо напрямок
        if dx > 0:
            previous_move = player.check_move('RIGHT', previous_move)
        elif dx < 0:
            previous_move = player.check_move('LEFT', previous_move)
        elif dy > 0:
            previous_move = player.check_move('DOWN', previous_move)
        elif dy < 0:
            previous_move = player.check_move('UP', previous_move)
        else:
            # Якщо руху немає
            return

        # Якщо гра не завершена, виконуємо рух
        if not GAME_OVER:
            player.player_rect.x += dx
            player.player_rect.y += dy


    def show_message(self, text, x, y):
        font = pygame.font.SysFont("Arial", 20)
        message = font.render(text, True, (255, 0, 0))
        message_rect = message.get_rect(topleft=(x, y))
        SCREEN.blit(message, message_rect)
        pygame.display.flip()

game = Game()



# Основний цикл гри
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not GAME_OVER:
                if event.key == pygame.K_LEFT:
                    game.move_player(-30, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move_player(30, 0)
                elif event.key == pygame.K_UP:
                    game.move_player(0, -30)
                elif event.key == pygame.K_DOWN:
                    game.move_player(0, 30)
                elif event.key == pygame.K_ESCAPE:
                    running = False


    # Малюємо фон
    SCREEN.fill(BACKGROUND_COLOR)

    if GAME_OVER:
        # Після завершення гри виводимо повідомлення
        if game_result == 'WIN':
            game.show_message("Вітаємо з перемогою!", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
        elif game_result == 'HIT_WALL':
            game.show_message("Шарік вдарився об стіну, гра завершена.", SCREEN_WIDTH // 10, SCREEN_HEIGHT // 3)
        elif game_result == 'RUN_AWAY':
            game.show_message("Шарік злякався і втік, гра завершена.", SCREEN_WIDTH // 5, SCREEN_HEIGHT // 3)
        elif game_result == 'LOST':
            game.show_message("Шарік заблукав, гра завершена.", SCREEN_WIDTH // 5, SCREEN_HEIGHT // 3)
    else:
        # Готуємо рівень
        labyrinth.load_level()
        SCREEN.blit(DOG_IMAGE, [(SCREEN_WIDTH - labyrinth.maze_length) / 2 - 40, (SCREEN_HEIGHT - labyrinth.maze_length) / 2 - 15])
        SCREEN.blit(BONE_IMAGE, [labyrinth.maze_length + 130, labyrinth.maze_length + 110])
        # Малюємо рівень та гравця
        pygame.draw.rect(SCREEN, PLAYER_COLOR, player.player_rect)


    # Оновлюємо екран
    pygame.display.flip()

pygame.quit()