import traceback
from PyQt5.QtWidgets import QWidget, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os

from plugin_base import PluginBase


class NotePadPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "桌面记事本"
        self.version = "1.0.0"
        self.description = "在桌面上显示可编辑的记事本"
        self.author = "Assistant"
        self.settings = {
            'note_content': '这是一个桌面记事本\n\n你可以在设置中编辑内容\n\n支持多行文本显示',
            'font_size': 12,
            'text_color': '#000000',
            'background_color': '#FFFACD',
            'position_x': 100,
            'position_y': 100,
            'width': 300,
            'height': 400
        }
        self.widget = None

    def initialize(self, app_instance):
        print(f"[{self.name}] 插件初始化")
        self.app = app_instance
        
        # 从QSettings加载保存的设置
        settings = QSettings("VideoWallpaper", "PluginSettings")
        settings.beginGroup(f"plugins/{self.name}")
        
        # 加载每个设置，如果不存在则使用默认值
        self.settings['note_content'] = settings.value('note_content', self.settings['note_content'], type=str)
        self.settings['font_size'] = settings.value('font_size', self.settings['font_size'], type=int)
        self.settings['text_color'] = settings.value('text_color', self.settings['text_color'], type=str)
        self.settings['background_color'] = settings.value('background_color', self.settings['background_color'], type=str)
        self.settings['position_x'] = settings.value('position_x', self.settings['position_x'], type=int)
        self.settings['position_y'] = settings.value('position_y', self.settings['position_y'], type=int)
        self.settings['width'] = settings.value('width', self.settings['width'], type=int)
        self.settings['height'] = settings.value('height', self.settings['height'], type=int)
        
        settings.endGroup()

    def on_wallpaper_start(self, video_path, loop):
        print(f"[{self.name}] 壁纸启动: {os.path.basename(video_path)}")

    def on_wallpaper_stop(self):
        print(f"[{self.name}] 壁纸停止")
        if self.widget:
            self.widget.close()
            self.widget = None

    def on_settings_changed(self, settings):
        print(f"[{self.name}] 设置已更改")

    def show_settings_dialog(self):
        root = tk.Tk()
        root.title(f"{self.name} 设置")
        root.geometry("500x600")

        # 记事本内容
        tk.Label(root, text="记事本内容:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        content_text = scrolledtext.ScrolledText(root, height=15, width=60)
        content_text.insert(tk.END, self.settings.get('note_content', ''))
        content_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # 设置区域
        settings_frame = tk.Frame(root)
        settings_frame.pack(pady=10, padx=10, fill=tk.X)

        # 字体大小
        tk.Label(settings_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        font_size_entry = tk.Entry(settings_frame, width=15)
        font_size_entry.insert(0, str(self.settings.get('font_size', 12)))
        font_size_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        # 文本颜色
        tk.Label(settings_frame, text="文本颜色:").grid(row=0, column=2, sticky=tk.W, pady=2)
        text_color_entry = tk.Entry(settings_frame, width=15)
        text_color_entry.insert(0, self.settings.get('text_color', '#000000'))
        text_color_entry.grid(row=0, column=3, sticky=tk.W, padx=5)

        # 背景颜色
        tk.Label(settings_frame, text="背景颜色:").grid(row=1, column=0, sticky=tk.W, pady=2)
        bg_color_entry = tk.Entry(settings_frame, width=15)
        bg_color_entry.insert(0, self.settings.get('background_color', '#FFFACD'))
        bg_color_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 20))

        # 位置设置
        tk.Label(settings_frame, text="X位置:").grid(row=1, column=2, sticky=tk.W, pady=2)
        x_entry = tk.Entry(settings_frame, width=15)
        x_entry.insert(0, str(self.settings.get('position_x', 100)))
        x_entry.grid(row=1, column=3, sticky=tk.W, padx=5)

        tk.Label(settings_frame, text="Y位置:").grid(row=2, column=0, sticky=tk.W, pady=2)
        y_entry = tk.Entry(settings_frame, width=15)
        y_entry.insert(0, str(self.settings.get('position_y', 100)))
        y_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 20))

        # 尺寸设置
        tk.Label(settings_frame, text="宽度:").grid(row=2, column=2, sticky=tk.W, pady=2)
        width_entry = tk.Entry(settings_frame, width=15)
        width_entry.insert(0, str(self.settings.get('width', 300)))
        width_entry.grid(row=2, column=3, sticky=tk.W, padx=5)

        tk.Label(settings_frame, text="高度:").grid(row=3, column=0, sticky=tk.W, pady=2)
        height_entry = tk.Entry(settings_frame, width=15)
        height_entry.insert(0, str(self.settings.get('height', 400)))
        height_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 20))

        def save_settings():
            try:
                new_settings = {
                    'note_content': content_text.get(1.0, tk.END).strip(),
                    'font_size': int(font_size_entry.get()),
                    'text_color': text_color_entry.get(),
                    'background_color': bg_color_entry.get(),
                    'position_x': int(x_entry.get()),
                    'position_y': int(y_entry.get()),
                    'width': int(width_entry.get()),
                    'height': int(height_entry.get())
                }
                
                # 保存设置到QSettings
                settings = QSettings("VideoWallpaper", "PluginSettings")
                settings.beginGroup(f"plugins/{self.name}")
                for key, value in new_settings.items():
                    settings.setValue(key, value)
                settings.endGroup()
                
                self.settings.update(new_settings)

                # 更新现有控件
                if self.widget:
                    self.widget.move(self.settings['position_x'], self.settings['position_y'])
                    self.widget.resize(self.settings['width'], self.settings['height'])
                    self.widget.update()  # 强制重绘

                messagebox.showinfo("保存成功", "设置已保存并应用")
                root.destroy()
            except ValueError as e:
                messagebox.showerror("错误", "请输入有效的数值")
            except Exception as e:
                messagebox.showerror("错误", f"保存设置时出错: {e}")

        # 按钮区域
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        save_button = tk.Button(button_frame, text="保存设置", command=save_settings, 
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        save_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="取消", command=root.destroy,
                                 bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        cancel_button.pack(side=tk.LEFT, padx=5)

        root.mainloop()

    def operate_on_window(self, window):
        """在壁纸上方创建记事本控件"""
        try:
            # 创建记事本控件
            self.widget = QWidget(window)
            self.widget.setGeometry(
                self.settings['position_x'],
                self.settings['position_y'],
                self.settings['width'],
                self.settings['height']
            )

            # 创建布局
            layout = QVBoxLayout(self.widget)
            layout.setContentsMargins(5, 5, 5, 5)

            # 标题栏
            title_layout = QHBoxLayout()
            title_label = QLabel("📝 记事本")
            title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: {self.settings['font_size'] + 2}px;
                    font-weight: bold;
                    color: {self.settings['text_color']};
                    padding: 5px;
                }}
            """)
            title_layout.addWidget(title_label)

            # 设置按钮
            settings_btn = QPushButton("设置")
            settings_btn.setMaximumWidth(60)
            settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            settings_btn.clicked.connect(self.show_settings_dialog)
            title_layout.addWidget(settings_btn)

            layout.addLayout(title_layout)

            # 文本显示区域
            self.text_display = QTextEdit()
            self.text_display.setPlainText(self.settings['note_content'])
            self.text_display.setReadOnly(True)  # 只读模式
            self.text_display.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {self.settings['background_color']};
                    color: {self.settings['text_color']};
                    font-size: {self.settings['font_size']}px;
                    font-family: Arial, sans-serif;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 8px;
                    line-height: 1.4;
                }}
            """)
            layout.addWidget(self.text_display)

            # 设置控件样式
            self.widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.settings['background_color']};
                    border: 2px solid #888;
                    border-radius: 8px;
                }}
            """)

            # 重写paintEvent来绘制阴影效果
            def paintEvent(event):
                painter = QPainter(self.widget)
                painter.setRenderHint(QPainter.Antialiasing)

                # 绘制阴影
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
                painter.drawRoundedRect(3, 3, self.widget.width()-3, self.widget.height()-3, 8, 8)

                painter.end()

            self.widget.paintEvent = paintEvent

            # 显示控件
            self.widget.show()
            print(f"[{self.name}] 记事本已显示在桌面")
        except Exception as e:
            print(f"[{self.name}] 创建记事本时出错: {e}")
            traceback.print_exc()

    def show_interaction(self):
        tk.messagebox.showinfo("记事本", "这是一个桌面记事本插件！\n\n点击""按钮来编辑内容。")

    def close_widget(self):
        """关闭控件的方法"""
        if self.widget:
            self.widget.close()
            self.widget = None
            print(f"[{self.name}] 记事本已关闭")


def create_plugin():
    return NotePadPlugin()
