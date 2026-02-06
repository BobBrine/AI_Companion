import pygame
import win32gui
import win32con
import win32api
from pet_avatar import PetAvatar
from ui import UI
from input_handler import InputHandler

# -------------------------
# Config
# -------------------------
W, H = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
FPS = 60
TRANSPARENT_COLOR = (255, 0, 255)
SPEED = 260 

# Menu Visual Config
MENU_WIDTH = 120
MENU_FULL_HEIGHT = 70
BUTTON_HEIGHT = 35
ANIM_SPEED = 8
COLOR_MENU_BG = (30, 30, 35)      
COLOR_ACCENT = (0, 150, 255)     
COLOR_TEXT = (240, 240, 240)
COLOR_HOVER = (50, 50, 60)

pygame.init()
font = pygame.font.SysFont("Segoe UI", 14, bold=True)

screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pet_avatar = PetAvatar()
pet_avatar.set_eye_mode(2)
PET_RADIUS = pet_avatar.pet_radius
ui = UI()
input_handler = InputHandler(PET_RADIUS)   
    
hwnd = pygame.display.get_wm_info()["window"]
ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT_COLOR), 0, win32con.LWA_COLORKEY)
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, W, H, win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE)

clock = pygame.time.Clock()

# Pet state
x, y = W * 0.5, H * 0.6

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    dt = clock.tick(FPS) / 1000.0

    # Handle all input events
    events = pygame.event.get()
    event_result = input_handler.handle_events(events, x, y, MENU_WIDTH, MENU_FULL_HEIGHT, W, H)
    
    if event_result['quit']:
        running = False
    
    if event_result['settings_clicked']:
        print("Settings clicked")  # Placeholder
    
    # Update pet position if dragging
    x, y = input_handler.update_dragging(x, y)
    
    # Update menu animation
    input_handler.update_menu_animation(MENU_FULL_HEIGHT, ANIM_SPEED)

    screen.fill(TRANSPARENT_COLOR)

    # Draw hover glow
    if input_handler.is_mouse_hovering(x, y):
        ui.draw_hover_glow(screen, x, y)
 
    # Draw pet avatar
    pet_avatar.draw(screen, x, y)

    # Draw context menu
    ui.draw_menu(screen, input_handler, mouse_pos, MENU_WIDTH, MENU_FULL_HEIGHT, 
                 BUTTON_HEIGHT, COLOR_MENU_BG, COLOR_ACCENT, COLOR_TEXT, COLOR_HOVER, font)

    pygame.display.update()

pygame.quit()