import pygame
import win32api


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
        
    def handle_events(self, events, pet_x, pet_y, menu_width, menu_full_height, screen_width, screen_height):
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
                    if self._is_point_on_pet(mouse_pos, pet_x, pet_y):
                        self.dragging = True
                        self.drag_offset_x = mouse_pos[0] - pet_x
                        self.drag_offset_y = mouse_pos[1] - pet_y
                        
            elif event.type == pygame.MOUSEBUTTONUP:
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
        Handle keyboard input for the text box.

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

            if event.key == pygame.K_RETURN:
                if self.text_input.strip():
                    submitted_text = self.text_input
                self.text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if event.unicode and event.unicode.isprintable():
                    if len(self.text_input) < self.text_input_max_len:
                        self.text_input += event.unicode

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
