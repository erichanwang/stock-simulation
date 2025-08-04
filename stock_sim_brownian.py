import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stock Trading Simulator v3.2 - Brownian Motion")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)

# Font
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)

# Player stats
player_cash = 10000.00
player_shares = 0

# Stock properties
stock_price = 50.00
stock_history = [stock_price] * (SCREEN_WIDTH - 100)
mu = 0.0005  # Increased Drift
sigma = 0.02  # Increased Volatility

# --- UI Elements ---
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = small_font.render(self.text, True, BLACK)
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
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isdigit():
                    self.text += event.unicode
        return None

    def draw(self, surface):
        color = LIGHT_GRAY if self.active else GRAY
        pygame.draw.rect(surface, color, self.rect)
        text_surface = small_font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(surface, BLACK, self.rect, 2)

# Create UI elements
buy_buttons = [
    Button(10, SCREEN_HEIGHT - 110, 50, 40, "Buy 1", GREEN),
    Button(70, SCREEN_HEIGHT - 110, 60, 40, "Buy 10", GREEN),
    Button(140, SCREEN_HEIGHT - 110, 60, 40, "Buy 50", GREEN),
    Button(210, SCREEN_HEIGHT - 110, 70, 40, "Buy 100", GREEN),
]
custom_buy_input = InputBox(290, SCREEN_HEIGHT - 110, 100, 40)
custom_buy_button = Button(400, SCREEN_HEIGHT - 110, 100, 40, "Buy Custom", GREEN)
buy_max_button = Button(510, SCREEN_HEIGHT - 110, 100, 40, "Buy Max", GREEN)

sell_buttons = [
    Button(10, SCREEN_HEIGHT - 60, 50, 40, "Sell 1", RED),
    Button(70, SCREEN_HEIGHT - 60, 60, 40, "Sell 10", RED),
    Button(140, SCREEN_HEIGHT - 60, 60, 40, "Sell 50", RED),
    Button(210, SCREEN_HEIGHT - 60, 70, 40, "Sell 100", RED),
]
custom_sell_input = InputBox(290, SCREEN_HEIGHT - 60, 100, 40)
custom_sell_button = Button(400, SCREEN_HEIGHT - 60, 100, 40, "Sell Custom", RED)
sell_max_button = Button(510, SCREEN_HEIGHT - 60, 100, 40, "Sell Max", RED)


def draw_text(text, x, y, color=BLACK, f=font):
    """Draws text on the screen."""
    text_surface = f.render(text, True, color)
    screen.blit(text_surface, (x, y))

def update_stock_price():
    """Updates the stock price using Geometric Brownian Motion."""
    global stock_price
    dt = 1  # Time step
    random_value = random.gauss(0, 1)
    change = stock_price * (mu * dt + sigma * random_value * math.sqrt(dt))
    stock_price += change
    if stock_price < 1:
        stock_price = 1
    stock_history.append(stock_price)
    if len(stock_history) > SCREEN_WIDTH - 100:
        stock_history.pop(0)

def buy_shares(amount):
    """Buys a specified number of shares."""
    global player_cash, player_shares
    if not isinstance(amount, int) or amount <= 0:
        return
    cost = stock_price * amount
    if player_cash >= cost:
        player_cash -= cost
        player_shares += amount

def sell_shares(amount):
    """Sells a specified number of shares."""
    global player_cash, player_shares
    if not isinstance(amount, int) or amount <= 0:
        return
    if player_shares >= amount:
        player_cash += stock_price * amount
        player_shares -= amount

# Game loop
running = True
clock = pygame.time.Clock()
price_update_timer = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Buy shortcuts
            if event.key == pygame.K_q:
                buy_shares(1)
            if event.key == pygame.K_w:
                buy_shares(10)
            if event.key == pygame.K_e:
                buy_shares(50)
            # Sell shortcuts
            if event.key == pygame.K_a:
                sell_shares(1)
            if event.key == pygame.K_s:
                sell_shares(10)
            if event.key == pygame.K_d:
                sell_shares(50)

        # Handle input box events
        custom_buy_amount_str = custom_buy_input.handle_event(event)
        if custom_buy_amount_str:
            try:
                amount = int(custom_buy_amount_str)
                buy_shares(amount)
                custom_buy_input.text = "" # Clear input after purchase
            except ValueError:
                custom_buy_input.text = "" # Clear if not a valid number
        
        custom_sell_amount_str = custom_sell_input.handle_event(event)
        if custom_sell_amount_str:
            try:
                amount = int(custom_sell_amount_str)
                sell_shares(amount)
                custom_sell_input.text = "" # Clear input after purchase
            except ValueError:
                custom_sell_input.text = "" # Clear if not a valid number

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Buy buttons
            for i, button in enumerate(buy_buttons):
                if button.is_clicked(event.pos):
                    amounts = [1, 10, 50, 100]
                    buy_shares(amounts[i])
            if custom_buy_button.is_clicked(event.pos):
                 try:
                    amount = int(custom_buy_input.text)
                    buy_shares(amount)
                    custom_buy_input.text = ""
                 except ValueError:
                    custom_buy_input.text = ""
            if buy_max_button.is_clicked(event.pos):
                if stock_price > 0:
                    amount = int(player_cash // stock_price)
                    buy_shares(amount)

            # Sell buttons
            for i, button in enumerate(sell_buttons):
                if button.is_clicked(event.pos):
                    amounts = [1, 10, 50, 100]
                    sell_shares(amounts[i])
            if custom_sell_button.is_clicked(event.pos):
                 try:
                    amount = int(custom_sell_input.text)
                    sell_shares(amount)
                    custom_sell_input.text = ""
                 except ValueError:
                    custom_sell_input.text = ""
            if sell_max_button.is_clicked(event.pos):
                sell_shares(player_shares)


    # Update stock price
    price_update_timer += clock.get_time()
    if price_update_timer >= 250: # Update 4 times a second
        update_stock_price()
        price_update_timer = 0

    # --- Drawing ---
    screen.fill(WHITE)

    # Display player info
    draw_text(f"Cash: ${player_cash:,.2f}", 10, 10)
    draw_text(f"Shares: {player_shares}", 10, 50)
    draw_text(f"Portfolio Value: ${(player_shares * stock_price):,.2f}", 10, 90)

    # Display stock info
    price_color = GREEN if stock_price >= (stock_history[-2] if len(stock_history) > 1 else stock_price) else RED
    draw_text(f"Stock Price: ${stock_price:,.2f}", SCREEN_WIDTH - 300, 10, color=price_color)

    # Draw stock history graph
    graph_rect = pygame.Rect(50, 150, SCREEN_WIDTH - 100, 400)
    pygame.draw.rect(screen, BLACK, graph_rect, 2)

    if len(stock_history) > 1:
        # Center the graph vertically around the average price
        avg_price = sum(stock_history) / len(stock_history)
        min_price = avg_price * 0.8
        max_price = avg_price * 1.2
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1

        points = []
        # Calculate the width of each point on the graph to fill the space
        point_width = graph_rect.width / (len(stock_history) - 1) if len(stock_history) > 1 else 0
        for i, price in enumerate(stock_history):
            x = graph_rect.x + int(i * point_width)
            # Clamp price to prevent extreme values from distorting the graph too much
            clamped_price = max(min_price, min(price, max_price))
            # Flip y-axis for drawing
            y = graph_rect.bottom - int(((clamped_price - min_price) / price_range) * (graph_rect.height - 4)) - 2
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(screen, RED, False, points, 2)

    # Draw UI Elements
    for button in buy_buttons:
        button.draw(screen)
    custom_buy_input.draw(screen)
    custom_buy_button.draw(screen)
    buy_max_button.draw(screen)
    for button in sell_buttons:
        button.draw(screen)
    custom_sell_input.draw(screen)
    custom_sell_button.draw(screen)
    sell_max_button.draw(screen)


    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
