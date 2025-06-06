import tkinter as tk
import threading
import random
import time
import math
import gc

class Ball:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.radius = random.randint(5, 15)
        self.life = random.uniform(2, 15)  # 壽命（秒）
        self.speed = random.uniform(10, 30)  # 像素/秒
        self.angle = random.uniform(0, 2 * math.pi)  # 方向（弧度）
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

        self.canvas_width = int(self.canvas['width'])
        self.canvas_height = int(self.canvas['height'])

        # 建立球體圖形
        self.id = self.canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill='blue'
        )

        self.thread = threading.Thread(target=self.animate)
        self.thread.daemon = True
        self.running = True
        self.thread.start()

    def animate(self):
        start_time = time.time()
        interval = 0.01  # 更新間隔（秒）

        while self.running:
            time_elapsed = time.time() - start_time
            if time_elapsed > self.life:
                break

            # 計算位移
            dx_per_tick = self.dx * interval
            dy_per_tick = self.dy * interval

            def move():
                coords = self.canvas.coords(self.id)
                x1, y1, x2, y2 = coords
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                # 邊界檢查
                if cx - self.radius + dx_per_tick < 0 or cx + self.radius + dx_per_tick > self.canvas_width:
                    self.dx = -self.dx
                if cy - self.radius + dy_per_tick < 0 or cy + self.radius + dy_per_tick > self.canvas_height:
                    self.dy = -self.dy

                self.canvas.move(self.id, self.dx * interval, self.dy * interval)

            self.canvas.after(0, move)
            time.sleep(interval)

        self.canvas.after(0, lambda: self.canvas.delete(self.id))


class Screen:
    def __init__(self):
        # build tk screen
        self.root = tk.Tk()
        self.root.title("HW8-ball")
        self.root.resizable(False, False)
        self.root.geometry("300x200")

        self.canvas = tk.Canvas(self.root, width=300, height=200, bg="black")
        self.canvas.pack()

        self.balls = []

        # 滑鼠右鍵綁定
        self.canvas.bind("<Button-3>", self.spawn_ball)

    def spawn_ball(self, event):
        if len(self.balls) >= 10:
            return  # 最多 10 顆球
        ball = Ball(self.canvas, event.x, event.y)
        self.balls.append(ball)

        # 自動清除已死亡球
        def cleanup():
            gc.collect()
            self.balls = [b for b in self.balls if b.canvas.coords(b.id)]
        self.root.after(1000, cleanup)

    def run(self):
        self.root.mainloop()


main = Screen()
main.run()
