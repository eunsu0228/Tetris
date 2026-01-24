import pygame
import random

# 초기화
pygame.init()

# 색상 정의
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

# 게임 설정
BLOCK_SIZE = 25
GRID_WIDTH = 10
GRID_HEIGHT = 20
# 2인용 화면: 좌측 보드 + 중앙 정보 + 우측 보드
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH * 2 + 200
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT + 100

# 테트로미노 모양 정의
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]]   # J
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]


class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.rotation = 0

    def rotate(self):
        """블록 회전"""
        rotated = []
        for i in range(len(self.shape[0])):
            new_row = []
            for j in range(len(self.shape) - 1, -1, -1):
                new_row.append(self.shape[j][i])
            rotated.append(new_row)
        return rotated

    def get_shape(self):
        """현재 블록 모양 반환"""
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
        self.spawn_piece()

    def spawn_piece(self):
        """새 블록 생성"""
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        if self.check_collision(self.current_piece.x, self.current_piece.y):
            self.game_over = True

    def check_collision(self, x, y, shape=None):
        """충돌 체크"""
        if shape is None:
            shape = self.current_piece.get_shape()
        
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False

    def merge_piece(self):
        """블록을 그리드에 고정"""
        shape = self.current_piece.get_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + i
                    grid_x = self.current_piece.x + j
                    if grid_y >= 0:
                        self.grid[grid_y][grid_x] = self.current_piece.color

    def clear_lines(self):
        """완성된 라인 제거하고 공격 라인 수 반환"""
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(row):
                lines_to_clear.append(i)
        
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
        """상대방으로부터 받은 공격 라인 추가"""
        for _ in range(num_lines):
            if self.grid:
                self.grid.pop(0)
            hole_position = random.randint(0, GRID_WIDTH - 1)
            garbage_line = [GRAY if i != hole_position else 0 for i in range(GRID_WIDTH)]
            self.grid.append(garbage_line)

    def move_piece(self, dx, dy):
        """블록 이동"""
        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy
        
        if not self.check_collision(new_x, new_y):
            self.current_piece.x = new_x
            self.current_piece.y = new_y
            return True
        return False

    def rotate_piece(self):
        """블록 회전"""
        rotated_shape = self.current_piece.rotate()
        
        if not self.check_collision(self.current_piece.x, self.current_piece.y, rotated_shape):
            self.current_piece.shape = rotated_shape
        else:
            for dx in [1, -1, 2, -2]:
                if not self.check_collision(self.current_piece.x + dx, self.current_piece.y, rotated_shape):
                    self.current_piece.x += dx
                    self.current_piece.shape = rotated_shape
                    break

    def hard_drop(self):
        """즉시 낙하"""
        while self.move_piece(0, 1):
            self.score += 2
        self.merge_piece()
        cleared = self.clear_lines()
        self.spawn_piece()
        return cleared

    def soft_drop(self):
        """빠른 낙하"""
        if self.move_piece(0, 1):
            self.score += 1
            return True, 0
        else:
            self.merge_piece()
            cleared = self.clear_lines()
            self.spawn_piece()
            return False, cleared


def draw_grid(screen, offset_x, offset_y):
    """그리드 그리기"""
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY, 
                        (offset_x + x * BLOCK_SIZE, offset_y), 
                        (offset_x + x * BLOCK_SIZE, offset_y + GRID_HEIGHT * BLOCK_SIZE))
    
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY, 
                        (offset_x, offset_y + y * BLOCK_SIZE), 
                        (offset_x + GRID_WIDTH * BLOCK_SIZE, offset_y + y * BLOCK_SIZE))


def draw_piece(screen, piece, offset_x, offset_y):
    """블록 그리기"""
    shape = piece.get_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                x = offset_x + (piece.x + j) * BLOCK_SIZE
                y = offset_y + (piece.y + i) * BLOCK_SIZE
                pygame.draw.rect(screen, piece.color, 
                               (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))


def draw_board(screen, game, offset_x, offset_y):
    """게임 보드 그리기"""
    for y, row in enumerate(game.grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, 
                               (offset_x + x * BLOCK_SIZE + 1, 
                                offset_y + y * BLOCK_SIZE + 1, 
                                BLOCK_SIZE - 2, BLOCK_SIZE - 2))


def draw_player_info(screen, game, offset_x, offset_y, font, player_name):
    """플레이어 정보 표시"""
    name_text = font.render(player_name, True, WHITE)
    screen.blit(name_text, (offset_x, offset_y))
    
    score_text = font.render(f'{game.score}', True, WHITE)
    screen.blit(score_text, (offset_x, offset_y + 25))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('테트리스 2인 대전')
    clock = pygame.time.Clock()
    
    try:
        font = pygame.font.SysFont('malgungothic', 28)
        small_font = pygame.font.SysFont('malgungothic', 18)
    except:
        try:
            font = pygame.font.SysFont('nanumgothic', 28)
            small_font = pygame.font.SysFont('nanumgothic', 18)
        except:
            font = pygame.font.SysFont('arial', 28)
            small_font = pygame.font.SysFont('arial', 18)
    
    player1 = Tetris(1)
    player2 = Tetris(2)
    
    board_offset_y = 80
    player1_offset_x = 20
    player2_offset_x = SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE - 20
    
    fall_time_p1 = 0
    fall_time_p2 = 0
    fall_speed = 500
    
    running = True
    winner = None
    
    while running:
        dt = clock.get_rawtime()
        fall_time_p1 += dt
        fall_time_p2 += dt
        clock.tick(60)
        
        if not player1.game_over and fall_time_p1 >= fall_speed:
            fall_time_p1 = 0
            _, cleared = player1.soft_drop()
            if cleared > 1:
                player2.add_garbage_lines(cleared - 1)
        
        if not player2.game_over and fall_time_p2 >= fall_speed:
            fall_time_p2 = 0
            _, cleared = player2.soft_drop()
            if cleared > 1:
                player1.add_garbage_lines(cleared - 1)
        
        if player1.game_over and not winner:
            winner = 2
        elif player2.game_over and not winner:
            winner = 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if not player1.game_over:
                    if event.key == pygame.K_a:
                        player1.move_piece(-1, 0)
                    elif event.key == pygame.K_d:
                        player1.move_piece(1, 0)
                    elif event.key == pygame.K_s:
                        _, cleared = player1.soft_drop()
                        if cleared > 1:
                            player2.add_garbage_lines(cleared - 1)
                    elif event.key == pygame.K_w:
                        player1.rotate_piece()
                    elif event.key == pygame.K_LSHIFT:
                        cleared = player1.hard_drop()
                        if cleared > 1:
                            player2.add_garbage_lines(cleared - 1)
                
                if not player2.game_over:
                    if event.key == pygame.K_LEFT:
                        player2.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player2.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        _, cleared = player2.soft_drop()
                        if cleared > 1:
                            player1.add_garbage_lines(cleared - 1)
                    elif event.key == pygame.K_UP:
                        player2.rotate_piece()
                    elif event.key == pygame.K_RETURN:
                        cleared = player2.hard_drop()
                        if cleared > 1:
                            player1.add_garbage_lines(cleared - 1)
                
                if winner:
                    if event.key == pygame.K_r:
                        player1 = Tetris(1)
                        player2 = Tetris(2)
                        winner = None
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        screen.fill(BLACK)
        
        title = font.render('테트리스 대전', True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        if not winner:
            draw_player_info(screen, player1, player1_offset_x, board_offset_y - 55, small_font, 'Player 1 (WASD)')
            draw_board(screen, player1, player1_offset_x, board_offset_y)
            if not player1.game_over:
                draw_piece(screen, player1.current_piece, player1_offset_x, board_offset_y)
            draw_grid(screen, player1_offset_x, board_offset_y)
            
            draw_player_info(screen, player2, player2_offset_x, board_offset_y - 55, small_font, 'Player 2 (방향키)')
            draw_board(screen, player2, player2_offset_x, board_offset_y)
            if not player2.game_over:
                draw_piece(screen, player2.current_piece, player2_offset_x, board_offset_y)
            draw_grid(screen, player2_offset_x, board_offset_y)
            
            vs_text = font.render('VS', True, RED)
            vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(vs_text, vs_rect)
            
            help_y = SCREEN_HEIGHT - 60
            help1 = small_font.render('P1: W(회전) A(←) S(↓) D(→) LShift(즉시낙하)', True, CYAN)
            help2 = small_font.render('P2: ↑(회전) ←(좌) ↓(하) →(우) Enter(즉시낙하)', True, ORANGE)
            screen.blit(help1, (20, help_y))
            screen.blit(help2, (20, help_y + 25))
        else:
            winner_text = font.render(f'Player {winner} 승리!', True, YELLOW)
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(winner_text, winner_rect)
            
            p1_score = small_font.render(f'Player 1 점수: {player1.score}', True, WHITE)
            p1_score_rect = p1_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(p1_score, p1_score_rect)
            
            p2_score = small_font.render(f'Player 2 점수: {player2.score}', True, WHITE)
            p2_score_rect = p2_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(p2_score, p2_score_rect)
            
            pygame.draw.line(screen, WHITE, 
                           (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60),
                           (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 60), 2)
            
            restart_text = small_font.render('R - 다시 시작', True, GREEN)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
            screen.blit(restart_text, restart_rect)
            
            quit_text = small_font.render('Q - 게임 종료', True, RED)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(quit_text, quit_rect)
        
        pygame.display.flip()
    
    pygame.quit()


if __name__ == '__main__':
    main()
