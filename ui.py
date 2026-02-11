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

    def draw_text_input(self, screen, x, y, text, cursor_pos, selection_start, selection_end,
                        drag_drop_cursor_pos, font, min_width=120, max_width=500, box_height=28):
        """Draw a white text input box under the pet with auto-adjusting width and a blinking cursor."""
        padding_y = 8
        padding_x = 16  # Horizontal padding inside the box
        
        # Calculate width based on text content
        if text:
            text_width = font.size(text)[0] + padding_x * 2 + 10  # Extra space for cursor
            box_width = max(min_width, min(text_width, max_width))
        else:
            box_width = min_width
        
        input_x = int(x - box_width / 2)
        input_y = int(y + self.pet_radius + padding_y)

        # Keep the input within screen bounds
        screen_width = screen.get_width()
        if input_x < 6:
            input_x = 6
        if input_x + box_width > screen_width - 6:
            input_x = screen_width - box_width - 6
            # Recalculate box_width if needed to fit on screen
            box_width = screen_width - input_x - 6

        rect = pygame.Rect(input_x, input_y, box_width, box_height)
        
        # Draw background
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1, border_radius=6)

        # Draw text with scrolling if it exceeds box width
        text_surf = font.render(text, True, (0, 0, 0))
        text_width_actual = text_surf.get_width()
        
        # Calculate scroll offset to keep cursor visible
        cursor_text = text[:cursor_pos]
        cursor_offset = font.size(cursor_text)[0]
        
        scroll_x = 0
        available_width = box_width - padding_x * 2
        
        if cursor_offset > available_width:
            scroll_x = cursor_offset - available_width + 20
        
        # Set clip area and draw selection highlight
        clip_rect = pygame.Rect(rect.x + 8, rect.y, rect.width - 16, rect.height)
        screen.set_clip(clip_rect)

        if selection_start != selection_end:
            sel_start = min(selection_start, selection_end)
            sel_end = max(selection_start, selection_end)
            prefix_width = font.size(text[:sel_start])[0]
            selection_width = font.size(text[sel_start:sel_end])[0]
            highlight_rect = pygame.Rect(
                rect.x + padding_x - scroll_x + prefix_width,
                rect.centery - text_surf.get_height() // 2,
                selection_width,
                text_surf.get_height()
            )
            pygame.draw.rect(screen, (173, 216, 230), highlight_rect)

        # Draw text
        screen.blit(text_surf, (rect.x + padding_x - scroll_x, rect.centery - text_surf.get_height() // 2))
        
        # Draw blinking cursor
        if pygame.time.get_ticks() % 1000 < 500:  # Blink every 500ms
            cursor_x = rect.x + padding_x + cursor_offset - scroll_x
            cursor_y_top = rect.centery - 8
            cursor_y_bottom = rect.centery + 8
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)

        if drag_drop_cursor_pos != -1:
            drop_x = rect.x + padding_x + font.size(text[:drag_drop_cursor_pos])[0] - scroll_x
            pygame.draw.line(screen, (100, 100, 255),
                             (drop_x, rect.centery - 12),
                             (drop_x, rect.centery + 12), 4)
        
        screen.set_clip(None)  # Reset clipping

        render_info = {
            "text_x_start": rect.x + padding_x - scroll_x,
            "scroll_x": scroll_x,
            "padding_x": padding_x,
            "font": font
        }

        return rect, render_info