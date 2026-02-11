import pygame
from pet_avatar import PetAvatar


class UI:
    """Handles UI rendering including hover effects and menus."""
    
    def __init__(self):
        # Initialize pet avatar for UI
        self.pet_avatar = PetAvatar()
        self.pet_radius = self.pet_avatar.pet_radius
        
    
    def draw_hover_glow(self, screen, x, y):
        """Draw a white glow around the pet when hovering."""
        pet_rect = self.pet_avatar.pet_image.get_rect(center=(int(x), int(y)))
        pygame.draw.rect(screen, (255, 255, 255), pet_rect.inflate(4, 4))
    
    def draw_menu(self, screen, input_handler, mouse_pos, menu_width, menu_full_height, 
                  button_height, color_bg, color_accent, color_text, color_hover, font):
        """
        Draw the context menu with animation.
        
        Args:
            screen: pygame screen surface
            input_handler: InputHandler instance with menu state
            mouse_pos: Current mouse position
            menu_width: Menu width
            menu_full_height: Full menu height
            button_height: Height of each button
            color_bg: Background color
            color_accent: Accent color
            color_text: Text color
            color_hover: Hover color
            font: pygame font object
        """
        if not input_handler.menu_open or input_handler.menu_anim_height < 2:
            return
        
        # Create full menu surface
        full_menu_surf = pygame.Surface((menu_width, menu_full_height), pygame.SRCALPHA)
        
        # Background
        pygame.draw.rect(full_menu_surf, color_bg, (0, 0, menu_width, menu_full_height), border_radius=8)
        
        # Accent Border
        if input_handler.is_opening_left:
            pygame.draw.rect(full_menu_surf, color_accent, (menu_width - 4, 0, 4, menu_full_height), 
                           border_top_right_radius=8, border_bottom_right_radius=8)
        else:
            pygame.draw.rect(full_menu_surf, color_accent, (0, 0, 4, menu_full_height), 
                           border_top_left_radius=8, border_bottom_left_radius=8)
        
        # Hover effects for buttons
        if input_handler.is_mouse_over_menu_button(mouse_pos, 0, button_height):
            pygame.draw.rect(full_menu_surf, color_hover, (0, 0, menu_width, button_height),
                           border_top_left_radius=8, border_top_right_radius=8)
        
        if input_handler.is_mouse_over_menu_button(mouse_pos, 1, button_height):
            pygame.draw.rect(full_menu_surf, color_hover, (0, button_height, menu_width, button_height),
                           border_bottom_left_radius=8, border_bottom_right_radius=8)
        
        # Draw text
        text_padding = 15
        full_menu_surf.blit(font.render("Settings", True, color_text), (text_padding, 8))
        full_menu_surf.blit(font.render("Close Pet", True, color_text), (text_padding, button_height + 8))
        
        # Animation clipping (stack upward effect)
        src_rect = pygame.Rect(0, menu_full_height - int(input_handler.menu_anim_height), 
                              menu_width, int(input_handler.menu_anim_height))
        
        # Blit to screen
        current_menu_x, current_menu_y = input_handler.get_menu_render_position()
        screen.blit(full_menu_surf, (current_menu_x, current_menu_y), src_rect)

    def draw_text_input(self, screen, x, y, text, font, box_width=220, box_height=28):
        """Draw a white text input box under the pet."""
        padding_y = 8
        input_x = int(x - box_width / 2)
        input_y = int(y + self.pet_radius + padding_y)

        # Keep the input within screen bounds.
        screen_width = screen.get_width()
        if input_x < 6:
            input_x = 6
        if input_x + box_width > screen_width - 6:
            input_x = screen_width - box_width - 6

        rect = pygame.Rect(input_x, input_y, box_width, box_height)
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1, border_radius=6)

        text_surf = font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect()
        text_rect.midleft = (rect.x + 8, rect.centery)
        screen.blit(text_surf, text_rect)