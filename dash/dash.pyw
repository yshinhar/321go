import turtle
import random
import math
import time
import keyboard
import winsound
import os

class GameObject:
    def __init__(self, x, y, size, color, screen):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.screen = screen  
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        
    def draw(self):
        self.t.clear()
        self.t.fillcolor(self.color)
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
    
    def cleanup(self):
        self.t.clear()
        self.t.hideturtle()


class AimArrow:
    def __init__(self):
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        self.t.penup()
        self.t.color("cyan3")
        self.angle = 0
        self.oscillating_up = True
        self.max_angle = 90
        self.angle_step = 3
        
        self.arc_t = turtle.Turtle()
        self.arc_t.hideturtle()
        self.arc_t.speed(0)
        self.arc_t.penup()
        self.arc_t.color("cyan3")

    def reset_angle(self):
        self.angle = 0
        self.oscillating_up = True

    def update(self):
        if self.oscillating_up:
            self.angle += self.angle_step
            if self.angle >= self.max_angle:
                self.oscillating_up = False
        else:
            self.angle -= self.angle_step
            if self.angle <= -self.max_angle:
                self.oscillating_up = True

    def draw(self, x, y, base_angle):
     
        self.t.clear()
        self.arc_t.clear()
        
     
        self.arc_t.penup()
        self.arc_t.goto(x, y)
        self.arc_t.setheading(base_angle - self.max_angle)  
        self.arc_t.pendown()
        self.arc_t.pensize(2)
        
    
        radius = 40
        self.arc_t.penup()
        self.arc_t.forward(40)
        self.arc_t.left(90)
        self.arc_t.pendown()
        self.arc_t.circle(radius, 180)  
        
        
        self.t.penup()
        self.t.goto(x, y)
        final_angle = base_angle + self.angle
        self.t.setheading(final_angle)
        self.t.pendown()
        self.t.pensize(3)
        self.t.forward(50)
        self.t.right(150)
        self.t.forward(15)
        self.t.backward(15)
        self.t.left(300)
        self.t.forward(15)
        self.t.penup()

    def cleanup(self):
        self.t.clear()
        self.arc_t.clear()
        
class Player(GameObject):
    def __init__(self, x, y, screen):
        super().__init__(x, y, 50, "blue", screen)
        self.direction = None
        self.is_dashing = False
        self.is_aiming = False
        self.dash_speed = 30
        self.score = 0
        self.aim_arrow = AimArrow()
        self.last_movement_angle = 0
        self.aim_start_position = None
        self.steps_taken = 0
        self.base_step_limit = 20
        
    def get_current_step_limit(self):
        return self.base_step_limit

    def move(self, dx, dy, grid_size):
        if not self.is_dashing and not self.is_aiming:
            if self.steps_taken >= self.get_current_step_limit():
                return
            
            new_x = self.x + dx * 10
            new_y = self.y + dy * 10
            
            half_grid = grid_size / 2
            
            buffer = 0.5
            if abs(new_x) < half_grid - self.size/2 - buffer and abs(new_y) < half_grid - self.size/2 - buffer:
                self.x = new_x
                self.y = new_y
                self.update_direction(dx, dy)
                if self.aim_start_position:
                    self.check_position_for_arrow()
                self.steps_taken += 1

    def execute_dash(self):
        winsound.Beep(500, 50)
        if self.is_aiming:
            self.aim_arrow.cleanup()  
            self.is_aiming = False
            self.is_dashing = True
            angle_rad = math.radians(self.last_movement_angle + self.aim_arrow.angle)
            self.direction = (math.cos(angle_rad), math.sin(angle_rad))
            self.aim_start_position = None
            self.steps_taken = 0  
                
    def update_direction(self, dx, dy):
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            self.last_movement_angle = math.degrees(math.atan2(dy, dx))
            
    def aim_control(self, dx, dy):
        if self.is_aiming and (dx != 0 or dy != 0):
            if dx > 0:  # D key
                self.last_movement_angle = 0
            elif dx < 0:  # A key
                self.last_movement_angle = 180
            elif dy > 0:  # W key
                self.last_movement_angle = 90
            elif dy < 0:  # S key
                self.last_movement_angle = 270
            
    def update_direction(self, dx, dy):
        if dx != 0 or dy != 0:
            self.direction = (dx, dy)
            if not self.is_aiming:
                if dx > 0:  # D key
                    self.last_movement_angle = 0
                elif dx < 0:  # A key
                    self.last_movement_angle = 180
                elif dy > 0:  # W key
                    self.last_movement_angle = 90
                elif dy < 0:  # S key
                    self.last_movement_angle = 270
    def start_aiming(self):
        if not self.is_dashing and not self.is_aiming and self.direction:
            self.is_aiming = True
            self.aim_start_position = (self.x, self.y)

    def update_dash(self, grid_size):
        if self.is_dashing:
            dx, dy = self.direction
            new_x = self.x + dx * self.dash_speed
            new_y = self.y + dy * self.dash_speed
            
            half_grid = grid_size / 2
            if abs(new_x) >= half_grid - self.size/2 or abs(new_y) >= half_grid - self.size/2:
                self.is_dashing = False
                self.x = max(min(new_x, half_grid - self.size/2 - 1), -half_grid + self.size/2 + 1)
                self.y = max(min(new_y, half_grid - self.size/2 - 1), -half_grid + self.size/2 + 1)
                return True
            else:
                self.x = new_x
                self.y = new_y
        return False

    
    def draw(self):
        self.t.clear()
        self.t.fillcolor("blue")
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
        
        if self.is_aiming:
            self.aim_arrow.draw(self.x, self.y, self.last_movement_angle)
            
class Collectible(GameObject):
    def __init__(self, grid_size, screen):
        half_grid = grid_size / 2 - 25
        x = random.uniform(-half_grid, half_grid)
        y = random.uniform(-half_grid, half_grid)
        super().__init__(x, y, 50, "yellow", screen)
        
    def draw(self):
        self.t.clear()
        self.t.fillcolor("yellow")
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
class ComboMeter:
    def __init__(self, x, y):
        self.value = 0
        self.max_value = 100
        self.decay_rate = 0.5 
        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.penup()
        self.t.goto(x, y)
        self.multiplier = 1
        self.last_update = time.time()
    
    def update(self, is_aiming=False):
        current_time = time.time()
        time_diff = current_time - self.last_update
        
        current_decay = self.decay_rate * (0.3 if is_aiming else 1.0)
        self.value = max(0, self.value - current_decay * time_diff * 60)
        
        if self.value <= 0:
            self.multiplier = 1
            
        self.last_update = current_time

    def add_value(self, amount):
        self.value = min(self.max_value, self.value + amount)
    
    def get_bonus_points(self):
        return (self.multiplier - 1) * 25
    
    def collect_coin(self):
        self.value = self.max_value
        self.multiplier += 1
    
    def draw(self):
        self.t.clear()
        self.t.goto(-self.max_value/2, 250)
        self.t.pendown()
        self.t.fillcolor("gray")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(self.max_value)
            self.t.left(90)
            self.t.forward(20)
            self.t.left(90)
        self.t.end_fill()
        
        self.t.fillcolor("cyan3")
        self.t.begin_fill()
        for _ in range(2):
            self.t.forward(self.value)
            self.t.left(90)
            self.t.forward(20)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
        
        self.t.goto(0, 280)
        self.t.write(f"Combo: x{self.multiplier}", align="center", font=("Arial", 16, "bold"))

class Enemy(GameObject):
    def __init__(self, x, y, screen, is_bouncing=False, enemy_type=''):
        super().__init__(x, y, 50, "red", screen)
        self.speed = 2.5
        self.is_bouncing = is_bouncing
        self.enemy_type = enemy_type
        if is_bouncing:
            self.angle = random.uniform(0, 360)
            self.speed = 4

    def draw(self):
        self.t.clear()
        self.t.fillcolor(self.color)
        self.t.goto(self.x - self.size/2, self.y - self.size/2)
        self.t.pendown()
        self.t.begin_fill()
        for _ in range(4):
            self.t.forward(self.size)
            self.t.left(90)
        self.t.end_fill()
        self.t.penup()
    def chase(self, player, grid_size, time_slowed):
        speed_multiplier = 0.3 if time_slowed else 1.0
        
        if self.is_bouncing:
            self.bounce(grid_size, speed_multiplier)
        else:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                new_x = self.x + (dx/dist) * self.speed * speed_multiplier
                new_y = self.y + (dy/dist) * self.speed * speed_multiplier
                
                half_grid = grid_size / 2
                self.x = max(min(new_x, half_grid - self.size/2), -half_grid + self.size/2)
                self.y = max(min(new_y, half_grid - self.size/2), -half_grid + self.size/2)
    
    def bounce(self, grid_size, speed_multiplier=1.0):
        angle_rad = math.radians(self.angle)
        dx = math.cos(angle_rad) * self.speed * speed_multiplier
        dy = math.sin(angle_rad) * self.speed * speed_multiplier
        
        half_grid = grid_size / 2
        new_x = self.x + dx
        new_y = self.y + dy
        
        bounced = False
        
    
        if abs(new_x) >= half_grid - self.size/2:
            self.angle = 180 - self.angle
            if self.angle < 0:
                self.angle += 360
            bounced = True
            new_x = max(min(new_x, half_grid - self.size/2), -half_grid + self.size/2)
        
        if abs(new_y) >= half_grid - self.size/2:
            self.angle = 360 - self.angle
            if self.angle >= 360:
                self.angle -= 360
            bounced = True
            new_y = max(min(new_y, half_grid - self.size/2), -half_grid + self.size/2)
        
        if bounced:
            self.angle += random.uniform(-10, 10)
            if self.angle < 0:
                self.angle += 360
            elif self.angle >= 360:
                self.angle -= 360
        
        self.x = new_x
        self.y = new_y

class Game:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.getcanvas().winfo_toplevel().attributes("-fullscreen", True)
        self.screen.bgcolor("black")
        
        self.screen.tracer(0, 0)
        turtle.tracer(0, 0)
        
        self.window = self.screen.getcanvas().winfo_toplevel()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        
        turtle.speed(0)
        
        
        self.grid_size = min(self.screen_width, self.screen_height) - 100
        
        self.game_state = "start"
        self.running = True  
        
        
        self.initialize_game()

    def initialize_game(self):
        self.is_running = True
        self.player = Player(0, 0, self.screen)  
        self.player.t.speed(0)
        self.player.t._tracer(0)
        
        
        self.enemies = [
            Enemy(-200, -200, self.screen, is_bouncing=True, enemy_type='rokia'),
            Enemy(200, 200, self.screen, is_bouncing=True, enemy_type='ranji'),
            Enemy(0, 200, self.screen, is_bouncing=False, enemy_type='ichigo')
        ]
        for enemy in self.enemies:
            enemy.t.speed(0)

        self.collectible = None
        
        
        self.score_label = turtle.Turtle()
        self.score_label.speed(0)
        self.score_label.hideturtle()
        self.score_label.penup()
        self.score_label.goto(self.grid_size/2 + 30, 20)
        
        self.score_number = turtle.Turtle()
        self.score_number.speed(0)
        self.score_number.hideturtle()
        self.score_number.penup()
        self.score_number.goto(self.grid_size/2 + 30, -20)
        self.score_number.color("red")
        
        
        self.combo_meter = ComboMeter(0, 0)
        self.combo_meter.t.speed(0)
        
        
        self.clear_square = turtle.Turtle()
        self.clear_square.speed(0)
        self.clear_square.hideturtle()
        self.clear_square.penup()
        
        
        self.step_display = turtle.Turtle()
        self.step_display.speed(0)
        self.step_display.hideturtle()
        self.step_display.penup()

    def draw_start_screen(self):
        self.screen.clear()
        self.screen.bgcolor("black")
        
        start_text = turtle.Turtle()
        start_text.speed(0)
        start_text.hideturtle()
        start_text.penup()
        start_text.color("white")
        
        
        start_text.goto(-100, 0)
        start_text.write("press           ", align="center", font=("Arial", 36, "normal"))
        start_text.color("cyan3")
        start_text.write("SPACE            ", font=("Arial", 36, "bold"))
        start_text.color("white")
        start_text.write("              to start", font=("Arial", 36, "normal"))
        
        
        start_text.goto(-50, -50)
        start_text.write("press    ", align="center", font=("Arial", 18, "normal"))
        start_text.color("cyan3")
        start_text.write("   ESC                 ", font=("Arial", 18, "normal"))
        start_text.color("white")
        start_text.write("           to exit", font=("Arial", 18, "normal"))
        
        self.screen.update()

    def draw_game_over_screen(self):
        self.screen.clear()
        self.screen.bgcolor("black")
        
        game_over = turtle.Turtle()
        game_over.speed(0)
        game_over.hideturtle()
        game_over.color("white")
        game_over.penup()
        
        game_over.goto(0, 50)
        game_over.write("Game Over!", align="center", font=("Arial", 36, "bold"))
        
        game_over.goto(0, -20)
        game_over.write(f"Score: {self.player.score}", align="center", font=("Arial", 24, "normal"))
        
        game_over.goto(0, -150)
        game_over.write("PRESS SPACE TO PLAY AGAIN", align="center", font=("Arial", 18, "normal"))
        
        game_over.goto(0, -200)
        game_over.write("press ESC to exit", align="center", font=("Arial", 18, "normal"))
        
        self.screen.update()

    def exit_fullscreen(self):
        self.running = False  
        self.window.destroy()  
        import sys
        sys.exit()

    def draw_grid(self):
        grid = turtle.Turtle()
        grid.speed(0)
        grid.hideturtle()
        
        
        grid.penup()
        grid.goto(-self.grid_size/2 - 10, -self.grid_size/2 - 10)
        grid.pendown()
        grid.fillcolor("black")
        grid.begin_fill()
        for _ in range(4):
            grid.forward(self.grid_size + 20)
            grid.left(90)
        grid.end_fill()
        
        
        grid.penup()
        grid.goto(-self.grid_size/2, -self.grid_size/2)
        grid.pendown()
        grid.fillcolor("white")
        grid.begin_fill()
        for _ in range(4):
            grid.forward(self.grid_size)
            grid.left(90)
        grid.end_fill()
        
        self.screen.update()

    def update_score_display(self):
        self.score_label.clear()
        self.score_number.clear()
        self.score_label.color("white")
        self.score_label.write("Score:", align="left", font=("Arial", 20, "bold"))
        self.score_number.color("cyan3")
        self.score_number.write(f"{self.player.score}", align="left", font=("Arial", 20, "bold"))

    def check_collisions(self):
        for enemy in self.enemies:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < (self.player.size + enemy.size)/2:
                self.is_running = False
        
        if self.collectible:
            dx = self.player.x - self.collectible.x
            dy = self.player.y - self.collectible.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < (self.player.size + self.collectible.size)/2:
                bonus_points = self.combo_meter.get_bonus_points()
                self.player.score += 100 + bonus_points
                self.combo_meter.collect_coin()
                winsound.Beep(1000, 100)
                self.remove_collectible()

    def check_movement(self):
        dx = dy = 0
        if keyboard.is_pressed('w'): dy = 1
        if keyboard.is_pressed('s'): dy = -1
        if keyboard.is_pressed('a'): dx = -1
        if keyboard.is_pressed('d'): dx = 1
        
        if dx != 0 or dy != 0:
            if self.player.is_aiming:
                self.player.aim_control(dx, dy)
            else:
                self.player.move(dx, dy, self.grid_size)  
                self.combo_meter.value = max(0, self.combo_meter.value - 0.5)
        
        if keyboard.is_pressed('space'):
            if self.game_state == "start" or self.game_state == "game_over":
                self.start_new_game()
            elif not self.player.is_aiming:
                self.player.start_aiming()
        elif keyboard.is_pressed('escape'):
                self.exit_fullscreen()
        elif self.player.is_aiming:
            self.player.execute_dash()
            self.combo_meter.add_value(20)
        
    def start_new_game(self):
        self.game_state = "playing"
        self.screen.clear()
        self.screen.bgcolor("black")
        self.draw_grid()  
        self.initialize_game()  

    def spawn_collectible(self):
        if self.collectible is None:
            self.collectible = Collectible(self.grid_size, self.screen)
            self.collectible.t.speed(0)
            
    def clear_collectible_visual(self, x, y, size):
        self.clear_square.clear()
        self.clear_square.fillcolor("white")
        
        extra_space = 5  
        self.clear_square.goto(x - size/2 - extra_space, y - size/2 - extra_space)
        self.clear_square.begin_fill()
        for _ in range(4):
            self.clear_square.forward(size + 2 * extra_space)
            self.clear_square.left(90)
        self.clear_square.end_fill()

    def remove_collectible(self):
        if self.collectible:
            self.clear_collectible_visual(self.collectible.x, self.collectible.y, self.collectible.size)
            self.collectible.cleanup()
            self.collectible = None
                
    def run(self):
        self.draw_start_screen()
        
        while self.running:  
            if self.game_state == "start":
                self.check_movement()
            
    def run(self):
        self.draw_start_screen()
        
        while self.running:
            if self.game_state == "start":
                self.check_movement()
            
            elif self.game_state == "playing":
                self.step_display.clear()
                current_step_limit = self.player.get_current_step_limit()
                steps_remaining = current_step_limit - self.player.steps_taken
                self.step_display.goto(-self.grid_size/2 + 30, self.grid_size/2 - 40)
                self.step_display.color("black")
                self.step_display.write("          Steps:        ", align="center", font=("Arial", 16, "normal"))
                self.step_display.color("cyan3")
                self.step_display.write(f"       {steps_remaining}          ", font=("Arial", 16, "normal"))
                self.step_display.color("black")
                self.step_display.write(f"           /{current_step_limit}", font=("Arial", 16, "normal"))
                
                self.check_movement()
                
                if self.player.is_aiming:
                    self.player.aim_arrow.update()
                
                if self.player.update_dash(self.grid_size):
                    self.spawn_collectible()
                
                for enemy in self.enemies:
                    enemy.chase(self.player, self.grid_size, self.player.is_aiming)
                
                self.combo_meter.update(self.player.is_aiming)
                
                
                self.player.t.clear()
                for enemy in self.enemies:
                    enemy.t.clear()
                if self.collectible:
                    self.collectible.t.clear()
                if hasattr(self.player, 'aim_arrow'):
                    self.player.aim_arrow.t.clear()
                self.combo_meter.t.clear()
                
                
                self.player.draw()
                for enemy in self.enemies:
                    enemy.draw()
                if self.collectible:
                    self.collectible.draw()
                self.combo_meter.draw()
                
                self.check_collisions()
                self.update_score_display()
                
                
                self.screen.update()
                
                if not self.is_running:
                    self.game_state = "game_over"
                    self.draw_game_over_screen()
            
            elif self.game_state == "game_over":
                self.check_movement()
            
            time.sleep(0.016)
            
if __name__ == "__main__":
    game = Game()
    game.run()
