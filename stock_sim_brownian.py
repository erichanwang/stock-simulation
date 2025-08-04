import pygame
import random
import os
import json
import math
from datetime import datetime
from collections import deque

# Initialize Pygame
pygame.init()

# --- Setup ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stock Trading Simulator v3.4 - Brownian Motion")

# --- Colors and Fonts ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 177, 106)
RED = (217, 30, 24)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (50, 50, 50)
BLUE = (30, 144, 255)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 72)

# --- File Paths and Data ---
DATA_DIR = "data"
SAVE_FILE = os.path.join(DATA_DIR, "save_game_brownian.json")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Game State Variables ---
player_cash = 10000.00
player_shares = 0
stock_price = 50.00
stock_history = deque(maxlen=5000)
mu = 0.0005
sigma = 0.02
graph_y_offset = 0
graph_zoom = 1.0

# --- UI Element Classes ---
class Button:
    def __init__(self, x, y, width, height, text, color, radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.radius = radius

    def draw(self, surface, font_size=small_font):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=self.radius)
        text_surface = font_size.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class InputBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN: return self.text
            elif event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            elif event.unicode.isdigit(): self.text += event.unicode
        return None

    def draw(self, surface):
        color = LIGHT_GRAY if self.active else GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surface = small_font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)

# --- Game Functions ---
def save_game():
    data = {
        "player_cash": player_cash,
        "player_shares": player_shares,
        "stock_price": stock_price,
        "stock_history": list(stock_history)
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_game():
    global player_cash, player_shares, stock_price, stock_history
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            player_cash = data["player_cash"]
            player_shares = data["player_shares"]
            stock_price = data["stock_price"]
            stock_history = deque(data["stock_history"], maxlen=5000)
        return True
    return False

def log_data():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(DATA_DIR, f"stock_log_brownian_{timestamp}.txt")
    with open(log_file, 'w') as f:
        for price in stock_history:
            f.write(f"{price}\n")

def update_stock_price_func():
    global stock_price
    dt = 1
    random_value = random.gauss(0, 1)
    change = stock_price * (mu * dt + sigma * random_value * math.sqrt(dt))
    stock_price += change
    if stock_price < 1: stock_price = 1
    stock_history.append(stock_price)

def buy_shares_func(amount):
    global player_cash, player_shares
    if not isinstance(amount, int) or amount <= 0: return
    cost = stock_price * amount
    if player_cash >= cost:
        player_cash -= cost
        player_shares += amount

def sell_shares_func(amount):
    global player_cash, player_shares
    if not isinstance(amount, int) or amount <= 0: return
    if player_shares >= amount:
        player_cash += stock_price * amount
        player_shares -= amount

def draw_text_func(text, x, y, color=BLACK, f=font):
    text_surface = f.render(text, True, color)
    screen.blit(text_surface, (x, y))

# --- Main Game Screens ---
def start_menu():
    new_game_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 80, "New Game", GREEN)
    load_game_button = Button(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 50, 200, 80, "Load Game", BLUE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None # Quit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.is_clicked(event.pos):
                    stock_history.clear()
                    stock_history.append(stock_price)
                    return "new"
                if load_game_button.is_clicked(event.pos):
                    if load_game():
                        return "load"
                    else:
                        print("No save file found, starting new game.")
                        stock_history.clear()
                        stock_history.append(stock_price)
                        return "new"

        screen.fill(DARK_GRAY)
        draw_text_func("Stock Simulator - Brownian", SCREEN_WIDTH/2 - 320, SCREEN_HEIGHT/4, WHITE, title_font)
        new_game_button.draw(screen, font)
        load_game_button.draw(screen, font)
        pygame.display.flip()
        clock.tick(15)

def main_game():
    global graph_y_offset, graph_zoom
    
    # --- UI Layout ---
    buy_label = font.render("Buy", True, GREEN)
    buy_buttons = [Button(80, SCREEN_HEIGHT - 110, 60, 40, "1", GREEN), Button(150, SCREEN_HEIGHT - 110, 60, 40, "10", GREEN), Button(220, SCREEN_HEIGHT - 110, 60, 40, "50", GREEN), Button(290, SCREEN_HEIGHT - 110, 70, 40, "100", GREEN)]
    custom_buy_input = InputBox(370, SCREEN_HEIGHT - 110, 100, 40)
    custom_buy_button = Button(480, SCREEN_HEIGHT - 110, 100, 40, "Custom", GREEN)
    buy_max_button = Button(590, SCREEN_HEIGHT - 110, 100, 40, "Max", GREEN)

    sell_label = font.render("Sell", True, RED)
    sell_buttons = [Button(80, SCREEN_HEIGHT - 60, 60, 40, "1", RED), Button(150, SCREEN_HEIGHT - 60, 60, 40, "10", RED), Button(220, SCREEN_HEIGHT - 60, 60, 40, "50", RED), Button(290, SCREEN_HEIGHT - 60, 70, 40, "100", RED)]
    custom_sell_input = InputBox(370, SCREEN_HEIGHT - 60, 100, 40)
    custom_sell_button = Button(480, SCREEN_HEIGHT - 60, 100, 40, "Custom", RED)
    sell_max_button = Button(590, SCREEN_HEIGHT - 60, 100, 40, "Max", RED)

    running = True
    price_update_timer = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_q: buy_shares_func(10)
                if event.key == pygame.K_w: buy_shares_func(50)
                if event.key == pygame.K_e: buy_shares_func(100)
                if event.key == pygame.K_a: sell_shares_func(10)
                if event.key == pygame.K_s: sell_shares_func(50)
                if event.key == pygame.K_d: sell_shares_func(100)
                if event.key == pygame.K_UP: graph_zoom *= 1.1
                if event.key == pygame.K_DOWN: graph_zoom /= 1.1
            if event.type == pygame.MOUSEWHEEL:
                graph_y_offset += event.y * 20

            custom_buy_input.handle_event(event)
            custom_sell_input.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i,b in enumerate(buy_buttons): 
                    if b.is_clicked(event.pos): buy_shares_func([1,10,50,100][i])
                if custom_buy_button.is_clicked(event.pos):
                    try: buy_shares_func(int(custom_buy_input.text)); custom_buy_input.text = ""
                    except: custom_buy_input.text = ""
                if buy_max_button.is_clicked(event.pos):
                    if stock_price > 0: buy_shares_func(int(player_cash // stock_price))
                for i,b in enumerate(sell_buttons):
                    if b.is_clicked(event.pos): sell_shares_func([1,10,50,100][i])
                if custom_sell_button.is_clicked(event.pos):
                    try: sell_shares_func(int(custom_sell_input.text)); custom_sell_input.text = ""
                    except: custom_sell_input.text = ""
                if sell_max_button.is_clicked(event.pos): sell_shares_func(player_shares)

        price_update_timer += clock.get_time()
        if price_update_timer >= 250:
            update_stock_price_func()
            price_update_timer = 0

        screen.fill(DARK_GRAY)
        
        # --- Draw Graph ---
        graph_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(screen, BLACK, graph_rect)
        if len(stock_history) > 1:
            max_len = graph_rect.width
            visible_history = list(stock_history)[-max_len:]
            
            max_price = max(visible_history)
            min_price = min(visible_history)
            price_range = (max_price - min_price) / graph_zoom if graph_zoom != 0 else 1
            if price_range == 0: price_range = 1
            center_price = (max_price + min_price) / 2
            
            points = []
            for i, price in enumerate(visible_history):
                x = graph_rect.x + i
                normalized_pos = (price - center_price) / price_range
                y = graph_rect.centery - normalized_pos * graph_rect.height - graph_y_offset
                y = max(graph_rect.top, min(graph_rect.bottom, y))
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, BLUE, False, points, 2)
        pygame.draw.rect(screen, WHITE, graph_rect, 2, border_radius=5)

        # --- Draw UI ---
        draw_text_func(f"Cash: ${player_cash:,.2f}", 20, 20, WHITE)
        draw_text_func(f"Shares: {player_shares}", 20, 60, WHITE)
        draw_text_func(f"Portfolio: ${(player_shares * stock_price):,.2f}", 20, 100, WHITE)
        price_color = GREEN if stock_price >= (stock_history[-2] if len(stock_history) > 1 else stock_price) else RED
        draw_text_func(f"Stock Price: ${stock_price:,.2f}", SCREEN_WIDTH - 320, 20, price_color)
        
        screen.blit(buy_label, (20, SCREEN_HEIGHT - 115))
        for button in buy_buttons: button.draw(screen)
        custom_buy_input.draw(screen)
        custom_buy_button.draw(screen)
        buy_max_button.draw(screen)
        
        screen.blit(sell_label, (20, SCREEN_HEIGHT - 65))
        for button in sell_buttons: button.draw(screen)
        custom_sell_input.draw(screen)
        custom_sell_button.draw(screen)
        sell_max_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    # --- Post-game ---
    save_game()
    log_data()

if __name__ == '__main__':
    clock = pygame.time.Clock()
    game_mode = start_menu()
    if game_mode:
        main_game()
    pygame.quit()
