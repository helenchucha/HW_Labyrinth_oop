import os
import json
import pygame


# Ініціалізація та налаштування
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

# Константи
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Лабіринт")
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
DOG_IMAGE = pygame.transform.scale(pygame.image.load('img/dog.jpg').convert_alpha(), (80, 90))
BONE_IMAGE = pygame.transform.scale(pygame.image.load('img/bone.jpg').convert_alpha(), (70, 50))

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

# Клас для збереження та завантаження прогресу
class SaveLoadManager:
    def __init__(self, filename='save_game.json'):
        self.filename = filename

    def save(self, player_rect, previous_move, path_idx):
        data = {
            'player_x': player_rect.x,
            'player_y': player_rect.y,
            'previous_move': previous_move,
            'path_index': path_idx
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(self.filename):
            return None
        with open(self.filename, 'r') as f:
            return json.load(f)

    def exists(self):
        return os.path.exists(self.filename)

    def delete(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

# Перед запуском запитати, чи є збереження
save_manager = SaveLoadManager()
'''if save_manager.exists():
    print("Знайдено збереження. Бажаєте його завантажити? (y/n): ")
    choice = input().lower()
    if choice == 'y':
        data = save_manager.load()
        if data:
            PLAYER_X = data['player_x']
            PLAYER_Y = data['player_y']
            previous_move = data['previous_move']
            path_index = data['path_index']
        else:
            print("Не вдалося завантажити збереження.")
    else:
        PLAYER_X = (SCREEN_WIDTH - labyrinth.maze_length) / 2 + 15
        PLAYER_Y = (SCREEN_HEIGHT - labyrinth.maze_length) / 2 + 10
        save_manager.delete()'''

if save_manager.exists():
    # Замість print — додамо стан для меню
    show_load_prompt = True
    load_prompt_answered = False
    load_decision = None
else:
    show_load_prompt = False



#Параметри гравця
PLAYER_WIDTH = PLAYER_HEIGHT = 15
PLAYER_COLOR = (255, 0, 0)

# Ініціалізація гравця
PLAYER_X = (SCREEN_WIDTH - labyrinth.maze_length) / 2 + 15
PLAYER_Y = (SCREEN_HEIGHT - labyrinth.maze_length) / 2 + 10

player = None  # створимо пізніше


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
                # Збереження програшу
                save_manager.save(self.player_rect, previous_move, path_index)
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

#player = Player()

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
        #pygame.display.flip()

game = Game()



# Основний цикл гри
running = True

while running:

    # Якщо показуємо меню запиту завантаження
    if 'show_load_prompt' in globals() and show_load_prompt:
        # Малюємо затемнений фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))

        # Виводимо запит
        font = pygame.font.SysFont("Arial", 30)
        question_text = "Знайдено збереження. Завантажити?"
        question_surf = font.render(question_text, True, (255, 255, 255))
        question_rect = question_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
        SCREEN.blit(question_surf, question_rect)

        # Створимо кнопки "Так" і "Ні"
        button_width, button_height = 100, 50
        yes_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 110, SCREEN_HEIGHT / 2 + 10, button_width, button_height)
        no_button_rect = pygame.Rect(SCREEN_WIDTH / 2 + 10, SCREEN_HEIGHT / 2 + 10, button_width, button_height)

        # Малюємо кнопки
        pygame.draw.rect(SCREEN, (0, 255, 0), yes_button_rect)
        pygame.draw.rect(SCREEN, (255, 0, 0), no_button_rect)

        # Текст на кнопках
        font_button = pygame.font.SysFont("Arial", 20)
        yes_text = font_button.render("Так", True, (0, 0, 0))
        no_text = font_button.render("Ні", True, (0, 0, 0))
        SCREEN.blit(yes_text, yes_text.get_rect(center=yes_button_rect.center))
        SCREEN.blit(no_text, no_text.get_rect(center=no_button_rect.center))

        # Обробка натискань у цьому ж циклі
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if yes_button_rect.collidepoint(mouse_pos):
                    # Завантажити збереження
                    data = save_manager.load()
                    if data:
                        PLAYER_X = data['player_x']
                        PLAYER_Y = data['player_y']
                        previous_move = data['previous_move']
                        path_index = data['path_index']
                    show_load_prompt = False
                elif no_button_rect.collidepoint(mouse_pos):
                    # Почати заново
                    PLAYER_X = (SCREEN_WIDTH - labyrinth.maze_length) / 2 + 15
                    PLAYER_Y = (SCREEN_HEIGHT - labyrinth.maze_length) / 2 + 10
                    save_manager.delete()
                    show_load_prompt = False
                    # скидаємо стан
                    GAME_OVER = False
                    game_result = None
                    current_message = ""

        player = Player()

        # Оновлюємо екран і пропускаємо інший рендеринг
        pygame.display.flip()
        continue

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
        SCREEN.blit(DOG_IMAGE, [(SCREEN_WIDTH - labyrinth.maze_length) / 2 - 80, (SCREEN_HEIGHT - labyrinth.maze_length) / 2 - 30])
        SCREEN.blit(BONE_IMAGE, [labyrinth.maze_length + 130, labyrinth.maze_length + 110])
        # Малюємо рівень та гравця
        pygame.draw.rect(SCREEN, PLAYER_COLOR, player.player_rect)


    # Оновлюємо екран
    pygame.display.flip()

pygame.quit()