import pygame
import sys
from constants import *
from entities import Player, Platform, Gem, Spike, Door
from ui import Button, load_font

class Game:
    def __init__(self):
        pygame.init()  # 初始化所有Pygame模块
        pygame.font.init()  # 确保字体模块已初始化
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("圣诞送礼物 - 2D平台跳跃小游戏")
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.current_level = 1
        self.lives = 3
        self.gems_collected = 0
        self.total_gems = 0
        self.birth_point = (100, SCREEN_HEIGHT - 150)  # 默认出生点

        #音频相关属性
        self.victory_sound = None
        self.victory_sound_played = False  # 防止重复播放
        
        # 尝试加载胜利音效
        try:
            # 初始化音频模块
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # 加载音效（支持多种格式）
            sound_formats = ["victory.mp3", "victory.wav", "victory.ogg"]
            sound_loaded = False
            
            for sound_file in sound_formats:
                try:
                    self.victory_sound = pygame.mixer.Sound(sound_file)
                    sound_loaded = True
                    break
                except:
                    continue
            
            if not sound_loaded:
                print("未找到胜利音效文件，将静音运行")
                self.victory_sound = None
            else:
                # 设置音量（0.0-1.0）
                self.victory_sound.set_volume(0.7)
                
        except Exception as e:
            print(f"音频初始化失败: {e}")
            self.victory_sound = None

        # 添加关卡背景图片
        try:
            self.background = pygame.image.load("background.png").convert_alpha()
            # 缩放背景图片到屏幕尺寸
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            print("背景图片加载失败，使用纯色背景")
            self.background = None

        # 添加菜单背景图片（用于所有非游戏界面）
        try:
            menu_bg_image = pygame.image.load("menu_bg.png").convert_alpha()
            # 使用保持比例的方法缩放
            self.menu_background = self.scale_keep_ratio(menu_bg_image, SCREEN_WIDTH, SCREEN_HEIGHT)
        except:
            print("菜单背景图片加载失败，使用纯色背景")
            self.menu_background = None

        # 加载字体
        self.font = load_font(36)
        self.title_font = load_font(72)
        self.instructions_font = load_font(28)
        
        # 创建按钮
        button_width = 200
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.start_button = Button(button_x, 250, button_width, button_height, "开始游戏", GREEN, LIGHT_GREEN, self.font)
        self.instructions_button = Button(button_x, 330, button_width, button_height, "游戏说明", BLUE, LIGHT_BLUE, self.font)
        self.exit_button = Button(button_x, 410, button_width, button_height, "退出游戏", RED, (255, 100, 100), self.font)
        
        self.level1_button = Button(button_x, 250, button_width, button_height, "关卡 1", GREEN, LIGHT_GREEN, self.font)
        self.level2_button = Button(button_x, 330, button_width, button_height, "关卡 2", BLUE, LIGHT_BLUE, self.font)
        self.back_button = Button(button_x, 410, button_width, button_height, "返回菜单", GRAY, (150, 150, 150), self.font)
        
        # 暂停菜单按钮
        self.resume_button = Button(button_x, 300, button_width, button_height, "继续游戏", GREEN, LIGHT_GREEN, self.font)
        self.pause_menu_button = Button(button_x, 380, button_width, button_height, "返回菜单", BLUE, LIGHT_BLUE, self.font)

        # 游戏说明页面的返回按钮（放在右上角）
        self.instructions_back_button = Button(SCREEN_WIDTH - 210, 20, 190, 50, "返回菜单", GRAY, (150, 150, 150), self.font)
        
        self.restart_button = Button(button_x, 350, button_width, button_height, "重新开始", GREEN, LIGHT_GREEN, self.font)
        self.menu_button = Button(button_x, 430, button_width, button_height, "返回菜单", BLUE, LIGHT_BLUE, self.font)
        
        # 游戏实体
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.door = None
        self.player = None
        
        # 加载游戏关卡
        self.load_level(self.current_level)

    def scale_keep_ratio(self, image, target_width, target_height):
        original_width = image.get_width()
        original_height = image.get_height()
            
        width_ratio = target_width / original_width
        height_ratio = target_height / original_height
        scale = min(width_ratio, height_ratio)
            
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
            
        scaled_image = pygame.transform.scale(image, (new_width, new_height))
            
        result = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        result.blit(scaled_image, (x, y))
            
        return result

    def play_victory_sound(self):
        """播放胜利音效"""
        if self.victory_sound and not self.victory_sound_played:
            try:
                # 停止所有正在播放的音效
                pygame.mixer.stop()
                
                # 播放胜利音效（0表示不循环，-1表示循环）
                self.victory_sound.play(0)
                self.victory_sound_played = True
                print("播放胜利音效")
            except Exception as e:
                print(f"播放音效失败: {e}")

    def stop_victory_sound(self):
        """停止胜利音效"""
        if self.victory_sound:
            try:
                self.victory_sound.stop()
                self.victory_sound_played = False
            except:
                pass         

    def load_level(self, level_num):
        # 清空现有实体
        self.all_sprites.empty()
        self.platforms.empty()
        self.gems.empty()
        self.spikes.empty()
        self.door = None
        self.player = None
        self.gems_collected = 0
        # 重置音频播放状态
        self.victory_sound_played = False
        
        # 根据关卡创建游戏元素
        if level_num == 1:
            self.total_gems = 6
            
            # 清空所有边界平台，让所有平台悬空
            # 第一层平台（底部）
            birth_platform_y = SCREEN_HEIGHT - 100  # 平台顶部Y坐标
            birth_platform_width = 150
            self.create_platform(50, birth_platform_y, birth_platform_width, 20, ICE_BLUE)# 出生平台
            self.create_platform(400, SCREEN_HEIGHT - 50, 200, 20, ICE_BLUE)  # 长平台
            self.create_platform(700, SCREEN_HEIGHT - 100, 120, 20, ICE_BLUE)  # 短平台

            # 设置出生点（在出生平台中间偏左）
            player_height = 40  # 玩家高度
            self.birth_point = (
                50 + birth_platform_width // 4,  # 平台1/4位置
                birth_platform_y - player_height  # 平台顶部减去玩家高度
            )
            
            # 创建玩家 - 直接使用出生点
            self.player = Player(self.birth_point[0], self.birth_point[1])
            self.all_sprites.add(self.player)

            
            # 第二层平台（中间层）
            self.create_platform(100, SCREEN_HEIGHT - 250, 180, 20, SNOW_WHITE)  # 长平台
            # 长平台中间带刺
            self.create_platform(450, SCREEN_HEIGHT - 250, 250, 20, SNOW_WHITE)  # 长平台
            self.create_spikes(550, SCREEN_HEIGHT - 285, 2)  # 平台中间的尖刺
            
            # 第三层平台（上层）
            self.create_platform(250, SCREEN_HEIGHT - 400, 150, 20, SNOW_WHITE)  # 长平台
            self.create_platform(600, SCREEN_HEIGHT - 400, 120, 20, SNOW_WHITE)  # 短平台
            
            # 垂直移动平台（便于上下移动）
            self.create_platform(800, SCREEN_HEIGHT - 350, 100, 15, FROST_BLUE, movable=True, vertical=True)
            
            # 第四层平台（顶部层）- 大门所在
            self.create_platform(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 550, 220, 20, GLACIER_BLUE)  # 长平台，右上角
            
            # 宝石分布
            self.create_gem(210, SCREEN_HEIGHT - 120)  # 第一层左平台
            self.create_gem(500, SCREEN_HEIGHT - 120)  # 第一层中平台
            self.create_gem(760, SCREEN_HEIGHT - 120)  # 第一层右平台
            
            self.create_gem(190, SCREEN_HEIGHT - 270)  # 第二层左平台
            self.create_gem(650, SCREEN_HEIGHT - 270)  # 第二层右平台（避开尖刺）
            
            self.create_gem(850, SCREEN_HEIGHT - 370)  # 垂直移动平台上
            
            # 大门 - 放在第四层右上角的长平台上
            self.door = Door(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 650, 100, 100)
            self.all_sprites.add(self.door)

        elif level_num == 2:
            self.total_gems = 8
            
            # 第一层平台（底部）- 出生平台
            birth_platform_y = SCREEN_HEIGHT - 80
            birth_platform_width = 100
            self.create_platform(0, birth_platform_y, birth_platform_width, 20, SNOW_WHITE)
            
            # 设置出生点
            player_height = 40
            self.birth_point = (
                birth_platform_width // 2,
                birth_platform_y - player_height
            )
            
            # 创建玩家
            self.player = Player(self.birth_point[0], self.birth_point[1])
            self.all_sprites.add(self.player)
            
            # 第一层其他平台
            self.create_platform(200, SCREEN_HEIGHT - 80, 250, 20, ICE_BLUE)  # 长平台
            self.create_spikes(300, SCREEN_HEIGHT - 115, 2)  # 平台中间的尖刺
            self.create_platform(650, SCREEN_HEIGHT - 80, 120, 20, ICE_BLUE)  # 短平台
            
            # 第一个关键垂直移动平台（必用的，连接第一层到第二层）
            self.create_platform(250, SCREEN_HEIGHT - 200, 100, 15, FROST_BLUE, movable=True, vertical=True)
            self.create_platform(850, SCREEN_HEIGHT - 200, 100, 15, FROST_BLUE, movable=True, vertical=True)
            
            # 第二层平台（中间层）
            self.create_platform(50, SCREEN_HEIGHT - 280, 180, 20, SNOW_WHITE)  # 左平台
            self.create_platform(400, SCREEN_HEIGHT - 280, 200, 20, SNOW_WHITE)  # 中平台，带刺
            self.create_spikes(480, SCREEN_HEIGHT - 315, 2)  # 平台中间的尖刺
            self.create_platform(700, SCREEN_HEIGHT - 280, 150, 20, SNOW_WHITE)  # 右平台
            

        
            # 第三层平台（上层）
            self.create_platform(100, SCREEN_HEIGHT - 400, 220, 20, SNOW_WHITE)  # 长平台
            self.create_platform(550, SCREEN_HEIGHT - 400, 100, 20, SNOW_WHITE)  # 中平台
  
            
            # 第三个垂直移动平台（关键，通往顶部）
            self.create_platform(550, SCREEN_HEIGHT - 520, 100, 15, FROST_BLUE, movable=True, vertical=True)
            
            # 第四层平台（顶层）- 大门平台
            gate_platform_width = 250
            gate_platform_x = SCREEN_WIDTH - gate_platform_width - 50
            gate_platform_y = SCREEN_HEIGHT - 550
            self.create_platform(gate_platform_x, gate_platform_y, gate_platform_width, 20, GLACIER_BLUE)
            
            # 宝石分布（沿着主要路径）
            self.create_gem(175, SCREEN_HEIGHT - 140)  # 出生平台
            self.create_gem(450, SCREEN_HEIGHT - 120)  # 第一层中平台
            self.create_gem(710, SCREEN_HEIGHT - 120)  # 第一层右平台
            
            self.create_gem(300, SCREEN_HEIGHT - 220)  # 垂直移动平台1上
            self.create_gem(200, SCREEN_HEIGHT - 300)  # 第二层左平台
            self.create_gem(750, SCREEN_HEIGHT - 300)  # 第二层右平台
            
            self.create_gem(625, SCREEN_HEIGHT - 420)  # 第三层中平台
            self.create_gem(500, SCREEN_HEIGHT - 500)  # 垂直移动平台3上
            
            # 大门 - 放在右上角的平台上
            gate_x = gate_platform_x + gate_platform_width // 2 - 30
            gate_y = gate_platform_y - 100
            self.door = Door(gate_x, gate_y, 100, 100)
            self.all_sprites.add(self.door)
                         
    def create_platform(self, x, y, width, height, color, movable=False, vertical=False):
        platform = Platform(x, y, width, height, color, movable, vertical)
        self.platforms.add(platform)
        self.all_sprites.add(platform)
        
    def create_spikes(self, x, y, count):
        for i in range(count):
            spike = Spike(x + i * 40, y)
            self.spikes.add(spike)
            self.all_sprites.add(spike)
            
    def create_gem(self, x, y):
        gem = Gem(x, y)
        self.gems.add(gem)
        self.all_sprites.add(gem)
    
    
    def draw_menu(self):
        # 绘制菜单背景
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill((30, 30, 60))

        # 绘制标题
        title_text = self.title_font.render("圣诞送礼物", True, BLACK)
        if title_text:
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(title_text, title_rect)
        
        # 绘制副标题
        subtitle_text = self.font.render("2D横版平台跳跃游戏", True, BLACK)
        if subtitle_text:
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(subtitle_text, subtitle_rect)
        
        # 绘制按钮
        self.start_button.draw(self.screen)
        self.instructions_button.draw(self.screen)
        self.exit_button.draw(self.screen)
        
        # 绘制操作说明
        controls_text = self.instructions_font.render("操作说明: 方向键移动, 空格键跳跃", True, BLACK)
        if controls_text:
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, 520))
            self.screen.blit(controls_text, controls_rect)
        
    def draw_level_select(self):
        # 绘制菜单背景
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill((30, 30, 60))
        
        # 绘制标题
        title_text = self.title_font.render("选择关卡", True, YELLOW)
        if title_text:
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(title_text, title_rect)
        
        # 绘制按钮
        self.level1_button.draw(self.screen)
        self.level2_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # 绘制关卡描述
        if self.level1_button.is_hovered():
            desc_text = "关卡 1: 入门难度，5个礼物，1组尖刺，1个移动平台"
        elif self.level2_button.is_hovered():
            desc_text = "关卡 2: 中等难度，8个礼物，2组尖刺，2个移动平台"
        else:
            desc_text = "选择一个关卡开始游戏"
            
        desc_surf = self.instructions_font.render(desc_text, True, BLACK)
        if desc_surf:
            desc_rect = desc_surf.get_rect(center=(SCREEN_WIDTH//2, 520))
            self.screen.blit(desc_surf, desc_rect)
    
    def draw_instructions(self):
        # 绘制菜单背景
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill((30, 30, 60))
        
        # 绘制标题
        title_text = self.title_font.render("游戏说明", True, YELLOW)
        if title_text:
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title_text, title_rect)
        
        # 绘制说明文本
        instructions = [
            "游戏目标: 收集关卡中的所有礼物，然后送到小屋中",
            "控制方式:",
            "  - 左右方向键: 左右移动",
            "  - 轻点空格: 小跳（跳得低），按住空格: 大跳（按住越久跳得越高）",
            "  - ESC键: 暂停游戏",
            "",
            "游戏规则:",
            "  - 你有3条生命，掉入虚空或碰到尖刺会失去一条生命",
            "  - 收集所有礼物后，小屋门会打开",
            "  - 有些平台会上下移动，注意时机",
            "",
            "收集与通关:",
            "  - 礼物: 收集目标",
            "  - 尖刺: 触碰会失去生命",
            "  - 圣诞小屋: 通关出口（收集所有礼物门会打开）"
        ]
        
        for i, line in enumerate(instructions):
            text_surf = self.instructions_font.render(line, True, BLACK)
            if text_surf:
                text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 140 + i*28))
                self.screen.blit(text_surf, text_rect)
        
        # 绘制返回按钮（右上角）
        self.instructions_back_button.draw(self.screen)
    
    def draw_playing(self):
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # 如果没有背景图片，使用原来的纯色背景
            self.screen.fill((100, 150, 200))
    
        
        # 绘制所有实体
        for sprite in self.all_sprites:
            if isinstance(sprite, Gem) and sprite.collected:
                continue
            self.screen.blit(sprite.image, sprite.rect)
        
        # 绘制宝石（礼物）（单独处理，因为有些可能已被收集）
        for gem in self.gems:
            if not gem.collected:
                self.screen.blit(gem.image, gem.rect)
        
        # 绘制UI信息
        # 生命值显示
        lives_text = self.font.render(f"生命: {self.lives}", True, WHITE)
        if lives_text:
            self.screen.blit(lives_text, (20, 20))
        
        # 宝石收集进度
        gems_text = self.font.render(f"礼物: {self.gems_collected}/{self.total_gems}", True, YELLOW)
        if gems_text:
            self.screen.blit(gems_text, (20, 60))
        
        # 关卡显示
        level_text = self.font.render(f"关卡: {self.current_level}", True, WHITE)
        if level_text:
            self.screen.blit(level_text, (20, 100))
        
        # 大门状态提示
        if self.gems_collected < self.total_gems:
            door_text = self.instructions_font.render("收集所有礼物打开圣诞小屋大门", True, WHITE)
        else:
            door_text = self.instructions_font.render("大门已打开！可以通关了", True, GREEN)
        
        if door_text:
            door_rect = door_text.get_rect(center=(SCREEN_WIDTH//2, 30))
            self.screen.blit(door_text, door_rect)
        
        # 移动平台提示
        if any(platform.movable for platform in self.platforms):
            platform_text = self.instructions_font.render("橙色平台会移动！可以站在上面一起移动", True, ORANGE)
            if platform_text:
                platform_rect = platform_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
                self.screen.blit(platform_text, platform_rect)
        
        # 暂停提示
        pause_text = self.instructions_font.render("按ESC键暂停游戏", True, WHITE)
        if pause_text:
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH - 100, 20))
            self.screen.blit(pause_text, pause_rect)
    
    def draw_win_screen(self):
        # 绘制菜单背景
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill((30, 60, 30))
        
        # 绘制胜利文本
        win_text = self.title_font.render("关卡通过！", True, YELLOW)
        if win_text:
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(win_text, win_rect)
        
        # 绘制收集信息
        gems_text = self.font.render(f"收集了 {self.gems_collected}/{self.total_gems} 个礼物", True, BLACK)
        if gems_text:
            gems_rect = gems_text.get_rect(center=(SCREEN_WIDTH//2, 220))
            self.screen.blit(gems_text, gems_rect)
        
        # 绘制剩余生命
        lives_text = self.font.render(f"剩余生命: {self.lives}", True, BLACK)
        if lives_text:
            lives_rect = lives_text.get_rect(center=(SCREEN_WIDTH//2, 270))
            self.screen.blit(lives_text, lives_rect)
        
        # 绘制按钮 - 重新排列避免重叠
        button_width = 200
        button_height = 60
        button_spacing = 20
        
        if self.current_level < 2:
            # 下一关按钮
            next_level_button = Button(
                SCREEN_WIDTH//2 - button_width//2, 
                330, 
                button_width, 
                button_height, 
                "下一关", 
                GREEN, 
                LIGHT_GREEN, 
                self.font
            )
            next_level_button.draw(self.screen)
            self.next_level_button = next_level_button
            
            # 重新开始按钮
            self.restart_button.rect.x = SCREEN_WIDTH//2 - button_width//2
            self.restart_button.rect.y = 330 + button_height + button_spacing
            self.restart_button.draw(self.screen)
            
            # 返回菜单按钮
            self.menu_button.rect.x = SCREEN_WIDTH//2 - button_width//2
            self.menu_button.rect.y = 330 + 2*(button_height + button_spacing)
            self.menu_button.draw(self.screen)
        else:
            # 所有关卡完成的情况
            complete_text = self.font.render("恭喜你完成了所有关卡！", True, YELLOW)
            if complete_text:
                complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 320))
                self.screen.blit(complete_text, complete_rect)
            
            self.restart_button.rect.x = SCREEN_WIDTH//2 - button_width//2
            self.restart_button.rect.y = 370
            self.restart_button.draw(self.screen)
            
            self.menu_button.rect.x = SCREEN_WIDTH//2 - button_width//2
            self.menu_button.rect.y = 370 + button_height + button_spacing
            self.menu_button.draw(self.screen)
    
    def draw_game_over(self):
        # 绘制菜单背景
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.screen.fill((60, 30, 30))
        
        # 绘制游戏结束文本
        game_over_text = self.title_font.render("游戏结束", True, RED)
        if game_over_text:
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(game_over_text, game_over_rect)
        
        # 绘制失败信息
        fail_text = self.font.render(f"你在关卡 {self.current_level} 失败了", True, WHITE)
        if fail_text:
            fail_rect = fail_text.get_rect(center=(SCREEN_WIDTH//2, 220))
            self.screen.blit(fail_text, fail_rect)
        
        # 绘制收集信息
        gems_text = self.font.render(f"收集了 {self.gems_collected}/{self.total_gems} 个礼物", True, WHITE)
        if gems_text:
            gems_rect = gems_text.get_rect(center=(SCREEN_WIDTH//2, 270))
            self.screen.blit(gems_text, gems_rect)
        
        # 绘制按钮
        button_width = 200
        button_height = 60
        button_spacing = 20
        
        self.restart_button.rect.x = SCREEN_WIDTH//2 - button_width//2
        self.restart_button.rect.y = 330
        self.restart_button.draw(self.screen)
        
        self.menu_button.rect.x = SCREEN_WIDTH//2 - button_width//2
        self.menu_button.rect.y = 330 + button_height + button_spacing
        self.menu_button.draw(self.screen)
    
    def draw_pause_screen(self):
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # 黑色半透明
        self.screen.blit(overlay, (0, 0))
        
        # 暂停标题
        pause_title = self.title_font.render("游戏暂停", True, YELLOW)
        if pause_title:
            title_rect = pause_title.get_rect(center=(SCREEN_WIDTH//2, 150))
            self.screen.blit(pause_title, title_rect)
        
        # 暂停提示
        pause_text = self.font.render("游戏已暂停", True, WHITE)
        if pause_text:
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, 220))
            self.screen.blit(pause_text, text_rect)
        
        # 绘制按钮
        self.resume_button.draw(self.screen)
        self.pause_menu_button.draw(self.screen)
        
        # 操作提示
        hint_text = self.instructions_font.render("按ESC键继续游戏", True, LIGHT_GRAY)
        if hint_text:
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH//2, 500))
            self.screen.blit(hint_text, hint_rect)

    def update_playing(self):
        # 更新移动平台
        for platform in self.platforms: 
            platform.update()
        
        # 更新玩家并检查碰撞
        result = self.player.update(self.platforms, self.spikes, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        if result == "fallen" or result == "spike_hit":
            self.lives -= 1
            if self.lives <= 0:
                self.state = GAME_OVER
            else:
                # 使用保存的出生点复活
                self.player.rect.x = self.birth_point[0]
                self.player.rect.y = self.birth_point[1]
                self.player.vel_y = 0
                self.player.on_moving_platform = None
                self.player.platform_velocity_x = 0
        
        # 检查宝石收集
        gems_hit = pygame.sprite.spritecollide(self.player, self.gems, False)
        for gem in gems_hit:
            if not gem.collected:
                gem.collected = True
                self.gems_collected += 1
                
                # 如果收集了所有宝石，打开大门
                if self.gems_collected >= self.total_gems and self.door:
                    self.door.open()
        
        # 检查是否到达大门
        if self.door and self.door.is_open and self.player.rect.colliderect(self.door.rect):
            self.state = WIN_SCREEN
            # 检查是否到达大门
            # 播放胜利音效
            self.play_victory_sound()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # ESC键处理
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == PLAYING:
                            self.state = PAUSED
                        elif self.state == PAUSED:
                            self.state = PLAYING

                # 处理菜单状态的事件
                if self.state == MENU:
                    self.start_button.update()
                    self.instructions_button.update()
                    self.exit_button.update()
                    
                    if self.start_button.is_clicked(event):
                        self.state = LEVEL_SELECT
                    elif self.instructions_button.is_clicked(event):
                        self.state = INSTRUCTIONS
                    elif self.exit_button.is_clicked(event):
                        running = False
                
                # 处理关卡选择状态的事件
                elif self.state == LEVEL_SELECT:
                    self.level1_button.update()
                    self.level2_button.update()
                    self.back_button.update()
                    
                    if self.level1_button.is_clicked(event):
                        self.current_level = 1
                        self.lives = 3
                        self.load_level(self.current_level)
                        self.state = PLAYING
                    elif self.level2_button.is_clicked(event):
                        self.current_level = 2
                        self.lives = 3
                        self.load_level(self.current_level)
                        self.state = PLAYING
                    elif self.back_button.is_clicked(event):
                        self.state = MENU
                
                # 处理游戏说明状态的事件
                elif self.state == INSTRUCTIONS:
                    self.instructions_back_button.update()
                    
                    if self.instructions_back_button.is_clicked(event):
                        self.state = MENU
                

                # 新增：处理暂停状态的事件
                elif self.state == PAUSED:
                    self.resume_button.update()
                    self.pause_menu_button.update()
                    
                    if self.resume_button.is_clicked(event):
                        self.stop_victory_sound()  # 停止音效
                        self.victory_sound_played = False  # 重置状态
                        self.lives = 3
                        self.load_level(self.current_level)
                        self.state = PLAYING
                    elif self.pause_menu_button.is_clicked(event):
                        self.stop_victory_sound()  # 停止音效
                        self.victory_sound_played = False  # 重置状态
                        self.state = MENU

                        # 检查下一关按钮点击
                    if hasattr(self, 'next_level_button') and self.current_level < 2:
                        self.next_level_button.update()
                        if self.next_level_button.is_clicked(event):
                            self.stop_victory_sound()  # 停止音效
                            self.victory_sound_played = False  # 重置状态
                            self.current_level += 1
                            self.lives = 3
                            self.load_level(self.current_level)
                            self.state = PLAYING

                # 处理游戏胜利状态的事件
                elif self.state == WIN_SCREEN:
                    self.restart_button.update()
                    self.menu_button.update()
                    
                    if self.restart_button.is_clicked(event):
                        self.lives = 3
                        self.load_level(self.current_level)
                        self.state = PLAYING
                    elif self.menu_button.is_clicked(event):
                        self.state = MENU
                    
                    # 检查下一关按钮点击
                    if hasattr(self, 'next_level_button') and self.current_level < 2:
                        self.next_level_button.update()
                        if self.next_level_button.is_clicked(event):
                            self.current_level += 1
                            self.lives = 3
                            self.load_level(self.current_level)
                            self.state = PLAYING
                
                # 处理游戏结束状态的事件
                elif self.state == GAME_OVER:
                    self.restart_button.update()
                    self.menu_button.update()
                    
                    if self.restart_button.is_clicked(event):
                        self.lives = 3
                        self.load_level(self.current_level)
                        self.state = PLAYING
                    elif self.menu_button.is_clicked(event):
                        self.state = MENU
            
            # 更新游戏状态
            if self.state == PLAYING:
                self.update_playing()
            
            # 绘制当前状态的界面
            if self.state == MENU:
                self.draw_menu()
            elif self.state == LEVEL_SELECT:
                self.draw_level_select()
            elif self.state == INSTRUCTIONS:
                self.draw_instructions()
            elif self.state == PLAYING:
                self.draw_playing()
            elif self.state == PAUSED:
                self.draw_playing()  # 先绘制游戏画面
                self.draw_pause_screen()  # 再绘制暂停界面
            elif self.state == WIN_SCREEN:
                self.draw_win_screen()
            elif self.state == GAME_OVER:
                self.draw_game_over()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()