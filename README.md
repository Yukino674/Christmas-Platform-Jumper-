# 圣诞送礼物 - 2D 平台跳跃小游戏

一个基于 Pygame 的横版平台跳跃游戏，包含关卡选择、收集礼物、移动平台、尖刺伤害、暂停/胜利/失败界面与简易音效支持。内置跨平台中文字体加载逻辑。

没下载代码前可将game.zip解压，再点击game.exe可以试玩小游戏


## 目录结构
- main.py：程序入口，启动游戏循环
- game.py：游戏主逻辑（状态机、关卡加载、绘制/更新、音效与背景）
- entities.py：实体类（Player, Platform, Gem, Spike, Door）
- ui.py：UI 组件与字体加载（Button, load_font）
- constants.py：常量与颜色、游戏状态值
- 资源文件（与代码同目录）：
  - 背景：background.png、menu_bg.png（可选）
  - 角色：player.png
  - 礼物：gem.png
  - 大门：door_closed.png、door_open.png
  - 音效：victory.mp3 或 victory.wav 或 victory.ogg（至少其一）

## 环境与依赖
- Python 3.8+
- Pygame 2.1+
- Windows/macOS/Linux 均可

安装依赖：
```
pip install pygame
```

## 运行
```
python main.py
```
若无声音或报“音频初始化失败”，游戏仍可继续（将静音运行）。

## 操作说明
- 方向键左右：移动
- 空格：按一下小跳；长按逐渐增大跳跃力度（大小跳）
- ESC：暂停/继续
- 鼠标：点击按钮进行菜单操作

## 游戏机制与状态
- 生命：初始 3 条，掉出屏幕或碰到尖刺减一；为 0 时 Game Over
- 收集：收集所有礼物后，大门开启，进入门判定胜利
- 移动平台：橙色平台可上下/左右移动，可站在其上
- 状态流转：
  - MENU（主菜单）
  - LEVEL_SELECT（关卡选择）
  - INSTRUCTIONS（游戏说明）
  - PLAYING（游戏中）
  - PAUSED（暂停）
  - WIN_SCREEN（胜利界面）
  - GAME_OVER（失败界面）

## 关键模块说明
- constants.py
  - 屏幕尺寸、FPS、颜色、状态常量
  - clamp_color(value)：颜色值安全裁剪
- ui.py
  - load_font(font_size)：多平台字体路径尝试，失败回退系统默认字体
  - Button：draw/update/is_clicked/is_hovered 基础按钮组件
- entities.py
  - Player：移动、大小跳、与平台/尖刺碰撞；支持移动平台跟随
  - Platform：固定/移动平台（支持垂直/水平往返）
  - Gem：可收集礼物
  - Spike：三角形尖刺伤害
  - Door：关闭/开启两态
- game.py
  - Game：状态机、关卡加载、音效播放、背景绘制、界面与事件处理
  - load_level(n)：按关卡号布置平台/礼物/尖刺/出生点/大门
  - scale_keep_ratio：按比例缩放图像并居中
  - play_victory_sound/stop_victory_sound：胜利音效控制
  - draw_xxx/update_playing：各状态绘制与游戏中逻辑

## 资源放置与命名
请将下列文件放在与代码同目录：
- 背景图：background.png、menu_bg.png
- 角色：player.png
- 礼物：gem.png
- 大门：door_closed.png、door_open.png
- 音效（任选其一存在即可）：victory.mp3 / victory.wav / victory.ogg

缺失资源时将回退为纯色或提示信息；字体会自动回退系统默认字体。

## 扩展关卡（快速指南）
1. 在 game.Game.load_level 中新增分支（例如 level_num == 3）。
2. 设置 self.total_gems，清空并创建平台/尖刺/礼物：
   - create_platform(x, y, w, h, color, movable=False, vertical=False)
   - create_spikes(x, y, count)
   - create_gem(x, y)
3. 设置出生平台与 self.birth_point，并创建 Player。
4. 放置 Door 并加入其它实体。
5. 若需要在关卡选择页展示按钮，请在 draw_level_select 与事件处理里增添按钮与点击逻辑。

## 常见问题
- 字体中文显示为方块
  - 将 simhei.ttf 放到程序目录，或在 ui.load_font 的 font_paths 中添加本机字体路径
- 背景或图片未显示
  - 确认文件名与大小写一致，图片与脚本处于同一目录
- 无法播放音效或报错
  - 确认存在 victory.mp3 且系统音频可用；失败时会自动静音继续
- 黑屏或无响应
  - 请确保 pygame 版本正确；首次运行可能较慢，耐心等待窗口初始化


