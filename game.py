import pygame
import numpy as np
import os
import pandas as pd
import sys

# Function to scale data points to fit within a given rectangle
def scale_data(x, y, rect):
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    rect_x, rect_y, rect_width, rect_height = rect
    
    scaled_x = [(xi - x_min) / (x_max - x_min) * rect_width + rect_x for xi in x]
    scaled_y = [(1 - (yi - y_min) / (y_max - y_min)) * rect_height + rect_y for yi in y]
    
    return list(zip(scaled_x, scaled_y))

# Function to draw labels
def draw_labels(screen, font, x, y, rect):
    rect_x, rect_y, rect_width, rect_height = rect
    # X-axis labels
    for i, xi in enumerate(x):
        label = font.render(str(xi), True, (0, 0, 0))
        screen.blit(label, (rect_x + i * (rect_width / (len(x) - 1)) - label.get_width() / 2, rect_y + rect_height + 5))
    # Y-axis labels
    for yi in y:
        label = font.render(str(yi), True, (0, 0, 0))
        scaled_y = (1 - (yi - min(y)) / (max(y) - min(y))) * rect_height + rect_y
        screen.blit(label, (rect_x - label.get_width() - 5, scaled_y - label.get_height() / 2))

def get_symbols():
    symbols = []
    #read in all csv files in data folder
    for filename in os.listdir('data'):
        if filename.endswith(".csv"):
            symbols.append(filename.split('-')[0])
    #put in random order
    np.random.shuffle(symbols)
    symbols = list(symbols)
    #for each symbol, create a random alias
    aliases = []
    for symbol in symbols:
        alias = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5))
        if alias in aliases:
            while alias in aliases:
                alias = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5))
        aliases.append(alias)
    return symbols, aliases

def get_alias(selected_label,symbols,aliases):
    if selected_label == 'USDC':
        return 'USDC'
    return aliases[symbols.index(selected_label)]

def get_symbol(selected_label,symbols,aliases):
    if selected_label == 'USDC':
        return 'USDC'
    return symbols[aliases.index(selected_label)]

def pick_random_start_time():
    #read in btc data
    df = pd.read_csv('data/BTC-USD.csv')
    #get random index between 2000 and len(df) - 2000
    start_index = np.random.randint(3000,len(df) - 3000)
    #get time at index
    start_time = df['time'][start_index]
    return start_time

def update_graph_data(symbols,start_time,n_prev):
    all_price_data = []
    all_vol_data = []
    current_prices = {}
    for symbol in symbols:
        #read in csv file for symbol
        df = pd.read_csv(f'data/{symbol}-USD.csv')
        #get index of start_time
        try:
            stop_index = df[df['time'] == start_time].index[0]
        except:
            stop_index = df[df['time'] < start_time].index[0]
        #get index of stop time
        start_index = stop_index - n_prev
        #get n rows of data after start time
        df_slice = df.iloc[start_index:stop_index]
        price_data = df_slice['close'].tolist()
        vol_data = df_slice['volume'].tolist()
        #get current price
        current_price = price_data[0]
        #order data from oldest to newest
        price_data.reverse()
        vol_data.reverse()
        #get lin space for x_data
        x_data = np.linspace(1, len(price_data), len(price_data))
        all_price_data.append((x_data, price_data))
        all_vol_data.append((x_data, vol_data))
        current_prices[symbol] = current_price
    return all_price_data, all_vol_data, current_prices

def get_current_price(current_prices,symbol):
    if symbol == 'USDC':
        return 1
    else:
        return current_prices[symbol]

def transact(best_coin, current_coin, running_total,current_prices):
    '''
    goal: simulate a transaction
    '''
    if best_coin == current_coin:
        current_price = get_current_price(current_prices,best_coin)
        return current_coin, running_total,current_price
    best_coin_price = get_current_price(current_prices,best_coin)
    current_coin_price = get_current_price(current_prices,current_coin)
    #multiply running total by current coin price (this will now be in USDC)
    running_total = running_total * current_coin_price
    #multiple running total by .97 (to simulate 3% fee for each trade. gas fees fluctuate, so this is a rough estimate)
    running_total = running_total * .97
    #now convert running total to amount of best coin
    running_total = running_total / best_coin_price
    return best_coin, running_total, best_coin_price

# Initialize Pygame
pygame.init()
# Constants
scroll_speed = 150
scroll_offset = 0
#SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
#set screen width and height to full screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
#BG_COLOR = (255, 255, 255)  # White background
#set background to light gray
BG_COLOR = (200, 200, 200)
FPS = 60
last_update_time = 0
update_interval = 30000
# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Trading Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
first = True
scroll = False
symbols, aliases = get_symbols()
NUM_GRAPHS = len(symbols)
#start_time = '2023-12-21 18:19:00'
start_time = pick_random_start_time()
#convert start time to d_time object
d_start_time = pd.to_datetime(start_time)
n_prev = 10*6*24
price_data, vol_data, current_prices = update_graph_data(symbols,start_time,n_prev)
#vol_data = update_vol_data(symbols)
graph_scale = 3
selected_label = 'USDC'
current_coin = 'USDC'
running_total = 1000
dollar_amount = running_total
best_coin = 'USDC'
best_coin_price = 1
b_skip = False

# Main game loop
running = True
total_iterations = 30
delta_minutes = 60
current_iteration = 0
while running:
    if current_iteration >= total_iterations:
        break
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            scroll = True
            if event.key == pygame.K_UP:
                scroll_offset -= scroll_speed
            elif event.key == pygame.K_DOWN:
                scroll_offset += scroll_speed
        elif event.type == pygame.MOUSEBUTTONDOWN:
            scroll = True
            if event.button == 4:  # Mouse wheel up
                scroll_offset += scroll_speed
            elif event.button == 5:  # Mouse wheel down
                scroll_offset -= scroll_speed

            mouse_pos = event.pos
            for i, rect in enumerate(button_rects):
                if rect.collidepoint(mouse_pos):
                    selected_label = symbols[i]
                    best_coin = selected_label
                    b_skip = True
                    break

            if hold_rect.collidepoint(mouse_pos):
                b_skip = True
                break

            if sell_rect.collidepoint(mouse_pos):
                selected_label = 'USDC'
                best_coin = selected_label
                b_skip = True
                break


    current_time = pygame.time.get_ticks()

    # Limit the scrolling
    max_scroll = NUM_GRAPHS * 150*graph_scale - SCREEN_HEIGHT
    scroll_offset = max(-max_scroll, min(0, scroll_offset))

    if current_time - last_update_time > update_interval or b_skip == True:
        #add n minutes to start time
        d_start_time = d_start_time + pd.Timedelta(minutes=delta_minutes)
        start_time = d_start_time.strftime('%Y-%m-%d %H:%M:%S')
        price_data, vol_data, current_prices = update_graph_data(symbols,start_time,n_prev)
        best_coin, running_total, best_coin_price = transact(best_coin, current_coin, running_total, current_prices)
        current_coin = best_coin
        dollar_amount = running_total * best_coin_price
        b_skip = False
        last_update_time = current_time
        current_iteration += 1

    # Inside the main loop
    screen.fill(BG_COLOR)
    for i, (x_data, y_data) in enumerate(price_data):
        y = 100 + i * 150*graph_scale + scroll_offset  # Apply scrolling offset

        label_text = font.render(aliases[i], True, (0, 0, 0))
        screen.blit(label_text, (210, y + 40*graph_scale))

        graph_rect = (275, y, 150*graph_scale, 100*graph_scale)

        # Draw the graph rectangle
        pygame.draw.rect(screen, (0, 0, 255), graph_rect)

        # Scale and draw the graph lines
        scaled_points = scale_data(x_data, y_data, graph_rect)
        for i in range(len(scaled_points) - 1):
            pygame.draw.line(screen, (255, 0, 0), scaled_points[i], scaled_points[i+1], 2)

        # Draw labels
        #draw_labels(screen, font, x_data, y_data, graph_rect)

    for i, (x_data, y_data) in enumerate(vol_data):
        y = 100 + i * 150*graph_scale + scroll_offset  # Apply scrolling offset

        graph_rect = (750, y, 150*graph_scale, 100*graph_scale)

        # Draw the graph rectangle
        pygame.draw.rect(screen, (0, 0, 255), graph_rect)

        # Scale and draw the graph lines
        scaled_points = scale_data(x_data, y_data, graph_rect)
        for i in range(len(scaled_points) - 1):
            pygame.draw.line(screen, (255, 0, 0), scaled_points[i], scaled_points[i+1], 2)

        # Draw labels
        #draw_labels(screen, font, x_data, y_data, graph_rect)

    button_rects = []
    button_height = 30  # Example height
    button_width = 60  # Example width
    for i in range(NUM_GRAPHS):
        button_x = 1250  # X position, adjust as needed
        button_y = 200 + i * 150*graph_scale + scroll_offset  # Y position, aligned with each graph
        button_rects.append(pygame.Rect(button_x, button_y, button_width, button_height))
    for rect in button_rects:
        pygame.draw.rect(screen, (0, 150, 0), rect)
        label_text = font.render('BUY', True, (255, 255, 255))  # White text
        label_text_rect = label_text.get_rect(center=rect.center)
        screen.blit(label_text, label_text_rect)

    #add iteration number as text
    iteration_text = font.render(f'Iteration: {current_iteration}/{total_iterations}', True, (0, 0, 0))
    screen.blit(iteration_text, (1500, 300))

    time_until_next_update = update_interval - (current_time - last_update_time)
    remaining_seconds = time_until_next_update // 1000
    timer_text = font.render(f'Next update in: {remaining_seconds} seconds', True, (0, 0, 0))
    screen.blit(timer_text, (1500, 350))

    # Draw the hold button
    hold_rect = pygame.Rect(1500, 400, 100, 50)
    pygame.draw.rect(screen, (100, 100, 100), hold_rect)
    label_text = font.render('HOLD', True, (255, 255, 255))  # White text
    label_text_rect = label_text.get_rect(center=hold_rect.center)
    screen.blit(label_text, label_text_rect)

    #Draw the sell button
    sell_rect = pygame.Rect(1500, 475, 100, 50)
    #pygame.draw.rect(screen, (100, 100, 100), sell_rect)
    #draw sell button with red baaackground
    pygame.draw.rect(screen, (255, 0, 0), sell_rect)
    label_text = font.render('SELL', True, (255, 255, 255))  # White text
    label_text_rect = label_text.get_rect(center=sell_rect.center)
    screen.blit(label_text, label_text_rect)

    #display current coin price
    #current_price_text = font.render(f'Current Price: {round(best_coin_price,2)}', True, (0, 0, 0))
    #screen.blit(current_price_text, (1500, 700))

    # display running total
    #running_total_text = font.render(f'Running Total: {round(running_total,2)}', True, (0, 0, 0))
    #screen.blit(running_total_text, (1500, 800))

    # display dollar amount
    dollar_amount_text = font.render(f'Dollar Amount: {round(dollar_amount,2)}', True, (0, 0, 0))
    screen.blit(dollar_amount_text, (1500, 550))

    selected_label_text = font.render(f'Current Coin: {get_alias(selected_label,symbols,aliases)}', True, (0, 0, 0))
    screen.blit(selected_label_text, (1500, 600))
    
    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
