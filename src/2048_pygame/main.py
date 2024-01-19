import pygame
import random

# ゲームの初期化
pygame.init()
size = 510
game_font = pygame.font.Font(None, 40)
tile_font = pygame.font.Font(None, 60)
screen = pygame.display.set_mode((size, size))
pygame.display.set_caption("2048")

# 色の定義
background_color = (187, 173, 160)
tile_colors = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

# ゲームの状態を表すクラス
class GameState:
    def __init__(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.moving_tiles = []
        self.score = 0
        self.game_over = False
        self.game_clear = False

    def place_random_tile(self):
        empty_tiles = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_tiles:
            row, col = random.choice(empty_tiles)
            self.board[row][col] = random.choice([2, 4])

    def move_tiles(self, direction):
        if direction == 'up':
            self.board = list(map(list, zip(*self.board))) # 90度反時計回りに回転
        elif direction == 'down':
            self.board = list(map(list, zip(*self.board[::-1]))) # 90度時計回りに回転
        elif direction == 'right':
            self.board = [row[::-1] for row in self.board] # 左右反転

        new_board = [[0] * 4 for _ in range(4)]
        for i in range(4):
            j = 0
            k = 0
            while j < 4:
                if self.board[i][j] != 0:
                    if k > 0 and new_board[i][k - 1] == self.board[i][j]:
                        new_board[i][k - 1] *= 2
                        self.score += new_board[i][k - 1]
                    else:
                        new_board[i][k] = self.board[i][j]
                        k += 1
                j += 1
        self.board = new_board

        if direction == 'up':
            self.board = list(map(list, zip(*self.board[::-1]))) # 90度時計回りに回転
            self.board = [row[::-1] for row in self.board] # 左右反転を解除
        elif direction == 'down':
            self.board = list(map(list, zip(*self.board))) # 90度反時計回りに回転
            self.board = self.board[::-1] # 上下反転を解除
        elif direction == 'right':
            self.board = [row[::-1] for row in self.board] # 左右反転を解除

    def is_game_over(self):
        if any(0 in row for row in self.board):
            return False
        for i in range(4):
            for j in range(4):
                if i < 3 and self.board[i][j] == self.board[i+1][j]:
                    return False
                if j < 3 and self.board[i][j] == self.board[i][j+1]:
                    return False
        return True

# ゲームの状態を初期化
game_state = GameState()
game_state.place_random_tile()
game_state.place_random_tile()

def update_game_state(game_state):
    if not game_state.game_over:
        game_state.place_random_tile()
        game_state.game_over = game_state.is_game_over()
        # Check for game clear (2048 tile) only if a tile has been moved
        if any(2048 in row for row in game_state.board):
            game_state.game_clear = True

touch_start_pos = None
def handle_events(game_state, touch_start_pos):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, touch_start_pos
        elif event.type == pygame.FINGERDOWN:
            touch_start_pos = event.x, event.y
        elif event.type == pygame.FINGERUP:
            if touch_start_pos is not None:
                touch_end_pos = event.x, event.y
                dx = touch_end_pos[0] - touch_start_pos[0]
                dy = touch_end_pos[1] - touch_start_pos[1]
                if abs(dx) > abs(dy):
                    if dx > 0:
                        game_state.move_tiles('right')
                    else:
                        game_state.move_tiles('left')
                else:
                    if dy > 0:
                        game_state.move_tiles('down')
                    else:
                        game_state.move_tiles('up')
                update_game_state(game_state)
        elif event.type == pygame.KEYDOWN:
            if not game_state.game_clear and not game_state.game_over:
                key_pressed = False
                if event.key == pygame.K_UP:
                    game_state.move_tiles('up')
                    key_pressed = True
                elif event.key == pygame.K_DOWN:
                    game_state.move_tiles('down')
                    key_pressed = True
                elif event.key == pygame.K_LEFT:
                    game_state.move_tiles('left')
                    key_pressed = True
                elif event.key == pygame.K_RIGHT:
                    game_state.move_tiles('right')
                    key_pressed = True

                if key_pressed:
                    update_game_state(game_state)
    return True, touch_start_pos

def draw_game(game_state, screen, game_font):
    screen.fill(background_color)

    # タイルを描画
    for i in range(4):
        for j in range(4):
            value = game_state.board[i][j]
            color = tile_colors[value]
            pygame.draw.rect(screen, color, (j * 125 + 10, i * 125 + 10, 115, 115))
            if value != 0:
                text_surface = tile_font.render(str(value), True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(j * 125 + 65, i * 125 + 65))
                screen.blit(text_surface, text_rect)

    # ゲームクリアメッセージを描画
    if game_state.game_clear:
        game_clear_text = game_font.render("Game Clear!", True, (0, 0, 0))
        screen.blit(game_clear_text, (170, 240))
        score_text = game_font.render(f"Score: {game_state.score}", True, (0, 0, 0))
        screen.blit(score_text, (170, 270))  # Adjust the position as needed

    # ゲームオーバーメッセージを描画
    if game_state.game_over:
        game_over_text = game_font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (170, 240))
        score_text = game_font.render(f"Score: {game_state.score}", True, (0, 0, 0))
        screen.blit(score_text, (170, 270))  # Adjust the position as needed

# ゲームループ
running = True
while running:
    running, touch_start_pos = handle_events(game_state, touch_start_pos)
    draw_game(game_state, screen, game_font)
    pygame.display.flip()

# ゲーム終了
pygame.quit()