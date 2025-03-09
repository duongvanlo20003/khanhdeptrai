import pygame
import random
import numpy as np
from ai_plot import plot_scores, load_scores
import pickle
import os

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gun Mayhem Clone")

# Font
font = pygame.font.SysFont('Arial', 24)

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Lớp nhân vật
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls=None, is_ai=False):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.5
        self.on_ground = False
        self.speed = 5
        self.direction = 1
        self.controls = controls
        self.is_ai = is_ai
        self.shoot_cooldown = 0
        self.hit_opponent = False
        self.got_hit = False

    def update_physics(self, platforms):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
        self.rect.x += self.vel_x
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def move(self, direction):
        self.vel_x = direction * self.speed
        if direction != 0:
            self.direction = direction

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            bullet = Bullet(self.rect.right if self.direction > 0 else self.rect.left, self.rect.centery, self.direction, self)
            bullets.add(bullet)
            self.shoot_cooldown = 20

# Lớp đạn
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10 * direction
        self.owner = owner
    
    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        for player in players:
            if player != self.owner and self.rect.colliderect(player.rect):
                knockback_direction = 1 if self.speed > 0 else -1
                player.rect.x += knockback_direction * 50
                player.vel_x = knockback_direction * 10
                player.vel_y = -10
                self.owner.hit_opponent = True
                player.got_hit = True
                self.kill()

class StepDisplay:
    def __init__(self, max_step, font, screen_width, screen_height):
        self.max_step = max_step  
        self.font = font          
        self.step = 0            

        self.bar_width = int(screen_width/3)                       
        self.bar_height = int(screen_height/20)                         
        self.bar_x = int((screen_width - self.bar_width) / 2)  
        self.bar_y = 10                              

        # Vị trí văn bản (dưới thanh loading 5 pixel)
        self.text_y = self.bar_y + self.bar_height + 5

    def update(self, current_step):
        self.step = current_step

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), (self.bar_x, self.bar_y, self.bar_width, self.bar_height))

        fill_width = (self.step / self.max_step) * self.bar_width  
        pygame.draw.rect(screen, (0, 255, 0), (self.bar_x, self.bar_y, fill_width, self.bar_height))

        step_text = self.font.render(f"Step: {self.step}/{self.max_step}", True, (255, 255, 255))
        text_width, _ = step_text.get_size()
        text_x = (screen.get_width() - text_width) / 2  
        screen.blit(step_text, (text_x, self.text_y))



# Function to save the Q-table
def save_q_table(ai, filename):
    with open(filename, 'wb') as f:
        pickle.dump(ai.q_table, f)
        print(f"Q-table file | Save Successed to {filename}")

    

# Q-learning AI
class QLearningAI:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = {}
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

    def get_q_values(self, state):
        return self.q_table.setdefault(state, np.zeros(len(self.actions)))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        q_values = self.get_q_values(state)
        return self.actions[np.argmax(q_values)]

    def update_q_value(self, state, action, reward, next_state):
        q_values = self.get_q_values(state)
        action_index = self.actions.index(action)
        if next_state is None:
            target = reward
        else:
            next_q_values = self.get_q_values(next_state)
            target = reward + self.discount_factor * np.max(next_q_values)
        q_values[action_index] += self.learning_rate * (target - q_values[action_index])

    def load_q_table(self, filename):
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    self.q_table = pickle.load(f)
                print(f"Q-table file | Successfully loaded Q-table from {filename}")
            else:
                self.q_table = {}
                print(f"Q-table file | {filename} does not exist. Starting with an empty Q-table.")

        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Error loading Q-table from {filename}: {e}. Starting with an empty Q-table.")


# AI Bot
class AIBot(Player):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, is_ai=True)
        self.ai = QLearningAI(actions=["idle", "left", "right", "jump", "shoot", "left_shoot", "right_shoot", "jump_shoot"])

    def get_state(self, target):
        rel_x = target.rect.x - self.rect.x
        rel_x_bin = 0 if rel_x < -100 else 1 if rel_x < -50 else 2 if rel_x <= 50 else 3 if rel_x <= 100 else 4
        rel_y = target.rect.y - self.rect.y
        rel_y_bin = 0 if rel_y < -50 else 1 if rel_y <= 50 else 2
        agent_on_ground = 1 if self.on_ground else 0
        opponent_on_ground = 1 if target.on_ground else 0
        agent_direction = 1 if self.direction > 0 else 0
        opponent_direction = 1 if target.direction > 0 else 0
        return (rel_x_bin, rel_y_bin, agent_on_ground, opponent_on_ground, agent_direction, opponent_direction)

    def perform_action(self, action, bullets):
        if action == "idle":
            self.move(0)
        elif action == "left":
            self.move(-1)
        elif action == "right":
            self.move(1)
        elif action == "jump":
            self.jump()
        elif action == "shoot":
            self.shoot(bullets)
        elif action == "left_shoot":
            self.move(-1)
            self.shoot(bullets)
        elif action == "right_shoot":
            self.move(1)
            self.shoot(bullets)
        elif action == "jump_shoot":
            self.jump()
            self.shoot(bullets)

# Lớp nền tảng
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Khởi tạo nhóm
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Nền tảng
platforms = pygame.sprite.Group()
# platforms.add(Platform(150, 500, 500, 20))
platforms.add(Platform(50, 400, 250, 20))
platforms.add(Platform(500, 400, 250, 20))
# platforms.add(Platform(300, 300, 200, 20))
platforms.add(Platform(50, 550, 700, 20))
# platforms.add(Platform(650, 300, 150, 20))
platforms.add(Platform(250, 250, 150, 20))
platforms.add(Platform(450, 250, 150, 20))


# Reset game
def reset_game():
    global players, bullets
    players.empty()
    bullets.empty()
    player1 = AIBot(300, 100, WHITE)
    player2 = AIBot(500, 100, GREEN)
    player1.ai.load_q_table("q_table_player1.pkl")
    player2.ai.load_q_table("q_table_player2.pkl")
    players.add(player1, player2)
    return player1, player2


scores_agent1 = load_scores(filename="history1.txt")
scores_agent2 = load_scores(filename="history2.txt")

max_step = 500

step_display = StepDisplay(max_step, font, WIDTH, HEIGHT)

# Chạy trò chơi
running = True
while running:
    # Calculate rewards
    total_reward1 = 0
    total_reward2 = 0

    step = 0
    player1, player2 = reset_game()
    episode_ended = False

    while not episode_ended:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                episode_ended = True

        # Get states
        state1 = player1.get_state(player2)
        state2 = player2.get_state(player1)

        # Choose actions
        action1 = player1.ai.choose_action(state1)
        action2 = player2.ai.choose_action(state2)

        # Perform actions
        player1.perform_action(action1, bullets)
        player2.perform_action(action2, bullets)

        # Update physics
        for player in players:
            player.update_physics(platforms)

        # Update bullets
        bullets.update()

        # Calculate rewards
        reward1 = 0
        reward2 = 0
        
        if player1.hit_opponent:
            reward1 += 100
        if player1.got_hit:
            reward1 -= 10
        if player2.hit_opponent:
            reward2 += 100
        if player2.got_hit:
            reward2 -= 10

        # Reset hit flags
        player1.hit_opponent = False
        player1.got_hit = False
        player2.hit_opponent = False
        player2.got_hit = False

        # Check terminal conditions
        if player1.rect.top > HEIGHT or player1.rect.right < 0 or player1.rect.left > WIDTH:
            episode_ended = True
            reward1 -= 100
            reward2 += 100
        elif player2.rect.top > HEIGHT or player2.rect.right < 0 or player2.rect.left > WIDTH:
            episode_ended = True
            reward1 += 100
            reward2 -= 100
        elif step >= max_step:
            episode_ended = True
            reward1 -= 50  # Small penalty for timeout
            reward2 -= 50  # Small penalty for timeout

        reward1 -= 0.01
        reward2 -= 0.01

        # Update reward his for plot
        total_reward1 += reward1
        total_reward2 += reward2

        # Get next states
        next_state1 = player1.get_state(player2) if not episode_ended else None
        next_state2 = player2.get_state(player1) if not episode_ended else None

        # Update Q-values
        player1.ai.update_q_value(state1, action1, reward1, next_state1)
        player2.ai.update_q_value(state2, action2, reward2, next_state2)

        # Increase step
        step +=1

        # Render
        step_display.update(step)
        screen.fill(BLACK)

        step_display.draw(screen)  
        players.draw(screen)
        bullets.draw(screen)
        platforms.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # Plot score
    # Update reward history for plot
    scores_agent1.append(total_reward1)
    scores_agent2.append(total_reward2)
    plot_scores(scores_agent1, scores_agent2)
    save_q_table(player1.ai, 'q_table_player1.pkl')
    save_q_table(player2.ai, 'q_table_player2.pkl')
    print(f"Current Game: {len(scores_agent1)} \n")

pygame.quit()