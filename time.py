import traceback
import math
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSettings, QTimer, QTime, QDate, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontDatabase, QLinearGradient, QRadialGradient, \
    QPainterPath
import tkinter as tk
from tkinter import messagebox, ttk, colorchooser
import os
import sys

from plugin_base import PluginBase


class ModernTimeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {}
        self.animation_phase = 0
        self.glow_intensity = 0.5
        self.pulse_direction = 1

        # 动画属性
        self._opacity = 1.0
        self._scale = 1.0

        # 设置动画定时器
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.update_glow)
        self.glow_timer.start(50)  # 20fps for smooth animation

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.update()

    def update_glow(self):
        """更新发光效果"""
        self.glow_intensity += 0.02 * self.pulse_direction
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.pulse_direction = -1
        elif self.glow_intensity <= 0.3:
            self.glow_intensity = 0.3
            self.pulse_direction = 1

        self.animation_phase = (self.animation_phase + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # 应用透明度和缩放
        painter.setOpacity(self._opacity)

        # 缩放变换
        center = self.rect().center()
        painter.translate(center)
        painter.scale(self._scale, self._scale)
        painter.translate(-center)

        # 获取当前时间和日期
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()

        # 构建时间字符串
        if self.settings.get('time_format', '24h') == '12h':
            time_str = current_time.toString('h:mm')
            if self.settings.get('show_seconds', True):
                time_str += f":{current_time.toString('ss')}"
            time_str += f" {current_time.toString('AP')}"
        else:
            time_str = current_time.toString('HH:mm')
            if self.settings.get('show_seconds', True):
                time_str += f":{current_time.toString('ss')}"

        # 构建日期字符串
        date_str = ""
        if self.settings.get('show_date', True):
            date_str = current_date.toString('yyyy年MM月dd日 dddd')

        # 绘制现代化背景
        self.draw_modern_background(painter)

        # 绘制时间文字
        self.draw_time_text(painter, time_str, date_str)

        # 绘制装饰元素
        self.draw_decorative_elements(painter)

        painter.end()

    def draw_modern_background(self, painter):
        """绘制现代化背景"""
        rect = self.rect()

        # 创建渐变背景
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())

        # 根据时间改变背景颜色
        current_hour = QTime.currentTime().hour()
        if 6 <= current_hour < 12:  # 早晨
            gradient.setColorAt(0, QColor(255, 183, 77, int(self.settings.get('background_alpha', 50))))
            gradient.setColorAt(1, QColor(255, 138, 101, int(self.settings.get('background_alpha', 50))))
        elif 12 <= current_hour < 18:  # 下午
            gradient.setColorAt(0, QColor(74, 144, 226, int(self.settings.get('background_alpha', 50))))
            gradient.setColorAt(1, QColor(80, 170, 255, int(self.settings.get('background_alpha', 50))))
        elif 18 <= current_hour < 22:  # 傍晚
            gradient.setColorAt(0, QColor(255, 94, 77, int(self.settings.get('background_alpha', 50))))
            gradient.setColorAt(1, QColor(255, 154, 0, int(self.settings.get('background_alpha', 50))))
        else:  # 夜晚
            gradient.setColorAt(0, QColor(44, 62, 80, int(self.settings.get('background_alpha', 50))))
            gradient.setColorAt(1, QColor(76, 84, 102, int(self.settings.get('background_alpha', 50))))

        # 绘制主背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))

        # 创建圆角矩形路径
        path = QPainterPath()
        radius = self.settings.get('border_radius', 20)
        painter.drawPath(path)

        # 绘制发光边框
        if self.settings.get('use_glow', True):
            glow_color = QColor(self.settings.get('color', '#FFFFFF'))
            glow_color.setAlpha(int(80 * self.glow_intensity))

            pen = QPen(glow_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

            # 外层发光
            for i in range(3):
                glow_color.setAlpha(int(30 * self.glow_intensity / (i + 1)))
                pen = QPen(glow_color, 1)
                painter.setPen(pen)
                expanded_rect = rect.adjusted(-i - 1, -i - 1, i + 1, i + 1)
                path_expanded = QPainterPath()

                painter.drawPath(path_expanded)

    def draw_time_text(self, painter, time_str, date_str):
        """绘制时间文字"""
        rect = self.rect()

        # 设置时间字体
        time_font = QFont(self.settings.get('font_family', 'Arial'))
        time_font.setPointSize(self.settings.get('font_size', 48))
        time_font.setWeight(QFont.Bold)
        time_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)

        # 创建文字发光效果
        if self.settings.get('use_shadow', True):
            # 绘制多层阴影实现发光效果
            shadow_colors = [
                QColor(0, 0, 0, 100),
                QColor(0, 0, 0, 60),
                QColor(0, 0, 0, 30)
            ]

            offsets = [(3, 3), (2, 2), (1, 1)]

            for shadow_color, (dx, dy) in zip(shadow_colors, offsets):
                painter.setPen(shadow_color)
                painter.setFont(time_font)

                # 计算居中位置
                fm = painter.fontMetrics()
                text_width = fm.width(time_str)
                text_height = fm.height()

                x = (rect.width() - text_width) // 2 + dx
                y = (rect.height() - text_height) // 2 + text_height // 2 + dy

                painter.drawText(x, y, time_str)

        # 绘制主文字
        text_color = QColor(self.settings.get('color', '#FFFFFF'))

        # 添加时间变化的颜色效果
        if self.settings.get('dynamic_color', True):
            hue = (self.animation_phase + QTime.currentTime().second() * 6) % 360
            text_color = QColor.fromHsv(hue, 100, 255)

        painter.setPen(text_color)
        painter.setFont(time_font)

        # 计算居中位置
        fm = painter.fontMetrics()
        text_width = fm.width(time_str)
        text_height = fm.height()

        x = (rect.width() - text_width) // 2
        y = (rect.height() - text_height) // 2 + text_height // 2

        painter.drawText(x, y, time_str)

        # 绘制日期
        if date_str:
            date_font = QFont(self.settings.get('font_family', 'Arial'))
            date_font.setPointSize(int(self.settings.get('font_size', 48) * 0.35))
            date_font.setWeight(QFont.Normal)
            painter.setFont(date_font)

            date_color = QColor(text_color)
            date_color.setAlpha(200)
            painter.setPen(date_color)

            fm_date = painter.fontMetrics()
            date_width = fm_date.width(date_str)

            date_x = (rect.width() - date_width) // 2
            date_y = y + 40

            painter.drawText(date_x, date_y, date_str)

    def draw_decorative_elements(self, painter):
        """绘制装饰元素"""
        if not self.settings.get('show_decorations', True):
            return

        rect = self.rect()

        # 绘制角落装饰
        corner_size = 15
        corner_color = QColor(self.settings.get('color', '#FFFFFF'))
        corner_color.setAlpha(int(100 * self.glow_intensity))

        painter.setPen(Qt.NoPen)
        painter.setBrush(corner_color)

        # 左上角
        painter.drawEllipse(10, 10, corner_size, corner_size)

        # 右上角
        painter.drawEllipse(rect.width() - corner_size - 10, 10, corner_size, corner_size)

        # 左下角
        painter.drawEllipse(10, rect.height() - corner_size - 10, corner_size, corner_size)

        # 右下角
        painter.drawEllipse(rect.width() - corner_size - 10, rect.height() - corner_size - 10, corner_size, corner_size)

        # 绘制中心装饰线
        center_y = rect.height() // 2
        line_color = QColor(self.settings.get('color', '#FFFFFF'))
        line_color.setAlpha(int(50 * self.glow_intensity))

        pen = QPen(line_color, 2)
        painter.setPen(pen)

        # 左侧装饰线
        painter.drawLine(20, center_y, 60, center_y)

        # 右侧装饰线
        painter.drawLine(rect.width() - 60, center_y, rect.width() - 20, center_y)


class TimeDisplayPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "现代时间显示插件"
        self.version = "2.0.0"
        self.description = "美观现代的桌面时间显示插件，支持动态效果和主题切换"
        self.author = "LiangYu"
        self.settings = {
            'show_seconds': True,
            'show_date': True,
            'font_size': 48,
            'font_family': 'Arial',
            'time_format': '24h',
            'color': '#FFFFFF',
            'background_alpha': 60,
            'position_x': 100,
            'position_y': 100,
            'border_radius': 20,
            'use_shadow': True,
            'use_glow': True,
            'dynamic_color': False,
            'show_decorations': True,
            'animation_enabled': True,
            'theme': 'auto'  # auto, morning, afternoon, evening, night
        }
        self.widget = None
        self.timer = None
        self.fade_animation = None

    def initialize(self, app_instance):
        print(f"[{self.name}] 插件初始化")
        self.app = app_instance

        # 从QSettings加载保存的设置
        settings = QSettings("VideoWallpaper", "PluginSettings")
        settings.beginGroup(f"plugins/{self.name}")

        # 加载设置
        for key, default_value in self.settings.items():
            if isinstance(default_value, bool):
                self.settings[key] = settings.value(key, default_value, type=bool)
            elif isinstance(default_value, int):
                self.settings[key] = settings.value(key, default_value, type=int)
            else:
                self.settings[key] = settings.value(key, default_value, type=str)

        settings.endGroup()

    def on_wallpaper_start(self, video_path, loop):
        print(f"[{self.name}] 壁纸启动: {os.path.basename(video_path)}")
        self.start_timer()

    def on_wallpaper_stop(self):
        print(f"[{self.name}] 壁纸停止")
        self.stop_timer()
        if self.widget:
            self.fade_out_widget()

    def on_settings_changed(self, settings):
        print(f"[{self.name}] 设置已更改")
        self.settings.update(settings)
        if self.widget:
            self.widget.settings = self.settings
            self.widget.update()

    def start_timer(self):
        if self.timer:
            self.timer.stop()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

    def show_settings_dialog(self):
        root = tk.Tk()
        root.title(f"{self.name} 设置")
        root.geometry("500x700")
        root.configure(bg='#2c3e50')

        # 设置现代化样式
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义样式
        style.configure('Modern.TNotebook', background='#34495e')
        style.configure('Modern.TFrame', background='#34495e')
        style.configure('Modern.TLabel', background='#34495e', foreground='#ecf0f1')
        style.configure('Modern.TButton', background='#3498db', foreground='white')

        # 创建选项卡
        tab_control = ttk.Notebook(root, style='Modern.TNotebook')

        # 时间显示选项卡
        time_tab = ttk.Frame(tab_control, style='Modern.TFrame')
        tab_control.add(time_tab, text="时间显示")

        # 外观选项卡
        appearance_tab = ttk.Frame(tab_control, style='Modern.TFrame')
        tab_control.add(appearance_tab, text="外观设置")

        # 动效选项卡
        effects_tab = ttk.Frame(tab_control, style='Modern.TFrame')
        tab_control.add(effects_tab, text="动效设置")

        # 位置选项卡
        position_tab = ttk.Frame(tab_control, style='Modern.TFrame')
        tab_control.add(position_tab, text="位置调整")

        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # 时间显示选项
        ttk.Label(time_tab, text="显示秒数:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        show_seconds_var = tk.BooleanVar(value=self.settings['show_seconds'])
        ttk.Checkbutton(time_tab, variable=show_seconds_var).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(time_tab, text="显示日期:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        show_date_var = tk.BooleanVar(value=self.settings['show_date'])
        ttk.Checkbutton(time_tab, variable=show_date_var).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(time_tab, text="时间格式:", style='Modern.TLabel').grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        time_format_var = tk.StringVar(value=self.settings['time_format'])
        ttk.Radiobutton(time_tab, text="24小时制", variable=time_format_var, value="24h").grid(row=2, column=1,
                                                                                               sticky=tk.W, padx=10,
                                                                                               pady=5)
        ttk.Radiobutton(time_tab, text="12小时制", variable=time_format_var, value="12h").grid(row=3, column=1,
                                                                                               sticky=tk.W, padx=10,
                                                                                               pady=5)

        # 外观选项
        ttk.Label(appearance_tab, text="字体大小:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10,
                                                                                pady=5)
        font_size_var = tk.IntVar(value=self.settings['font_size'])
        ttk.Scale(appearance_tab, from_=24, to=96, orient=tk.HORIZONTAL, variable=font_size_var, length=200).grid(row=0,
                                                                                                                  column=1,
                                                                                                                  padx=10,
                                                                                                                  pady=5)
        size_label = ttk.Label(appearance_tab, text=str(font_size_var.get()), style='Modern.TLabel')
        size_label.grid(row=0, column=2, padx=5, pady=5)

        def update_size_label(*args):
            size_label.config(text=str(font_size_var.get()))

        font_size_var.trace('w', update_size_label)

        # 字体选择
        available_fonts = ["Arial", "Microsoft YaHei", "SimHei", "Helvetica", "Times New Roman", "Consolas",
                           "Comic Sans MS"]
        ttk.Label(appearance_tab, text="字体:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10,
                                                                            pady=5)
        font_family_var = tk.StringVar(value=self.settings['font_family'])
        font_combo = ttk.Combobox(appearance_tab, textvariable=font_family_var, values=available_fonts, width=20)
        font_combo.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # 颜色选择
        ttk.Label(appearance_tab, text="文字颜色:", style='Modern.TLabel').grid(row=2, column=0, sticky=tk.W, padx=10,
                                                                                pady=5)
        color_var = tk.StringVar(value=self.settings['color'])
        color_frame = tk.Frame(appearance_tab, bg=self.settings['color'], width=30, height=20)
        color_frame.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        def choose_color():
            color = colorchooser.askcolor(initialcolor=color_var.get())[1]
            if color:
                color_var.set(color)
                color_frame.config(bg=color)

        ttk.Button(appearance_tab, text="选择", command=choose_color).grid(row=2, column=2, padx=5, pady=5)

        # 背景透明度
        ttk.Label(appearance_tab, text="背景透明度:", style='Modern.TLabel').grid(row=3, column=0, sticky=tk.W, padx=10,
                                                                                  pady=5)
        bg_alpha_var = tk.IntVar(value=self.settings['background_alpha'])
        ttk.Scale(appearance_tab, from_=0, to=255, orient=tk.HORIZONTAL, variable=bg_alpha_var, length=200).grid(row=3,
                                                                                                                 column=1,
                                                                                                                 padx=10,
                                                                                                                 pady=5)
        alpha_label = ttk.Label(appearance_tab, text=str(bg_alpha_var.get()), style='Modern.TLabel')
        alpha_label.grid(row=3, column=2, padx=5, pady=5)

        def update_alpha_label(*args):
            alpha_label.config(text=str(bg_alpha_var.get()))

        bg_alpha_var.trace('w', update_alpha_label)

        # 圆角半径
        ttk.Label(appearance_tab, text="圆角半径:", style='Modern.TLabel').grid(row=4, column=0, sticky=tk.W, padx=10,
                                                                                pady=5)
        border_radius_var = tk.IntVar(value=self.settings['border_radius'])
        ttk.Scale(appearance_tab, from_=0, to=50, orient=tk.HORIZONTAL, variable=border_radius_var, length=200).grid(
            row=4, column=1, padx=10, pady=5)
        radius_label = ttk.Label(appearance_tab, text=str(border_radius_var.get()), style='Modern.TLabel')
        radius_label.grid(row=4, column=2, padx=5, pady=5)

        def update_radius_label(*args):
            radius_label.config(text=str(border_radius_var.get()))

        border_radius_var.trace('w', update_radius_label)

        # 动效选项
        ttk.Label(effects_tab, text="启用动画:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10,
                                                                             pady=5)
        animation_var = tk.BooleanVar(value=self.settings['animation_enabled'])
        ttk.Checkbutton(effects_tab, variable=animation_var).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(effects_tab, text="文字阴影:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10,
                                                                             pady=5)
        use_shadow_var = tk.BooleanVar(value=self.settings['use_shadow'])
        ttk.Checkbutton(effects_tab, variable=use_shadow_var).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(effects_tab, text="发光效果:", style='Modern.TLabel').grid(row=2, column=0, sticky=tk.W, padx=10,
                                                                             pady=5)
        use_glow_var = tk.BooleanVar(value=self.settings['use_glow'])
        ttk.Checkbutton(effects_tab, variable=use_glow_var).grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(effects_tab, text="动态颜色:", style='Modern.TLabel').grid(row=3, column=0, sticky=tk.W, padx=10,
                                                                             pady=5)
        dynamic_color_var = tk.BooleanVar(value=self.settings['dynamic_color'])
        ttk.Checkbutton(effects_tab, variable=dynamic_color_var).grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(effects_tab, text="显示装饰:", style='Modern.TLabel').grid(row=4, column=0, sticky=tk.W, padx=10,
                                                                             pady=5)
        show_decorations_var = tk.BooleanVar(value=self.settings['show_decorations'])
        ttk.Checkbutton(effects_tab, variable=show_decorations_var).grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)

        # 位置选项
        ttk.Label(position_tab, text="X 坐标:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=10,
                                                                            pady=5)
        x_pos_var = tk.IntVar(value=self.settings['position_x'])
        ttk.Entry(position_tab, textvariable=x_pos_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        ttk.Label(position_tab, text="Y 坐标:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, padx=10,
                                                                            pady=5)
        y_pos_var = tk.IntVar(value=self.settings['position_y'])
        ttk.Entry(position_tab, textvariable=y_pos_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        def save_settings():
            new_settings = {
                'show_seconds': show_seconds_var.get(),
                'show_date': show_date_var.get(),
                'font_size': font_size_var.get(),
                'font_family': font_family_var.get(),
                'time_format': time_format_var.get(),
                'color': color_var.get(),
                'background_alpha': bg_alpha_var.get(),
                'position_x': x_pos_var.get(),
                'position_y': y_pos_var.get(),
                'border_radius': border_radius_var.get(),
                'use_shadow': use_shadow_var.get(),
                'use_glow': use_glow_var.get(),
                'dynamic_color': dynamic_color_var.get(),
                'show_decorations': show_decorations_var.get(),
                'animation_enabled': animation_var.get()
            }

            # 保存设置
            settings = QSettings("VideoWallpaper", "PluginSettings")
            settings.beginGroup(f"plugins/{self.name}")
            for key, value in new_settings.items():
                settings.setValue(key, value)
            settings.endGroup()

            self.settings.update(new_settings)

            if self.widget:
                self.widget.settings = self.settings
                self.widget.move(self.settings['position_x'], self.settings['position_y'])
                self.widget.update()

            messagebox.showinfo("保存成功", "设置已保存并应用")
            root.destroy()

        # 保存按钮
        button_frame = tk.Frame(root, bg='#2c3e50')
        button_frame.pack(fill='x', padx=10, pady=10)

        save_button = tk.Button(button_frame, text="保存设置", command=save_settings,
                                bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                                relief='flat', padx=20, pady=8)
        save_button.pack(side='right', padx=5)

        cancel_button = tk.Button(button_frame, text="取消", command=root.destroy,
                                  bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'),
                                  relief='flat', padx=20, pady=8)
        cancel_button.pack(side='right', padx=5)

        root.mainloop()

    def operate_on_window(self, window):
        """在壁纸上显示现代化时间控件"""
        try:
            # 创建现代化时间控件
            self.widget = ModernTimeWidget(window)
            self.widget.settings = self.settings

            # 设置控件位置和大小
            self.widget.setGeometry(
                self.settings['position_x'],
                self.settings['position_y'],
                400,
                200
            )

            # 设置窗口属性
            self.widget.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.SubWindow
            )
            self.widget.setAttribute(Qt.WA_TranslucentBackground, True)

            # 添加阴影效果
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 5)
            self.widget.setGraphicsEffect(shadow)

            # 设置拖拽功能
            self.setup_drag_functionality()

            # 设置右键菜单
            self.setup_context_menu()

            # 淡入动画
            self.fade_in_widget()

            print(f"[{self.name}] 现代化时间显示插件已启动")
        except Exception as e:
            print(f"[{self.name}] 显示时间时出错: {e}")
            traceback.print_exc()

    def setup_drag_functionality(self):
        """设置拖拽功能"""

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.widget.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(event):
            if event.buttons() & Qt.LeftButton:
                new_pos = event.globalPos() - self.drag_position
                self.widget.move(new_pos)
                self.settings['position_x'] = self.widget.x()
                self.settings['position_y'] = self.widget.y()
                event.accept()

        def mouseDoubleClickEvent(event):
            """双击切换主题"""
            if event.button() == Qt.LeftButton:
                self.cycle_theme()
                event.accept()

        self.widget.mousePressEvent = mousePressEvent
        self.widget.mouseMoveEvent = mouseMoveEvent
        self.widget.mouseDoubleClickEvent = mouseDoubleClickEvent

    def setup_context_menu(self):
        """设置右键菜单"""

        def contextMenuEvent(event):
            from PyQt5.QtWidgets import QMenu, QAction

            menu = QMenu()
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 1px solid #34495e;
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    border-radius: 3px;
                }
                QMenu::item:selected {
                    background-color: #3498db;
                }
            """)

            # 设置菜单
            settings_action = QAction("⚙️ 设置", self.widget)
            settings_action.triggered.connect(self.show_settings_dialog)
            menu.addAction(settings_action)

            # 主题切换
            theme_action = QAction("🎨 切换主题", self.widget)
            theme_action.triggered.connect(self.cycle_theme)
            menu.addAction(theme_action)

            menu.addSeparator()

            # 透明度调整
            opacity_menu = menu.addMenu("🔍 透明度")
            for opacity in [0.3, 0.5, 0.7, 0.9, 1.0]:
                action = QAction(f"{int(opacity * 100)}%", self.widget)
                action.triggered.connect(lambda checked, o=opacity: self.set_opacity(o))
                opacity_menu.addAction(action)

            menu.addSeparator()

            # 关闭选项
            close_action = QAction("❌ 关闭插件", self.widget)
            close_action.triggered.connect(self.close_widget)
            menu.addAction(close_action)

            menu.exec_(event.globalPos())

        self.widget.contextMenuEvent = contextMenuEvent

    def cycle_theme(self):
        """循环切换主题"""
        themes = {
            'morning': {'color': '#ff6b35', 'bg_alpha': 70},
            'afternoon': {'color': '#4a90e2', 'bg_alpha': 80},
            'evening': {'color': '#ff5e5b', 'bg_alpha': 90},
            'night': {'color': '#7b68ee', 'bg_alpha': 60},
            'neon': {'color': '#00ffff', 'bg_alpha': 50, 'dynamic_color': True},
            'elegant': {'color': '#ffd700', 'bg_alpha': 40}
        }

        theme_names = list(themes.keys())
        current_theme = getattr(self, 'current_theme', 'morning')

        try:
            current_index = theme_names.index(current_theme)
            next_index = (current_index + 1) % len(theme_names)
        except ValueError:
            next_index = 0

        next_theme = theme_names[next_index]
        theme_settings = themes[next_theme]

        self.settings.update(theme_settings)
        self.current_theme = next_theme

        if self.widget:
            self.widget.settings = self.settings
            self.widget.update()

        print(f"[{self.name}] 切换到主题: {next_theme}")

    def set_opacity(self, opacity):
        """设置透明度"""
        if self.widget:
            self.widget.setWindowOpacity(opacity)

    def fade_in_widget(self):
        """淡入动画"""
        if not self.settings.get('animation_enabled', True):
            self.widget.show()
            return

        self.widget.show()

        self.fade_animation = QPropertyAnimation(self.widget, b"opacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

    def fade_out_widget(self):
        """淡出动画"""
        if not self.widget:
            return

        if not self.settings.get('animation_enabled', True):
            self.widget.close()
            self.widget = None
            return

        self.fade_animation = QPropertyAnimation(self.widget, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_animation.finished.connect(self.widget.close)
        self.fade_animation.finished.connect(lambda: setattr(self, 'widget', None))
        self.fade_animation.start()

    def update_time(self):
        """更新时间显示"""
        if self.widget:
            self.widget.update()

    def close_widget(self):
        """关闭控件"""
        self.stop_timer()
        if self.widget:
            self.fade_out_widget()
            print(f"[{self.name}] 控件已关闭")


def create_plugin():
    return TimeDisplayPlugin()
