Dual Tetris 문서
==================

2인용 대전 테트리스 게임
-------------------------

**Dual Tetris**는 Python과 Pygame을 사용하여 구현한 2인 대전 테트리스 게임입니다.
한 플레이어가 라인을 제거하면 상대방에게 공격 라인이 추가됩니다.

주요 기능
---------

* 2인 동시 플레이 모드
* 라인 제거 시 상대방 공격 시스템
* 다음 블록 미리보기
* 점수 및 레벨 시스템
* 7가지 테트로미노 블록

조작 방법
---------

Player 1 (좌측)
~~~~~~~~~~~~~~~

* **W** - 블록 회전
* **A** - 왼쪽 이동
* **S** - 빠른 낙하 (소프트 드롭)
* **D** - 오른쪽 이동
* **Left Shift** - 즉시 낙하 (하드 드롭)

Player 2 (우측)
~~~~~~~~~~~~~~~

* **↑** - 블록 회전
* **←** - 왼쪽 이동
* **↓** - 빠른 낙하 (소프트 드롭)
* **→** - 오른쪽 이동
* **Enter** - 즉시 낙하 (하드 드롭)

공통 키
~~~~~~~

* **ESC** - 게임 종료
* **R** - 게임 오버 후 재시작
* **Q** - 게임 오버 후 종료

게임 규칙
---------

기본 규칙
~~~~~~~~~

* 떨어지는 테트로미노 블록을 회전하고 이동하여 배치
* 가로 한 줄을 완전히 채우면 해당 줄이 제거되고 점수 획득
* 블록이 맨 위까지 쌓이면 게임 오버

대전 규칙
~~~~~~~~~

* 2줄 이상을 한 번에 제거하면 상대방에게 공격 라인 전송
* 공격 라인 수 = 제거한 라인 수 - 1

  * 2줄 제거 → 상대방에게 1줄 추가
  * 3줄 제거 → 상대방에게 2줄 추가
  * 4줄 제거 → 상대방에게 3줄 추가

* 공격받은 라인은 회색 블록으로 보드 하단에 추가 (랜덤 위치에 구멍 1개)
* 상대방이 먼저 게임 오버되면 승리

점수 시스템
~~~~~~~~~~~

* 소프트 드롭: 한 칸당 1점
* 하드 드롭: 한 칸당 2점
* 라인 클리어:

  * 1줄: 100점 × 레벨
  * 2줄: 300점 × 레벨
  * 3줄: 500점 × 레벨
  * 4줄: 800점 × 레벨

* 레벨: 10줄 제거마다 1레벨 상승

코드 문서
---------

.. toctree::
   :maxdepth: 2
   :caption: API 문서:

   modules

모듈 및 클래스
~~~~~~~~~~~~~~

.. automodule:: tetris
   :members:
   :undoc-members:
   :show-inheritance:

Tetromino 클래스
^^^^^^^^^^^^^^^^

.. autoclass:: tetris.Tetromino
   :members:
   :special-members: __init__

Tetris 클래스
^^^^^^^^^^^^^

.. autoclass:: tetris.Tetris
   :members:
   :special-members: __init__

함수 목록
~~~~~~~~~

화면 그리기 함수
^^^^^^^^^^^^^^^^

.. autofunction:: tetris.draw_grid
.. autofunction:: tetris.draw_piece
.. autofunction:: tetris.draw_board
.. autofunction:: tetris.draw_player_info
.. autofunction:: tetris.draw_next_piece

메인 함수
^^^^^^^^^

.. autofunction:: tetris.main

색상 및 설정
------------

게임에서 사용되는 색상:

* **BLACK** - 배경색
* **WHITE** - 텍스트 및 선 색상
* **GRAY** - 공격 라인 색상
* **CYAN** - I 블록
* **YELLOW** - O 블록
* **PURPLE** - T 블록
* **GREEN** - S 블록
* **RED** - Z 블록
* **BLUE** - L 블록
* **ORANGE** - J 블록

게임 설정:

* **BLOCK_SIZE**: 25픽셀
* **GRID_WIDTH**: 10칸
* **GRID_HEIGHT**: 20칸
* **SCREEN_WIDTH**: 800픽셀
* **SCREEN_HEIGHT**: 680픽셀

설치 및 실행
------------

필요 사항
~~~~~~~~~

* Python 3.7 이상
* Pygame 라이브러리

설치
~~~~

.. code-block:: bash

   pip install pygame

실행
~~~~

.. code-block:: bash

   python tetris.py

라이선스
--------

이 프로젝트는 교육 목적으로 제작되었습니다.

인덱스 및 검색
--------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
