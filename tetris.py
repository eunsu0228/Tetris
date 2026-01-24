"""
Dual Tetris - 2인용 대전 테트리스 게임

Python과 Pygame을 사용하여 구현한 2인 대전 테트리스입니다.
한 플레이어가 라인을 제거하면 상대방에게 공격 라인이 추가됩니다.
"""

import pygame
import random

# Pygame 초기화
pygame.init()

# ==================== 색상 정의 ====================
# RGB 값으로 색상 정의 (R, G, B)
BLACK = (0, 0, 0)          # 배경색
WHITE = (255, 255, 255)    # 텍스트 및 선 색상
GRAY = (128, 128, 128)     # 공격 라인 색상
DARK_GRAY = (64, 64, 64)   # 미리보기 박스 테두리
CYAN = (0, 255, 255)       # I 블록 및 Player 1 텍스트
YELLOW = (255, 255, 0)     # O 블록 및 승리 텍스트
PURPLE = (128, 0, 128)     # T 블록
GREEN = (0, 255, 0)        # S 블록 및 재시작 버튼
RED = (255, 0, 0)          # Z 블록 및 VS 텍스트
BLUE = (0, 0, 255)         # L 블록
ORANGE = (255, 165, 0)     # J 블록 및 Player 2 텍스트

# ==================== 게임 설정 ====================
BLOCK_SIZE = 25            # 각 블록의 픽셀 크기
GRID_WIDTH = 10            # 게임 보드의 가로 블록 수
GRID_HEIGHT = 20           # 게임 보드의 세로 블록 수

# 화면 크기 계산
# 좌측 보드 + Next 박스 + 중앙 정보 + Next 박스 + 우측 보드
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH * 2 + 400   # 총 화면 너비
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT + 180     # 총 화면 높이 (하단 조작 안내 공간 포함)

# ==================== 테트로미노 모양 정의 ====================
# 7가지 테트로미노 블록의 형태를 2차원 배열로 정의
# 1은 블록이 있는 부분, 0은 빈 공간
SHAPES = [
    [[1, 1, 1, 1]],              # I - 일자 블록
    [[1, 1], [1, 1]],            # O - 정사각형 블록
    [[0, 1, 0], [1, 1, 1]],      # T - T자 블록
    [[1, 1, 0], [0, 1, 1]],      # S - S자 블록
    [[0, 1, 1], [1, 1, 0]],      # Z - Z자 블록
    [[1, 0, 0], [1, 1, 1]],      # L - L자 블록
    [[0, 0, 1], [1, 1, 1]]       # J - 역L자 블록
]

# 각 테트로미노에 대응하는 색상 배열
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]


# ==================== Tetromino 클래스 ====================
class Tetromino:
    """떨어지는 테트로미노 블록을 나타내는 클래스"""
    
    def __init__(self, x, y):
        """
        테트로미노 객체 초기화
        
        Args:
            x (int): 그리드 상의 x 좌표 (가로 위치)
            y (int): 그리드 상의 y 좌표 (세로 위치)
        """
        self.x = x  # 현재 x 좌표
        self.y = y  # 현재 y 좌표
        self.shape_index = random.randint(0, len(SHAPES) - 1)  # 랜덤하게 블록 형태 선택
        self.shape = SHAPES[self.shape_index]  # 선택된 블록의 형태
        self.color = SHAPE_COLORS[self.shape_index]  # 선택된 블록의 색상
        self.rotation = 0  # 회전 상태 (현재는 미사용)

    def rotate(self):
        """
        블록을 시계방향으로 90도 회전
        
        Returns:
            list: 회전된 블록의 형태 (2차원 배열)
        """
        rotated = []
        # 행과 열을 바꾸면서 역순으로 배치하여 90도 회전 효과
        for i in range(len(self.shape[0])):
            new_row = []
            for j in range(len(self.shape) - 1, -1, -1):
                new_row.append(self.shape[j][i])
            rotated.append(new_row)
        return rotated

    def get_shape(self):
        """
        현재 블록의 형태 반환
        
        Returns:
            list: 현재 블록의 형태 (2차원 배열)
        """
        return self.shape


# ==================== Tetris 게임 클래스 ====================
class Tetris:
    """테트리스 게임 로직을 관리하는 클래스 (각 플레이어당 하나의 인스턴스)"""
    
    def __init__(self, player_id):
        """
        테트리스 게임 객체 초기화
        
        Args:
            player_id (int): 플레이어 번호 (1 또는 2)
        """
        self.player_id = player_id  # 플레이어 식별 번호
        # 게임 보드 초기화 (0은 빈 칸, 색상 값이 있으면 블록이 고정된 칸)
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None  # 현재 조작 중인 블록
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)  # 다음에 나올 블록
        self.game_over = False  # 게임 오버 상태
        self.score = 0  # 현재 점수
        self.lines_cleared = 0  # 제거한 총 라인 수
        self.level = 1  # 현재 레벨
        self.spawn_piece()  # 첫 번째 블록 생성

    def spawn_piece(self):
        """
        새 블록 생성 및 배치
        - 다음 블록을 현재 블록으로 이동
        - 새로운 다음 블록 생성
        - 배치할 위치에 이미 블록이 있으면 게임 오버
        """
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(GRID_WIDTH // 2 - 1, 0)
        
        # 새 블록이 배치될 위치에 이미 블록이 있으면 게임 오버
        if self.check_collision(self.current_piece.x, self.current_piece.y):
            self.game_over = True

    def check_collision(self, x, y, shape=None):
        """
        블록과 보드/다른 블록과의 충돌 검사
        
        Args:
            x (int): 검사할 x 좌표
            y (int): 검사할 y 좌표
            shape (list, optional): 검사할 블록 형태. None이면 현재 블록 사용
            
        Returns:
            bool: 충돌이 있으면 True, 없으면 False
        """
        if shape is None:
            shape = self.current_piece.get_shape()
        
        # 블록의 각 셀에 대해 충돌 검사
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:  # 블록이 있는 셀만 검사
                    new_x = x + j
                    new_y = y + i
                    
                    # 벽 충돌 또는 바닥 충돌 또는 다른 블록과 충돌 검사
                    if (new_x < 0 or new_x >= GRID_WIDTH or 
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x])):
                        return True
        return False

    def merge_piece(self):
        """
        현재 블록을 그리드에 고정 (더 이상 움직일 수 없음)
        블록의 색상 정보를 그리드에 저장
        """
        shape = self.current_piece.get_shape()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:  # 블록이 있는 부분만 그리드에 저장
                    grid_y = self.current_piece.y + i
                    grid_x = self.current_piece.x + j
                    if grid_y >= 0:  # 화면 위쪽 범위 체크
                        self.grid[grid_y][grid_x] = self.current_piece.color

    def clear_lines(self):
        """
        완성된 라인(가로줄이 완전히 채워진 줄)을 제거하고 점수 계산
        
        Returns:
            int: 제거한 라인 수 (상대방에게 보낼 공격 라인 계산용)
        """
        lines_to_clear = []
        # 완성된 라인 찾기
        for i, row in enumerate(self.grid):
            if all(row):  # 모든 칸이 채워져 있으면
                lines_to_clear.append(i)
        
        # 완성된 라인 제거 및 위에서 아래로 블록 이동
        for line in lines_to_clear:
            del self.grid[line]  # 해당 라인 삭제
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])  # 맨 위에 빈 라인 추가
        
        # 점수 및 레벨 계산
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            # 라인 수에 따른 점수 (1줄: 100, 2줄: 300, 3줄: 500, 4줄: 800)
            points = [0, 100, 300, 500, 800]
            self.score += points[min(len(lines_to_clear), 4)] * self.level
            # 10줄마다 레벨 1 상승
            self.level = self.lines_cleared // 10 + 1
        
        return len(lines_to_clear)

    def add_garbage_lines(self, num_lines):
        """
        상대방으로부터 공격받은 라인 추가 (회색 블록, 랜덤 구멍 1개)
        
        Args:
            num_lines (int): 추가할 공격 라인 수
        """
        for _ in range(num_lines):
            if self.grid:
                self.grid.pop(0)  # 맨 위 라인 제거 (블록을 위로 밀어올림)
            # 랜덤 위치에 구멍이 하나 있는 회색 라인 생성
            hole_position = random.randint(0, GRID_WIDTH - 1)
            garbage_line = [GRAY if i != hole_position else 0 for i in range(GRID_WIDTH)]
            self.grid.append(garbage_line)  # 맨 아래에 공격 라인 추가

    def move_piece(self, dx, dy):
        """
        블록을 지정된 방향으로 이동
        
        Args:
            dx (int): x축 이동량 (-1: 왼쪽, 1: 오른쪽)
            dy (int): y축 이동량 (1: 아래)
            
        Returns:
            bool: 이동 성공 시 True, 실패 시 False
        """
        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy
        
        # 충돌이 없으면 이동
        if not self.check_collision(new_x, new_y):
            self.current_piece.x = new_x
            self.current_piece.y = new_y
            return True
        return False

    def rotate_piece(self):
        """
        블록을 시계방향으로 90도 회전
        회전 후 벽에 부딪히면 좌우로 이동을 시도 (Wall Kick)
        """
        rotated_shape = self.current_piece.rotate()
        
        # 회전 후 충돌이 없으면 회전 적용
        if not self.check_collision(self.current_piece.x, self.current_piece.y, rotated_shape):
            self.current_piece.shape = rotated_shape
        else:
            # 벽 킥: 좌우로 이동하여 회전 가능한지 시도
            for dx in [1, -1, 2, -2]:
                if not self.check_collision(self.current_piece.x + dx, self.current_piece.y, rotated_shape):
                    self.current_piece.x += dx
                    self.current_piece.shape = rotated_shape
                    break

    def hard_drop(self):
        """
        블록을 즉시 바닥까지 낙하 (하드 드롭)
        
        Returns:
            int: 제거한 라인 수 (공격용)
        """
        # 더 이상 내려갈 수 없을 때까지 이동
        while self.move_piece(0, 1):
            self.score += 2  # 한 칸당 2점
        self.merge_piece()  # 블록 고정
        cleared = self.clear_lines()  # 라인 제거
        self.spawn_piece()  # 다음 블록 생성
        return cleared

    def soft_drop(self):
        """
        블록을 한 칸 빠르게 낙하 (소프트 드롭)
        
        Returns:
            tuple: (계속 움직일 수 있는지 여부, 제거한 라인 수)
        """
        if self.move_piece(0, 1):
            self.score += 1  # 한 칸당 1점
            return True, 0
        else:
            # 더 이상 내려갈 수 없으면 블록 고정 및 다음 블록 생성
            self.merge_piece()
            cleared = self.clear_lines()
            self.spawn_piece()
            return False, cleared


# ==================== 화면 그리기 함수들 ====================

def draw_grid(screen, offset_x, offset_y):
    """
    게임 보드의 그리드 선 그리기
    
    Args:
        screen: Pygame 화면 객체
        offset_x (int): 보드의 x축 시작 위치
        offset_y (int): 보드의 y축 시작 위치
    """
    # 세로 선 그리기
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY, 
                        (offset_x + x * BLOCK_SIZE, offset_y), 
                        (offset_x + x * BLOCK_SIZE, offset_y + GRID_HEIGHT * BLOCK_SIZE))
    
    # 가로 선 그리기
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY, 
                        (offset_x, offset_y + y * BLOCK_SIZE), 
                        (offset_x + GRID_WIDTH * BLOCK_SIZE, offset_y + y * BLOCK_SIZE))


def draw_piece(screen, piece, offset_x, offset_y):
    """
    현재 떨어지는 블록 그리기
    
    Args:
        screen: Pygame 화면 객체
        piece: 그릴 Tetromino 객체
        offset_x (int): 보드의 x축 시작 위치
        offset_y (int): 보드의 y축 시작 위치
    """
    shape = piece.get_shape()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:  # 블록이 있는 부분만 그리기
                x = offset_x + (piece.x + j) * BLOCK_SIZE
                y = offset_y + (piece.y + i) * BLOCK_SIZE
                # 테두리를 남기고 블록 그리기
                pygame.draw.rect(screen, piece.color, 
                               (x + 1, y + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2))


def draw_board(screen, game, offset_x, offset_y):
    """
    게임 보드에 고정된 블록들 그리기
    
    Args:
        screen: Pygame 화면 객체
        game: Tetris 게임 객체
        offset_x (int): 보드의 x축 시작 위치
        offset_y (int): 보드의 y축 시작 위치
    """
    for y, row in enumerate(game.grid):
        for x, cell in enumerate(row):
            if cell:  # 블록이 있는 셀만 그리기
                pygame.draw.rect(screen, cell, 
                               (offset_x + x * BLOCK_SIZE + 1, 
                                offset_y + y * BLOCK_SIZE + 1, 
                                BLOCK_SIZE - 2, BLOCK_SIZE - 2))


def draw_player_info(screen, game, offset_x, offset_y, font, player_name):
    """
    플레이어 정보 표시 (이름, 점수)
    
    Args:
        screen: Pygame 화면 객체
        game: Tetris 게임 객체
        offset_x (int): 정보 표시 x 위치
        offset_y (int): 정보 표시 y 위치
        font: 사용할 폰트 객체
        player_name (str): 표시할 플레이어 이름
    """
    # 플레이어 이름 표시
    name_text = font.render(player_name, True, WHITE)
    screen.blit(name_text, (offset_x, offset_y))
    
    # 점수 표시
    score_text = font.render(f'{game.score}', True, WHITE)
    screen.blit(score_text, (offset_x, offset_y + 25))


def draw_next_piece(screen, game, offset_x, offset_y, small_font):
    """
    다음에 나올 블록 미리보기
    
    Args:
        screen: Pygame 화면 객체
        game: Tetris 게임 객체
        offset_x (int): 미리보기 박스 x 위치
        offset_y (int): 미리보기 박스 y 위치
        small_font: 사용할 폰트 객체
    """
    # "Next" 텍스트 표시
    next_text = small_font.render('Next:', True, WHITE)
    screen.blit(next_text, (offset_x, offset_y))
    
    # 다음 블록 정보 가져오기
    next_piece = game.next_piece
    shape = next_piece.get_shape()
    
    # 미리보기용으로 블록 크기를 약간 작게 조정
    preview_block_size = BLOCK_SIZE - 5
    
    # 블록을 중앙에 배치하기 위한 오프셋 계산
    shape_width = len(shape[0]) * preview_block_size
    shape_height = len(shape) * preview_block_size
    
    start_x = offset_x + (100 - shape_width) // 2
    start_y = offset_y + 30
    
    # 미리보기 박스 테두리 그리기
    preview_box_width = 100
    preview_box_height = 80
    pygame.draw.rect(screen, DARK_GRAY, 
                    (offset_x, start_y - 5, preview_box_width, preview_box_height), 2)
    
    # 다음 블록 그리기
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                x = start_x + j * preview_block_size
                y = start_y + i * preview_block_size
                pygame.draw.rect(screen, next_piece.color, 
                               (x + 1, y + 1, preview_block_size - 2, preview_block_size - 2))


# ==================== 메인 게임 루프 ====================
def main():
    """메인 게임 함수 - 게임 초기화 및 메인 루프 실행"""
    
    # Pygame 화면 설정
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('테트리스 2인 대전')
    clock = pygame.time.Clock()
    
    # 한글 폰트 설정 시도 (맑은 고딕 -> 나눔고딕 -> Arial 순)
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
    
    # 두 플레이어의 게임 인스턴스 생성
    player1 = Tetris(1)
    player2 = Tetris(2)
    
    # 게임 보드 위치 설정
    board_offset_y = 80  # 상단에서 보드까지의 여백
    player1_offset_x = 30  # Player 1 보드의 좌측 여백
    player2_offset_x = SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE - 30  # Player 2 보드의 우측 정렬
    
    # 블록 자동 낙하 타이머
    fall_time_p1 = 0  # Player 1 타이머
    fall_time_p2 = 0  # Player 2 타이머
    fall_speed = 500  # 낙하 속도 (밀리초)
    
    # 게임 상태 변수
    running = True  # 게임 실행 여부
    winner = None  # 승자 (None, 1, 또는 2)
    
    # ==================== 메인 게임 루프 ====================
    while running:
        # 프레임 시간 계산
        dt = clock.get_rawtime()
        fall_time_p1 += dt
        fall_time_p2 += dt
        clock.tick(60)  # 60 FPS
        
        # ==================== 자동 낙하 처리 ====================
        # Player 1 자동 낙하
        if not player1.game_over and fall_time_p1 >= fall_speed:
            fall_time_p1 = 0
            _, cleared = player1.soft_drop()
            # 2줄 이상 제거 시 상대방에게 공격 (제거한 라인 수 - 1)
            if cleared > 1:
                player2.add_garbage_lines(cleared - 1)
        
        # Player 2 자동 낙하
        if not player2.game_over and fall_time_p2 >= fall_speed:
            fall_time_p2 = 0
            _, cleared = player2.soft_drop()
            # 2줄 이상 제거 시 상대방에게 공격
            if cleared > 1:
                player1.add_garbage_lines(cleared - 1)
        
        # ==================== 승자 결정 ====================
        if player1.game_over and not winner:
            winner = 2  # Player 1이 게임오버면 Player 2 승리
        elif player2.game_over and not winner:
            winner = 1  # Player 2가 게임오버면 Player 1 승리
        
        # ==================== 이벤트 처리 ====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # ========== Player 1 조작 (WASD + Left Shift) ==========
                if not player1.game_over:
                    if event.key == pygame.K_a:  # 왼쪽 이동
                        player1.move_piece(-1, 0)
                    elif event.key == pygame.K_d:  # 오른쪽 이동
                        player1.move_piece(1, 0)
                    elif event.key == pygame.K_s:  # 빠른 낙하
                        _, cleared = player1.soft_drop()
                        if cleared > 1:
                            player2.add_garbage_lines(cleared - 1)
                    elif event.key == pygame.K_w:  # 회전
                        player1.rotate_piece()
                    elif event.key == pygame.K_LSHIFT:  # 즉시 낙하
                        cleared = player1.hard_drop()
                        if cleared > 1:
                            player2.add_garbage_lines(cleared - 1)
                
                # ========== Player 2 조작 (방향키 + Enter) ==========
                if not player2.game_over:
                    if event.key == pygame.K_LEFT:  # 왼쪽 이동
                        player2.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:  # 오른쪽 이동
                        player2.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:  # 빠른 낙하
                        _, cleared = player2.soft_drop()
                        if cleared > 1:
                            player1.add_garbage_lines(cleared - 1)
                    elif event.key == pygame.K_UP:  # 회전
                        player2.rotate_piece()
                    elif event.key == pygame.K_RETURN:  # 즉시 낙하
                        cleared = player2.hard_drop()
                        if cleared > 1:
                            player1.add_garbage_lines(cleared - 1)
                
                # ========== 게임 종료 및 재시작 ==========
                if winner:
                    if event.key == pygame.K_r:  # 재시작
                        player1 = Tetris(1)
                        player2 = Tetris(2)
                        winner = None
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:  # 종료
                        running = False
                elif event.key == pygame.K_ESCAPE:  # 게임 중 ESC는 종료
                    running = False
        
        # ==================== 화면 그리기 ====================
        screen.fill(BLACK)  # 배경을 검은색으로 채우기
        
        # 제목 표시
        title = font.render('테트리스 대전', True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(title, title_rect)
        
        if not winner:  # 게임이 진행 중일 때
            draw_player_info(screen, player1, player1_offset_x, board_offset_y - 55, small_font, 'Player 1 (WASD)')
            draw_board(screen, player1, player1_offset_x, board_offset_y)
            if not player1.game_over:
                draw_piece(screen, player1.current_piece, player1_offset_x, board_offset_y)
            draw_grid(screen, player1_offset_x, board_offset_y)
            
            # Player 1 다음 블록 미리보기 (보드 오른쪽)
            next_box_offset_x = player1_offset_x + GRID_WIDTH * BLOCK_SIZE + 30
            draw_next_piece(screen, player1, next_box_offset_x, board_offset_y + 50, small_font)
            
            draw_player_info(screen, player2, player2_offset_x, board_offset_y - 55, small_font, 'Player 2 (방향키)')
            draw_board(screen, player2, player2_offset_x, board_offset_y)
            if not player2.game_over:
                draw_piece(screen, player2.current_piece, player2_offset_x, board_offset_y)
            draw_grid(screen, player2_offset_x, board_offset_y)
            
            # Player 2 다음 블록 미리보기 (보드 왼쪽)
            next_box_offset_x2 = player2_offset_x - 140
            draw_next_piece(screen, player2, next_box_offset_x2, board_offset_y + 50, small_font)
            
            # ========== 중앙 VS 표시 ==========
            vs_text = font.render('VS', True, RED)
            vs_rect = vs_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(vs_text, vs_rect)
            
            # ========== 하단 조작 안내 ==========
            help_y = board_offset_y + GRID_HEIGHT * BLOCK_SIZE + 30
            help1 = small_font.render('P1: W(회전) A(←) S(↓) D(→) LShift(즉시낙하)', True, CYAN)
            help2 = small_font.render('P2: ↑(회전) ←(좌) ↓(하) →(우) Enter(즉시낙하)', True, ORANGE)
            help1_rect = help1.get_rect(center=(SCREEN_WIDTH // 2, help_y))
            help2_rect = help2.get_rect(center=(SCREEN_WIDTH // 2, help_y + 30))
            screen.blit(help1, help1_rect)
            screen.blit(help2, help2_rect)
        else:  # 게임 종료 시 승리 화면
            # ========== 승리 메시지 ==========
            winner_text = font.render(f'Player {winner} 승리!', True, YELLOW)
            winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            screen.blit(winner_text, winner_rect)
            
            # ========== 최종 점수 표시 ==========
            p1_score = small_font.render(f'Player 1 점수: {player1.score}', True, WHITE)
            p1_score_rect = p1_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            screen.blit(p1_score, p1_score_rect)
            
            p2_score = small_font.render(f'Player 2 점수: {player2.score}', True, WHITE)
            p2_score_rect = p2_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(p2_score, p2_score_rect)
            
            # ========== 구분선 ==========
            pygame.draw.line(screen, WHITE, 
                           (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60),
                           (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 60), 2)
            
            # ========== 재시작/종료 안내 ==========
            restart_text = small_font.render('R - 다시 시작', True, GREEN)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
            screen.blit(restart_text, restart_rect)
            
            quit_text = small_font.render('Q - 게임 종료', True, RED)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(quit_text, quit_rect)
        
        # 화면 업데이트
        pygame.display.flip()
    
    # 게임 종료
    pygame.quit()


# ==================== 프로그램 시작점 ====================
if __name__ == '__main__':
    main()  # 메인 함수 실행
