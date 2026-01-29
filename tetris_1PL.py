import pygame
import random
import copy

# Pygame 초기화
pygame.init()

# ==================== 색상 정의 ====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# ==================== 게임 설정 ====================
BLOCK_SIZE = 25
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH * 2 + 400
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT + 180

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]]
]
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class Tetromino:
    def __init__(self, x, y, shape_index=None):
        self.x = x
        self.y = y
        if shape_index is None:
            self.shape_index = random.randint(0, len(SHAPES) - 1)
        else:
            self.shape_index = shape_index
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]

    def rotate(self):
        rotated = []
        for i in range(len(self.shape[0])):
            new_row = []
            for j in range(len(self.shape) - 1, -1, -1):
                new_row.append(self.shape[j][i])
            rotated.append(new_row)
        return rotated

    def get_shape(self):
        return self.shape

class Tetris:
    def __init__(self, player_id):
        self.player_id = player_id
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        self.game_over = False
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        # AI용 변수
        self.target_x = None
        self.target_rotation = None
        self.spawn_piece()

    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        if self.check_collision(self.current_piece.x, self.current_piece.y):
            self.game_over = True
        
        # AI인 경우 새로운 조작 목표 계산
        if self.player_id == 2 and not self.game_over:
            self.think_best_move()

    def check_collision(self, x, y, shape=None, grid=None):
        if shape is None: shape = self.current_piece.get_shape()
        if grid is None: grid = self.grid
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x, new_y = x + j, y + i
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x])):
                        return True
        return False

    def merge_piece(self):
        shape = self.current_piece.get_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y, grid_x = self.current_piece.y + i, self.current_piece.x + j
                    if grid_y >= 0: self.grid[grid_y][grid_x] = self.current_piece.color

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(row)]
        for line in lines_to_clear:
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            points = [0, 100, 300, 500, 800]
            self.score += points[min(len(lines_to_clear), 4)] * self.level
            self.level = self.lines_cleared // 10 + 1
        return len(lines_to_clear)

    def add_garbage_lines(self, num_lines):
        for _ in range(num_lines):
            if self.grid: self.grid.pop(0)
            hole = random.randint(0, GRID_WIDTH - 1)
            self.grid.append([GRAY if i != hole else 0 for i in range(GRID_WIDTH)])

    def move_piece(self, dx, dy):
        if not self.check_collision(self.current_piece.x + dx, self.current_piece.y + dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        rotated = self.current_piece.rotate()
        if not self.check_collision(self.current_piece.x, self.current_piece.y, rotated):
            self.current_piece.shape = rotated
            return True
        return False

    def hard_drop(self):
        while self.move_piece(0, 1): self.score += 2
        self.merge_piece()
        cleared = self.clear_lines()
        self.spawn_piece()
        return cleared

    def soft_drop(self):
        if self.move_piece(0, 1):
            self.score += 1
            return True, 0
        else:
            self.merge_piece()
            cleared = self.clear_lines()
            self.spawn_piece()
            return False, cleared

    # ==================== AI 로직 영역 ====================
    def think_best_move(self):
        """AI가 현재 보드 상황에서 최적의 위치(x)와 회전 횟수를 계산"""
        best_score = -1000000
        self.target_x = self.current_piece.x
        self.target_rotation = 0

        # 4번의 회전 상태에 대해 검사
        temp_piece = Tetromino(self.current_piece.x, self.current_piece.y, self.current_piece.shape_index)
        for r in range(4):
            # 각 회전 상태에서 가능한 모든 가로 위치(x) 검사
            for x in range(-2, GRID_WIDTH):
                if not self.check_collision(x, 0, temp_piece.shape):
                    # 바닥까지 내려갔을 때의 y 위치 찾기
                    y = 0
                    while not self.check_collision(x, y + 1, temp_piece.shape):
                        y += 1
                    
                    # 시뮬레이션 점수 계산 (낮을수록 좋음, 줄 제거 가점)
                    score = y * 10  # 더 낮게 깔릴수록 높은 점수
                    # 간단한 휴리스틱: 구멍이나 높이 차이는 배제하고 기초적인 '낮게 쌓기' 위주
                    if score > best_score:
                        best_score = score
                        self.target_x = x
                        self.target_rotation = r
            temp_piece.shape = temp_piece.rotate()

    def ai_update(self):
        """AI가 목표 위치로 한 칸씩 이동 및 회전"""
        if self.game_over: return 0
        
        # 1. 회전 맞추기
        if self.target_rotation > 0:
            if self.rotate_piece():
                self.target_rotation -= 1
        # 2. 가로 위치 맞추기
        elif self.current_piece.x < self.target_x:
            self.move_piece(1, 0)
        elif self.current_piece.x > self.target_x:
            self.move_piece(-1, 0)
        # 3. 위치가 맞으면 하드 드롭
        else:
            return self.hard_drop()
        return 0

# ==================== 그리기 함수 (동일) ====================
def draw_grid(screen, offset_x, offset_y):
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY, (offset_x + x * BLOCK_SIZE, offset_y), (offset_x + x * BLOCK_SIZE, offset_y + GRID_HEIGHT * BLOCK_SIZE))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY, (offset_x, offset_y + y * BLOCK_SIZE), (offset_x + GRID_WIDTH * BLOCK_SIZE, offset_y + y * BLOCK_SIZE))

def draw_piece(screen, piece, offset_x, offset_y):
    shape = piece.get_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color, (offset_x + (piece.x + j) * BLOCK_SIZE + 1, offset_y + (piece.y + i) * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))

def draw_board(screen, game, offset_x, offset_y):
    for y, row in enumerate(game.grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (offset_x + x * BLOCK_SIZE + 1, offset_y + y * BLOCK_SIZE + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))

def draw_player_info(screen, game, offset_x, offset_y, font, player_name):
    name_text = font.render(player_name, True, WHITE)
    screen.blit(name_text, (offset_x, offset_y))
    score_text = font.render(f'{game.score}', True, WHITE)
    screen.blit(score_text, (offset_x, offset_y + 25))

def draw_next_piece(screen, game, offset_x, offset_y, small_font):
    next_text = small_font.render('Next:', True, WHITE)
    screen.blit(next_text, (offset_x, offset_y))
    next_piece = game.next_piece
    shape = next_piece.get_shape()
    preview_block_size = BLOCK_SIZE - 5
    start_x = offset_x + (100 - len(shape[0]) * preview_block_size) // 2
    start_y = offset_y + 30
    pygame.draw.rect(screen, DARK_GRAY, (offset_x, start_y - 5, 100, 80), 2)
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, next_piece.color, (start_x + j * preview_block_size + 1, start_y + i * preview_block_size + 1, preview_block_size - 2, preview_block_size - 2))

# ==================== 메인 루프 ====================
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('테트리스 1인 대전 vs AI')
    clock = pygame.time.Clock()
    
    try:
        font = pygame.font.SysFont('malgungothic', 28)
        small_font = pygame.font.SysFont('malgungothic', 18)
    except:
        font = pygame.font.SysFont('arial', 28)
        small_font = pygame.font.SysFont('arial', 18)
    
    player1 = Tetris(1)
    player2 = Tetris(2) # AI Player
    
    board_offset_y = 80
    player1_offset_x = 30
    player2_offset_x = SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE - 30
    
    fall_time_p1 = 0
    ai_tick = 0 # AI 동작 간격 조절용
    fall_speed = 500
    
    running = True
    winner = None
    
    while running:
        dt = clock.get_rawtime()
        fall_time_p1 += dt
        ai_tick += dt
        clock.tick(60)
        
        # P1 자동 낙하
        if not player1.game_over and fall_time_p1 >= fall_speed:
            fall_time_p1 = 0
            _, cleared = player1.soft_drop()
            if cleared > 1: player2.add_garbage_lines(cleared - 1)
        
        # P2(AI) 동작 - 약 0.2초마다 한 칸씩 움직이도록 설정 (너무 빠르면 재미없으므로)
        if not player2.game_over and ai_tick >= 200:
            ai_tick = 0
            cleared = player2.ai_update()
            if cleared > 1: player1.add_garbage_lines(cleared - 1)
        
        if player1.game_over and not winner: winner = 2
        elif player2.game_over and not winner: winner = 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if not player1.game_over:
                    if event.key == pygame.K_a: player1.move_piece(-1, 0)
                    elif event.key == pygame.K_d: player1.move_piece(1, 0)
                    elif event.key == pygame.K_s:
                        _, cleared = player1.soft_drop()
                        if cleared > 1: player2.add_garbage_lines(cleared - 1)
                    elif event.key == pygame.K_w: player1.rotate_piece()
                    elif event.key == pygame.K_LSHIFT:
                        cleared = player1.hard_drop()
                        if cleared > 1: player2.add_garbage_lines(cleared - 1)
                
                if winner and event.key == pygame.K_r:
                    player1, player2 = Tetris(1), Tetris(2)
                    winner = None
                elif event.key == pygame.K_ESCAPE: running = False

        screen.fill(BLACK)
        title = font.render('테트리스 대전 vs AI', True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 30)))
        
        if not winner:
            draw_player_info(screen, player1, player1_offset_x, board_offset_y - 55, small_font, 'Player 1 (You)')
            draw_board(screen, player1, player1_offset_x, board_offset_y)
            if not player1.game_over: draw_piece(screen, player1.current_piece, player1_offset_x, board_offset_y)
            draw_grid(screen, player1_offset_x, board_offset_y)
            draw_next_piece(screen, player1, player1_offset_x + GRID_WIDTH * BLOCK_SIZE + 30, board_offset_y + 50, small_font)
            
            draw_player_info(screen, player2, player2_offset_x, board_offset_y - 55, small_font, 'Player 2 (AI)')
            draw_board(screen, player2, player2_offset_x, board_offset_y)
            if not player2.game_over: draw_piece(screen, player2.current_piece, player2_offset_x, board_offset_y)
            draw_grid(screen, player2_offset_x, board_offset_y)
            draw_next_piece(screen, player2, player2_offset_x - 140, board_offset_y + 50, small_font)
            
            vs_text = font.render('VS', True, RED)
            screen.blit(vs_text, vs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        else:
            msg = f'{"당신" if winner==1 else "AI"}의 승리!'
            win_text = font.render(msg, True, YELLOW)
            screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
            r_text = small_font.render('R - 다시 시작 / ESC - 종료', True, GREEN)
            screen.blit(r_text, r_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))
        
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()