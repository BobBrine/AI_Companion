import pygame
import win32clipboard
import win32con
from collections import deque


class InputHandler:
    """Handles all user input including mouse clicks, dragging, and menu interactions."""
    
    def __init__(self, pet_radius):
        """
        Initialize the input handler.
        
        Args:
            pet_radius: Radius of the pet for collision detection
        """
        self.pet_radius = pet_radius
        
        # Dragging state
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Menu state
        self.menu_open = False
        self.menu_anim_height = 0
        self.menu_anchor_pos = [0, 0]  # [Target X, Anchor Bottom Y]
        self.is_opening_left = False

        # Text input state
        self.text_input = ""
        self.text_input_max_len = 60
        self.cursor_pos = 0
        self.text_input_rect = None
        self.text_input_render_info = None
        self.selection_start = 0
        self.selection_end = 0
        self.clipboard = ""
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)
        self.activate_window = None
        self.selecting = False
        self.drag_drop = False
        self.drag_drop_copy = False
        self.drag_drop_selection = (0, 0)
        self.drag_drop_cursor_pos = -1
        self._last_click_time = 0
        self._last_click_pos = (0, 0)
        self._click_count = 0
        self._record_state()

    def _record_state(self):
        state = {
            "text": self.text_input,
            "cursor": self.cursor_pos,
            "sel_start": self.selection_start,
            "sel_end": self.selection_end
        }
        if self.undo_stack and self.undo_stack[-1] == state:
            return
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def _restore_state(self, state):
        self.text_input = state["text"]
        self.cursor_pos = state["cursor"]
        self.selection_start = state["sel_start"]
        self.selection_end = state["sel_end"]

    def _copy_to_clipboard(self, text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        except Exception:
            self.clipboard = text
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass

    def _paste_from_clipboard(self):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            else:
                data = ""
        except Exception:
            return self.clipboard
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
        return data

    def set_text_render_info(self, render_info):
        self.text_input_render_info = render_info

    def insert_text(self, text):
        if not text:
            return

        if self.selection_start != self.selection_end:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.text_input = self.text_input[:start] + self.text_input[end:]
            self.cursor_pos = start

        remaining = self.text_input_max_len - len(self.text_input)
        if remaining <= 0:
            return

        text = text[:remaining]
        self.text_input = (
            self.text_input[:self.cursor_pos] +
            text +
            self.text_input[self.cursor_pos:]
        )
        self.cursor_pos += len(text)
        self.selection_start = self.selection_end = self.cursor_pos
        self._record_state()

    def _get_char_index_from_pos(self, mouse_pos):
        if not self.text_input_rect or not self.text_input_render_info:
            return 0

        text_x_start = self.text_input_render_info["text_x_start"]
        rel_x = mouse_pos[0] - text_x_start
        if rel_x <= 0:
            return 0

        font = self.text_input_render_info["font"]
        for index in range(len(self.text_input) + 1):
            if font.size(self.text_input[:index])[0] >= rel_x:
                return index
        return len(self.text_input)

    def _select_word(self, click_index):
        if not self.text_input:
            return

        def is_word_char(char):
            return char.isalnum() or char == "_"

        start = min(max(click_index, 0), len(self.text_input))
        end = start

        while start > 0 and is_word_char(self.text_input[start - 1]):
            start -= 1
        while end < len(self.text_input) and is_word_char(self.text_input[end]):
            end += 1

        self.selection_start = start
        self.selection_end = end
        self.cursor_pos = end

    def _select_all(self):
        self.selection_start = 0
        self.selection_end = len(self.text_input)
        self.cursor_pos = self.selection_end

    def _perform_drag_drop(self):
        if not self.drag_drop_selection or self.drag_drop_cursor_pos == -1:
            return

        start = min(self.drag_drop_selection)
        end = max(self.drag_drop_selection)
        drop_pos = max(0, min(self.drag_drop_cursor_pos, len(self.text_input)))

        if not self.drag_drop_copy and start <= drop_pos <= end:
            self.selection_start = self.selection_end = drop_pos
            self.cursor_pos = drop_pos
            return

        dragged_text = self.text_input[start:end]
        if self.drag_drop_copy:
            remaining = self.text_input_max_len - len(self.text_input)
            if remaining <= 0:
                return
            dragged_text = dragged_text[:remaining]
            self.text_input = (
                self.text_input[:drop_pos] +
                dragged_text +
                self.text_input[drop_pos:]
            )
            self.cursor_pos = drop_pos + len(dragged_text)
        else:
            if drop_pos > start:
                drop_pos -= (end - start)
            temp = self.text_input[:start] + self.text_input[end:]
            self.text_input = (
                temp[:drop_pos] +
                dragged_text +
                temp[drop_pos:]
            )
            self.cursor_pos = drop_pos + len(dragged_text)

        self.selection_start = self.selection_end = self.cursor_pos
        self._record_state()
        self.drag_drop_selection = (0, 0)
        
    def handle_events(self, events, pet_x, pet_y, menu_width, menu_full_height, screen_width, screen_height, hwnd):
        """
        Process all pygame events.
        
        Args:
            events: List of pygame events
            pet_x: Current pet x position
            pet_y: Current pet y position
            menu_width: Width of the context menu
            menu_full_height: Full height of the context menu
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            dict with keys: 'quit', 'settings_clicked', 'close_clicked'
        """
        result = {
            'quit': False,
            'settings_clicked': False,
            'close_clicked': False
        }
        
        mouse_pos = pygame.mouse.get_pos()
        button_height = menu_full_height // 2
        
        # Calculate current menu position for click detection
        current_menu_x = self.menu_anchor_pos[0] if self.menu_open else 0
        current_menu_y = self.menu_anchor_pos[1] - int(self.menu_anim_height) if self.menu_open else 0
        
        for event in events:
            if event.type == pygame.QUIT:
                result['quit'] = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right Click
                    if self._is_point_on_pet(mouse_pos, pet_x, pet_y):
                        self._open_menu(pet_x, pet_y, menu_width, menu_full_height, screen_width, screen_height)
                
                elif event.button == 1:  # Left Click
                    clicked_text_input = (
                        self.text_input_rect is not None and
                        self.text_input_rect.collidepoint(mouse_pos)
                    )
                    if self.activate_window:
                        rel_x = mouse_pos[0] - current_menu_x
                        rel_y = mouse_pos[1] - current_menu_y
                        is_menu_click = (
                            self.menu_open and 0 <= rel_x <= menu_width and 0 <= rel_y <= menu_full_height
                        )
                        if (self._is_point_on_pet(mouse_pos, pet_x, pet_y) or
                                clicked_text_input or is_menu_click):
                            self.activate_window(hwnd)

                    if clicked_text_input:
                        click_index = self._get_char_index_from_pos(mouse_pos)
                        now = pygame.time.get_ticks()
                        if (now - self._last_click_time <= 450 and
                                self._last_click_pos == mouse_pos):
                            self._click_count += 1
                        else:
                            self._click_count = 1

                        self._last_click_time = now
                        self._last_click_pos = mouse_pos

                        if self._click_count == 2:
                            self._select_word(click_index)
                            self.selecting = False
                            self.drag_drop = False
                            self.drag_drop_cursor_pos = -1
                        elif self._click_count >= 3:
                            self._select_all()
                            self.selecting = False
                            self.drag_drop = False
                            self.drag_drop_cursor_pos = -1
                            self._click_count = 0
                        else:
                            if (self.selection_start != self.selection_end and
                                    min(self.selection_start, self.selection_end) <= click_index <=
                                    max(self.selection_start, self.selection_end)):
                                self.drag_drop = True
                                self.drag_drop_selection = (self.selection_start, self.selection_end)
                                self.drag_drop_copy = bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
                                self.drag_drop_cursor_pos = click_index
                            else:
                                self.selecting = True
                                self.drag_drop = False
                                self.drag_drop_cursor_pos = -1
                                self.selection_start = self.selection_end = click_index
                                self.cursor_pos = click_index
                    else:
                        self.selecting = False
                        self.drag_drop = False
                        self.drag_drop_cursor_pos = -1
                        self.selection_start = self.selection_end = self.cursor_pos

                    if self.menu_open:
                        # Check menu clicks
                        rel_x = mouse_pos[0] - current_menu_x
                        rel_y = mouse_pos[1] - current_menu_y
                        
                        if 0 <= rel_x <= menu_width and 0 <= rel_y <= menu_full_height:
                            if 0 <= rel_y < button_height:
                                result['settings_clicked'] = True
                            elif button_height <= rel_y < button_height * 2:
                                result['close_clicked'] = True
                                result['quit'] = True
                        
                        self.menu_open = False
                    
                    # Start dragging
                    if self._is_point_on_pet(mouse_pos, pet_x, pet_y) and not clicked_text_input:
                        self.dragging = True
                        self.drag_offset_x = mouse_pos[0] - pet_x
                        self.drag_offset_y = mouse_pos[1] - pet_y

            elif event.type == pygame.MOUSEMOTION:
                if self.selecting and self.text_input_rect:
                    idx = self._get_char_index_from_pos(event.pos)
                    self.selection_end = idx
                    self.cursor_pos = idx
                elif self.drag_drop and self.text_input_rect:
                    self.drag_drop_cursor_pos = self._get_char_index_from_pos(event.pos)
                    self.drag_drop_copy = bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.drag_drop and self.text_input_rect:
                        self.drag_drop_copy = bool(pygame.key.get_mods() & pygame.KMOD_CTRL)
                        self._perform_drag_drop()
                    self.selecting = False
                    self.drag_drop = False
                    self.drag_drop_cursor_pos = -1
                self.dragging = False
        
        return result
    
    def update_dragging(self, pet_x, pet_y):
        """
        Update pet position if dragging.
        
        Args:
            pet_x: Current pet x position
            pet_y: Current pet y position
            
        Returns:
            tuple: (new_x, new_y) or (pet_x, pet_y) if not dragging
        """
        if self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            self.menu_open = False  # Close menu when dragging
            return mouse_pos[0] - self.drag_offset_x, mouse_pos[1] - self.drag_offset_y
        return pet_x, pet_y
    
    def update_menu_animation(self, menu_full_height, anim_speed):
        """
        Update menu animation state.
        
        Args:
            menu_full_height: Target height when fully open
            anim_speed: Animation speed factor
        """
        if self.menu_open:
            if self.menu_anim_height < menu_full_height:
                self.menu_anim_height += (menu_full_height - self.menu_anim_height) / anim_speed + 0.5
        else:
            self.menu_anim_height = 0

    def handle_text_input(self, events, allow_input):
        """
        Handle keyboard input for the text box with full text editing support.

        Args:
            events: List of pygame events
            allow_input: True when the text input is visible

        Returns:
            str or None: Submitted text when Enter is pressed, otherwise None
        """
        if not allow_input:
            return None

        submitted_text = None

        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            mods = pygame.key.get_mods()
            shift_held = mods & pygame.KMOD_SHIFT
            ctrl_held = mods & pygame.KMOD_CTRL

            if ctrl_held and event.key == pygame.K_z:
                if len(self.undo_stack) > 1:
                    self.redo_stack.append(self.undo_stack.pop())
                    self._restore_state(self.undo_stack[-1])
                continue

            if ctrl_held and event.key == pygame.K_y:
                if self.redo_stack:
                    state = self.redo_stack.pop()
                    self.undo_stack.append(state)
                    self._restore_state(state)
                continue

            if ctrl_held and event.key == pygame.K_a:
                self.selection_start = 0
                self.selection_end = len(self.text_input)
                self.cursor_pos = self.selection_end
                continue

            if ctrl_held and event.key == pygame.K_c:
                if self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self._copy_to_clipboard(self.text_input[start:end])
                continue

            if ctrl_held and event.key == pygame.K_x:
                if self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self._copy_to_clipboard(self.text_input[start:end])
                    self.text_input = self.text_input[:start] + self.text_input[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = start
                    self._record_state()
                continue

            if ctrl_held and event.key == pygame.K_v:
                paste_text = self._paste_from_clipboard()
                if paste_text:
                    paste_text = paste_text.replace("\r\n", " ").replace("\n", " ")
                    changed = False
                    if self.selection_start != self.selection_end:
                        start = min(self.selection_start, self.selection_end)
                        end = max(self.selection_start, self.selection_end)
                        self.text_input = self.text_input[:start] + self.text_input[end:]
                        self.cursor_pos = start
                        changed = True
                    remaining = self.text_input_max_len - len(self.text_input)
                    if remaining > 0:
                        paste_text = paste_text[:remaining]
                        self.text_input = (
                            self.text_input[:self.cursor_pos] +
                            paste_text +
                            self.text_input[self.cursor_pos:]
                        )
                        self.cursor_pos += len(paste_text)
                        self.selection_start = self.selection_end = self.cursor_pos
                        changed = True
                    if changed:
                        self._record_state()
                continue

            if event.key == pygame.K_RETURN:
                if self.text_input.strip():
                    submitted_text = self.text_input
                self.text_input = ""
                self.cursor_pos = 0
                self.selection_start = self.selection_end = 0
                self._record_state()
                continue

            if event.key == pygame.K_BACKSPACE:
                if self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text_input = self.text_input[:start] + self.text_input[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = start
                elif self.cursor_pos > 0:
                    self.text_input = (
                        self.text_input[:self.cursor_pos - 1] +
                        self.text_input[self.cursor_pos:]
                    )
                    self.cursor_pos -= 1
                    self.selection_start = self.selection_end = self.cursor_pos
                self._record_state()
                continue

            if event.key == pygame.K_DELETE:
                if self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text_input = self.text_input[:start] + self.text_input[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = start
                elif self.cursor_pos < len(self.text_input):
                    self.text_input = (
                        self.text_input[:self.cursor_pos] +
                        self.text_input[self.cursor_pos + 1:]
                    )
                    self.selection_start = self.selection_end = self.cursor_pos
                self._record_state()
                continue

            if event.key == pygame.K_LEFT:
                if shift_held:
                    if self.selection_start == self.selection_end:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                    self.selection_end = self.cursor_pos
                else:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                    self.selection_start = self.selection_end = self.cursor_pos
                continue

            if event.key == pygame.K_RIGHT:
                if shift_held:
                    if self.selection_start == self.selection_end:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = min(len(self.text_input), self.cursor_pos + 1)
                    self.selection_end = self.cursor_pos
                else:
                    self.cursor_pos = min(len(self.text_input), self.cursor_pos + 1)
                    self.selection_start = self.selection_end = self.cursor_pos
                continue

            if event.key == pygame.K_HOME:
                if shift_held:
                    if self.selection_start == self.selection_end:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = 0
                    self.selection_end = self.cursor_pos
                else:
                    self.cursor_pos = 0
                    self.selection_start = self.selection_end = 0
                continue

            if event.key == pygame.K_END:
                if shift_held:
                    if self.selection_start == self.selection_end:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = len(self.text_input)
                    self.selection_end = self.cursor_pos
                else:
                    self.cursor_pos = len(self.text_input)
                    self.selection_start = self.selection_end = self.cursor_pos
                continue

            if event.unicode and event.unicode.isprintable():
                if self.selection_start != self.selection_end:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    self.text_input = self.text_input[:start] + self.text_input[end:]
                    self.cursor_pos = start
                    self.selection_start = self.selection_end = start
                if len(self.text_input) < self.text_input_max_len:
                    self.text_input = (
                        self.text_input[:self.cursor_pos] +
                        event.unicode +
                        self.text_input[self.cursor_pos:]
                    )
                    self.cursor_pos += 1
                    self.selection_start = self.selection_end = self.cursor_pos
                    self._record_state()

        return submitted_text
    
    def get_menu_render_position(self):
        """
        Get the current menu rendering position.
        
        Returns:
            tuple: (x, y) position for menu rendering
        """
        current_menu_x = self.menu_anchor_pos[0]
        current_menu_y = self.menu_anchor_pos[1] - int(self.menu_anim_height)
        return current_menu_x, current_menu_y
    
    def is_mouse_over_menu_button(self, mouse_pos, button_index, button_height):
        """
        Check if mouse is over a specific menu button.
        
        Args:
            mouse_pos: Current mouse position (x, y)
            button_index: Button index (0 for settings, 1 for close)
            button_height: Height of each button
            
        Returns:
            bool: True if mouse is over the button
        """
        if not self.menu_open or self.menu_anim_height < 2:
            return False
        
        current_menu_x, current_menu_y = self.get_menu_render_position()
        rel_x = mouse_pos[0] - current_menu_x
        rel_y = mouse_pos[1] - current_menu_y
        
        button_y_start = button_index * button_height
        button_y_end = (button_index + 1) * button_height
        
        rect = pygame.Rect(0, button_y_start, 999, button_height)  # Wide width for simplicity
        return rect.collidepoint((rel_x, rel_y))
    
    def is_mouse_hovering(self, pet_x, pet_y):
        """
        Check if mouse is hovering over the pet.
        
        Args:
            pet_x: Pet center x position
            pet_y: Pet center y position
        
        Returns:
            True if mouse is within pet radius, False otherwise
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos[0], mouse_pos[1]
        
        dx = mouse_x - pet_x
        dy = mouse_y - pet_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        return distance <= self.pet_radius
    
    def is_mouse_over_text_input(self):
        """
        Check if mouse is hovering over the text input box.
        
        Returns:
            True if mouse is over the text input, False otherwise
        """
        if self.text_input_rect is None:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        return self.text_input_rect.collidepoint(mouse_pos)
    
    def is_mouse_in_bridge_area(self, pet_x, pet_y):
        """
        Check if mouse is in the bridge area between pet and text input.
        This prevents the text input from disappearing when moving cursor slowly.
        
        Args:
            pet_x: Pet center x position
            pet_y: Pet center y position
        
        Returns:
            True if mouse is in the bridge area, False otherwise
        """
        if self.text_input_rect is None:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos[0], mouse_pos[1]
        
        # Define bridge area: from bottom of pet to top of text input
        pet_bottom = pet_y + self.pet_radius
        text_input_top = self.text_input_rect.top
        
        # Check if mouse is in the vertical bridge area
        if pet_bottom <= mouse_y <= text_input_top:
            # Check if mouse is horizontally aligned with either pet or text input
            pet_left = pet_x - self.pet_radius
            pet_right = pet_x + self.pet_radius
            text_left = self.text_input_rect.left
            text_right = self.text_input_rect.right
            
            # Combine both areas for bridge
            bridge_left = min(pet_left, text_left)
            bridge_right = max(pet_right, text_right)
            
            return bridge_left <= mouse_x <= bridge_right
        
        return False
    
    def _is_point_on_pet(self, point, pet_x, pet_y):
        """Check if a point is within the pet's radius."""
        return (pet_x - self.pet_radius <= point[0] <= pet_x + self.pet_radius and
                pet_y - self.pet_radius <= point[1] <= pet_y + self.pet_radius)
    
    def _open_menu(self, pet_x, pet_y, menu_width, menu_full_height, screen_width, screen_height):
        """Calculate menu position and open it."""
        # Determine X Position (Border Logic)
        target_x = pet_x + self.pet_radius
        check_left = False
        
        # Check if it hits the right edge of the screen
        if target_x + menu_width > screen_width:
            target_x = pet_x - self.pet_radius - menu_width
            check_left = True
        
        # Determine Y Position (Stack Upward Logic)
        anchor_bottom_y = pet_y + self.pet_radius
        
        # Ensure menu doesn't go off top of screen
        if anchor_bottom_y - menu_full_height < 0:
            anchor_bottom_y = menu_full_height
        
        self.menu_anchor_pos = [target_x, anchor_bottom_y]
        self.is_opening_left = check_left
        self.menu_open = True
        self.menu_anim_height = 0
