"""
实体模块：定义游戏中的所有对象类
包括玩家、平台、宝石、尖刺和门等游戏实体
"""
import pygame
from constants import *

class Player(pygame.sprite.Sprite):
    """
    玩家类：控制游戏主角的移动、跳跃和碰撞
    继承自pygame的Sprite类，便于碰撞检测和渲染
    """
    def __init__(self, x, y):
        super().__init__()
        # 尝试加载角色图片
        original_image = pygame.image.load("player.png").convert_alpha()
            
        # 创建朝右和朝左的图片
        self.image_right = original_image
        self.image_left = pygame.transform.flip(original_image, True, False)
            
        # 初始使用朝右的图片
        self.image = self.image_right
                    
        # 设置玩家的矩形区域（用于碰撞检测）
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 物理属性
        self.vel_y = 0      # 垂直速度（向下为正，向上为负）
        self.vel_x = 0      # 水平速度
        self.speed = 5      # 水平移动速度
        
        # 跳跃参数：支持大小跳机制
        self.max_jump_power = -9     # 大跳最大速度
        self.min_jump_power = -6     # 小跳速度
        
        # 跳跃状态
        self.jump_held_time = 0      # 跳跃键按住的时间
        self.max_jump_hold = 20      # 最大按住时间
        self.is_jumping = False      # 是否正在跳跃
        self.on_ground = False       # 是否在地面上
        
        # 方向状态
        self.facing_right = True     # 是否面朝右边
        
        # 移动平台相关
        self.on_moving_platform = None      # 当前所在的移动平台
        self.platform_velocity_x = 0        # 平台的水平速度
        
    def update(self, platforms, spikes, screen_width, screen_height):
        """
        更新玩家状态（每帧调用）
        玩家状态：
            "fallen": 玩家掉出屏幕
            "spike_hit": 玩家碰到尖刺
            None: 正常状态
        """
        # 处理左右移动输入
        keys = pygame.key.get_pressed()
        player_move_x = 0
        if keys[pygame.K_LEFT]:
            player_move_x = -self.speed
            self.facing_right = False
            self.image = self.image_left  # 切换为向左的图片
        if keys[pygame.K_RIGHT]:
            player_move_x = self.speed
            self.facing_right = True
            self.image = self.image_right  # 切换为向右的图片
        
        # 处理跳跃输入（支持多个按键）
        jump_pressed = keys[pygame.K_SPACE]
        
        if jump_pressed:
            if self.on_ground and not self.is_jumping:
                # 开始跳跃：初始为小跳速度
                self.is_jumping = True
                self.jump_held_time = 0
                self.vel_y = self.min_jump_power  # -6
            elif self.is_jumping and self.jump_held_time < self.max_jump_hold:
                # 按住跳跃键：逐渐增加速度到最大跳跃速度（大小跳机制）
                self.jump_held_time += 1
                hold_ratio = self.jump_held_time / self.max_jump_hold
                target_speed = self.min_jump_power + (self.max_jump_power - self.min_jump_power) * hold_ratio
                
                # 如果当前速度小于目标速度，就增加速度（注意：负值比较）
                if self.vel_y > target_speed:
                    self.vel_y = target_speed
        else:
            # 松开空格键：结束跳跃
            if self.is_jumping:
                self.is_jumping = False
        
        # 应用重力（每帧增加垂直速度），在平台上不受重力
        self.vel_y += 0.8
        if self.vel_y > 20:  # 限制最大下落速度
            self.vel_y = 20
        
        # 先处理水平移动和碰撞
        self.rect.x += player_move_x
        self.check_collision_x(platforms)
        
        # 垂直移动（考虑移动平台的影响）
        vertical_move = self.vel_y
        if self.on_moving_platform and self.on_moving_platform.vertical:
            vertical_move += self.on_moving_platform.move_speed * self.on_moving_platform.direction
        
        self.rect.y += vertical_move
        
        # 重置垂直碰撞相关状态
        self.on_ground = False
        self.on_moving_platform = None
        self.platform_velocity_x = 0
        
        # 检查头部碰撞（当玩家上升时）
        if vertical_move < 0:
            for platform in platforms:
                # 精确检测：玩家顶部与平台底部接触
                if (self.rect.top <= platform.rect.bottom and 
                    self.rect.top >= platform.rect.bottom - 10 and
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    # 头部碰到平台，停止上升
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
                    self.is_jumping = False
                    break
        
        # 检查脚部碰撞（当玩家下落时）
        if vertical_move >= 0:
            for platform in platforms:
                # 精确检测：玩家底部与平台顶部接触
                if (self.rect.bottom >= platform.rect.top - 5 and 
                    self.rect.bottom <= platform.rect.top + 15 and 
                    self.rect.right > platform.rect.left + 5 and 
                    self.rect.left < platform.rect.right - 5):
                    
                    # 站在平台上，取消重力
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    
                    # 如果是移动平台，记录平台信息
                    if platform.movable:
                        self.on_moving_platform = platform
                        if platform.vertical:
                            self.platform_velocity_x = 0
                        else:
                            self.platform_velocity_x = platform.move_speed * platform.direction
                    break
        
        # 检查是否掉出屏幕底部
        if self.rect.top > screen_height:
            return "fallen"
        
        # 检查尖刺碰撞
        spike_hit = pygame.sprite.spritecollide(self, spikes, False)
        if spike_hit:
            return "spike_hit"
        
        return None  # 正常状态
    
    def check_collision_x(self, platforms):
        #检查水平方向的碰撞
        # 检查水平碰撞
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # 检查是从左侧还是右侧碰撞
                if self.vel_x > 0:  # 向右移动时碰到平台
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:  # 向左移动时碰到平台
                    self.rect.left = platform.rect.right
                
        #检查垂直方向的碰撞在update方法中

class Platform(pygame.sprite.Sprite):
    """
    平台类：游戏的固定平台和移动平台
    """
    def __init__(self, x, y, width, height, color=GREEN, movable=False, vertical=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        
        if movable:
            # 移动平台使用橙色
            self.image.fill(ORANGE)
            
            # 添加移动平台纹理
            darker_color = (clamp_color(ORANGE[0]-40), clamp_color(ORANGE[1]-40), clamp_color(ORANGE[2]-40))
            for i in range(0, width, 15):
                #每15个横坐标绘制一道纹理
                pygame.draw.line(self.image, darker_color, (i, 0), (i, height), 2)
            
            # 根据移动方向添加箭头标识
            arrow_size = 10
            
            if vertical:
                # 垂直移动平台：添加上下箭头
                # 上箭头（三角形三个点的范围内）
                pygame.draw.polygon(self.image, YELLOW, [
                    (width//2, 5),
                    (width//2 - arrow_size, arrow_size + 5),
                    (width//2 + arrow_size, arrow_size + 5)
                ])
                # 下箭头
                pygame.draw.polygon(self.image, YELLOW, [
                    (width//2, height - 5),
                    (width//2 - arrow_size, height - arrow_size - 5),
                    (width//2 + arrow_size, height - arrow_size - 5)
                ])

        else:
            # 固定平台：使用指定颜色，添加纹理
            self.image.fill(color)
            # 添加平台纹理（垂直线条）
            darker_color = (clamp_color(color[0]-30), clamp_color(color[1]-30), clamp_color(color[2]-30))
            for i in range(0, width, 20):
                pygame.draw.line(self.image, darker_color, (i, 0), (i, height), 2)
        
        # 设置平台的矩形区域
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 平台属性
        self.movable = movable      # 是否可移动
        self.vertical = vertical    # 是否垂直移动（仅对移动平台有效）
        
        if movable:
            # 根据移动方向和平台大小设置不同的参数
            if vertical:
                self.move_speed = 1.5  
                self.move_range = 80   # 垂直移动范围
            
            # 移动方向：1=下，-1=上，垂直平台初始向上
            self.direction = 1 if not vertical else -1
            
            # 记录起始位置（用于计算移动范围）
            self.start_x = x
            self.start_y = y
        else:
            # 固定平台的移动参数为0
            self.move_speed = 0
            self.move_range = 0
            self.direction = 0
            self.start_x = x
            self.start_y = y
    
    def update(self):
        #更新移动平台的位置（每帧调用）
        if self.movable:
            if self.vertical:
                # 垂直移动：上下往返
                self.rect.y += self.move_speed * self.direction
                if self.direction > 0:  # 向下移动
                    if self.rect.y > self.start_y + self.move_range:
                        self.direction = -1  # 反向向上
                else:  # 向上移动
                    if self.rect.y < self.start_y - self.move_range:
                        self.direction = 1  # 反向下
            else:
                # 水平移动：左右往返
                self.rect.x += self.move_speed * self.direction
                if self.direction > 0:  # 向右移动
                    if self.rect.x > self.start_x + self.move_range:
                        self.direction = -1  # 反向
                else:  # 向左移动
                    if self.rect.x < self.start_x - self.move_range:
                        self.direction = 1  # 反向

class Gem(pygame.sprite.Sprite):
    """
    宝石类：玩家需要收集的游戏物品
    代表圣诞礼物
    """
    def __init__(self, x, y):
        super().__init__()
        try:
            # 直接加载宝石图片
            self.image = pygame.image.load("gem.png").convert_alpha()
            
        except Exception as e:
            # 如果图片加载失败，使用程序绘制的默认宝石
            print(f"无法加载礼物图片 ({e})，使用默认图形")
            self.image = pygame.Surface((32, 30), pygame.SRCALPHA)
            # 绘制宝石形状：黄色五边形
            pygame.draw.polygon(self.image, YELLOW, [(15, 0), (28, 10), (23, 25), (7, 25), (2, 10)])
            pygame.draw.polygon(self.image, (255, 255, 150), [(15, 5), (24, 12), (20, 22), (10, 22), (6, 12)])
        
        # 设置宝石的矩形区域（中心点在指定位置）
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.collected = False  # 是否已被收集
        
    def draw(self, screen):
        #绘制宝石（如果未被收集）
        if not self.collected:
            screen.blit(self.image, self.rect)

class Spike(pygame.sprite.Sprite):
    """
    尖刺类：游戏中的障碍物，触碰会失去生命
    使用冰川蓝颜色，形状为三角形
    """
    def __init__(self, x, y, width=25, height=35):
        super().__init__()
        # 创建透明表面（尖刺形状不规则）
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # 绘制三角形尖刺
        points = [(0, height), (width//2, 0), (width, height)]
        spike_color = (160, 200, 240)  # 冰川蓝
        pygame.draw.polygon(self.image, spike_color, points)
        
        # 设置尖刺的矩形区域
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    """
    门类：游戏的通关出口
    收集所有宝石后门会打开
    """
    def __init__(self, x, y, width, height):
        super().__init__()
        
        # 加载门图片（会自动适应任意尺寸的图片）
        try:
            # 加载关闭状态的门图片
            self.image_closed = pygame.image.load("door_closed.png").convert_alpha()
            # 加载打开状态的门图片
            self.image_open = pygame.image.load("door_open.png").convert_alpha()
            
            # 自动缩放图片到指定尺寸
            self.image_closed = pygame.transform.scale(self.image_closed, (width, height))
            self.image_open = pygame.transform.scale(self.image_open, (width, height))
            
        except pygame.error as e:
            # 如果图片加载失败，使用颜色方块替代
            print(f"加载门图片失败: {e}")
            print("使用默认颜色方块替代")
            # 关闭状态为紫色方块
            self.image_closed = pygame.Surface((width, height))
            self.image_closed.fill(PURPLE)
            # 打开状态为绿色方块
            self.image_open = pygame.Surface((width, height))
            self.image_open.fill(GREEN)
        
        # 初始显示关闭状态
        self.image = self.image_closed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_open = False  # 门是否打开
        
    def open(self):
        self.is_open = True
        self.image = self.image_open