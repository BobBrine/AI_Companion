import pygame
import win32gui
import win32con
import win32api
from pet_avatar import PetAvatar
from ui import UI
from input_handler import InputHandler
import ai_core
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
pygame.key.set_repeat(500, 30)  # Enable key repeat: 500ms delay, 30ms interval
font = pygame.font.SysFont("Segoe UI", 14, bold=True)

screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
pet_avatar = PetAvatar()
pet_avatar.set_eye_mode(2)
PET_RADIUS = pet_avatar.pet_radius
ui = UI()
input_handler = InputHandler(PET_RADIUS)   

def activate_window(hwnd):
    """Bring the window to the foreground and give it focus."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0,
        0,
        0,
        0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
    )
    win32gui.SetForegroundWindow(hwnd)

input_handler.activate_window = activate_window

hwnd = pygame.display.get_wm_info()["window"]
win32gui.DragAcceptFiles(hwnd, True)
ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW
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

    is_hovering = input_handler.is_mouse_hovering(x, y)
    is_over_text_input = input_handler.is_mouse_over_text_input()
    is_in_bridge = input_handler.is_mouse_in_bridge_area(x, y)
    show_text_input = is_hovering or is_over_text_input or is_in_bridge or bool(input_handler.text_input)
    
    # Handle all input events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.DROPFILE:
            input_handler.insert_text(event.file)
            show_text_input = True
        elif event.type == pygame.DROPTEXT:
            input_handler.insert_text(event.text)
            show_text_input = True

    drop_message = win32gui.PeekMessage(
        hwnd,
        win32con.WM_DROPFILES,
        win32con.WM_DROPFILES,
        win32con.PM_REMOVE
    )
    if drop_message and len(drop_message) >= 5:
        msg, wparam, lparam, time, pt = drop_message
        if msg == win32con.WM_DROPFILES:
            file_count = win32gui.DragQueryFile(wparam, -1)
            dropped_files = [
                win32gui.DragQueryFile(wparam, i)
                for i in range(file_count)
            ]
            win32gui.DragFinish(wparam)
            if dropped_files:
                input_handler.insert_text("\n".join(dropped_files))
                show_text_input = True
    event_result = input_handler.handle_events(events, x, y, MENU_WIDTH, MENU_FULL_HEIGHT, W, H, hwnd)

    submitted_text = input_handler.handle_text_input(events, show_text_input)
    if submitted_text:   # only call the AI when there's actual input
        history = [{"role": "user", "content": submitted_text}]
        reply = ai_core.get_model_response(history)
        print("You:", submitted_text)
        print("Assistant:", reply)
        
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
    if is_hovering:
        ui.draw_hover_glow(screen, x, y)
 
    # Draw pet avatar
    pet_avatar.draw(screen, x, y)

    # Draw text input
    if show_text_input:
        text_input_rect, render_info = ui.draw_text_input(
            screen,
            x,
            y,
            input_handler.text_input,
            input_handler.cursor_pos,
            input_handler.selection_start,
            input_handler.selection_end,
            input_handler.drag_drop_cursor_pos,
            font
        )
        input_handler.text_input_rect = text_input_rect
        input_handler.set_text_render_info(render_info)
    else:
        input_handler.text_input_rect = None
        input_handler.set_text_render_info(None)

    # Draw context menu
    ui.draw_menu(screen, input_handler, mouse_pos, MENU_WIDTH, MENU_FULL_HEIGHT, 
                 BUTTON_HEIGHT, COLOR_MENU_BG, COLOR_ACCENT, COLOR_TEXT, COLOR_HOVER, font)

    pygame.display.update()

pygame.quit()