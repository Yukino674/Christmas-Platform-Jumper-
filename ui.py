import os
from constants import *

# 加载字体函数
def load_font(font_size):
    # 尝试使用系统字体
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "simhei.ttf",
    ]
    
    for font_path in font_paths:
        try:
            if font_path and os.path.exists(font_path):
                return pygame.font.Font(font_path, font_size)
        except:
            continue
    
    # 如果都没找到，直接使用默认字体
    return pygame.font.SysFont(None, font_size)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None):
        #x : 按钮左上角的 x 坐标；y : 按钮左上角的 y 坐标
        #color : 按钮的默认颜色；hover_color 鼠标悬停时按钮的颜色
        #font : 按钮文本的字体
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        if font:
            self.font = font
        else:
            self.font = load_font(36)

    #绘制按钮到屏幕上    
    def draw(self, screen):
        # 绘制按钮的矩形区域
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        # 绘制按钮的边框
        pygame.draw.rect(screen, WHITE, self.rect, 3, border_radius=10)
        # 绘制按钮上的文本
        text_surf = self.font.render(self.text, True, WHITE)    # 渲染文本
        text_rect = text_surf.get_rect(center=self.rect.center) # 文本居中对齐
        screen.blit(text_surf, text_rect)   # 将文本绘制到屏幕上

    #检查鼠标是否悬停在按钮上    
    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    #更新按钮的状态（颜色变化）    
    def update(self):
        if self.is_hovered():
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    #检查按钮是否被点击        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False