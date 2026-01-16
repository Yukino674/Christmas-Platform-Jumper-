# 游戏常量
import pygame

# 游戏窗口设置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义 - 确保颜色值在0-255范围内
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 70, 200)
GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 200, 255)
LIGHT_GREEN = (100, 255, 150)
DARK_GREEN = (30, 100, 50)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
ICE_BLUE = (180, 220, 255)      # 冰蓝色
SNOW_WHITE = (240, 248, 255)    # 雪白色
FROST_BLUE = (200, 230, 255)    # 霜蓝色
GLACIER_BLUE = (160, 200, 240)  # 冰川蓝
ICICLE_BLUE = (140, 180, 220)   # 冰柱蓝

# 游戏状态
MENU = 0
LEVEL_SELECT = 1
PLAYING = 2
INSTRUCTIONS = 3
WIN_SCREEN = 4
GAME_OVER = 5
PAUSED = 6  

# 工具函数：确保颜色值在有效范围内
def clamp_color(value):
    return max(0, min(255, value))