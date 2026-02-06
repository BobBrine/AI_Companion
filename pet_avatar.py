import pygame
import win32api
import math


class PetAvatar:
    """Handles pet avatar rendering with body, eyes, and smooth eye tracking."""
    
    def __init__(self, pixel_art_scale=3):
        """
        Initialize the pet avatar.
        
        Args:
            pixel_art_scale: Scale factor for pixel art images (default 3)
        """
        self.pixel_art_scale = pixel_art_scale
        
        # Load pet body image
        pet_image_original = pygame.image.load("images/idle/idle_1.png").convert_alpha()
        new_width = pet_image_original.get_width() * pixel_art_scale
        new_height = pet_image_original.get_height() * pixel_art_scale
        self.pet_image = pygame.transform.scale(pet_image_original, (new_width, new_height))
        self.pet_radius = max(self.pet_image.get_width(), self.pet_image.get_height()) // 2
        
        # Load eye image
        self.eye_image_original = pygame.image.load("images/eyes/eye_1.png").convert_alpha()
        
        # Eye state for smooth movement
        self.eye_mode = 1
        self.eye_positions = [(0, 0)]
        self.current_eye_offsets = [(0.0, 0.0)]
        self._update_eye_image()
        self.eye_smoothness = 0.1  # Lower = smoother/slower
        self.max_eye_offset = 24  # How far eyes can move
        self.eye_tracking_enabled = True  # Enable/disable eye tracking
        
    
    def set_eye_smoothness(self, smoothness):
        """Set how smoothly the eyes move (0.05-0.2 recommended)."""
        self.eye_smoothness = smoothness
    
    def set_max_eye_offset(self, offset):
        """Set how far the eyes can move from center."""
        self.max_eye_offset = offset
    
    def enable_eye_tracking(self):
        """Enable eye tracking to follow the cursor."""
        self.eye_tracking_enabled = True
    
    def disable_eye_tracking(self):
        """Disable eye tracking - eyes stay centered."""
        self.eye_tracking_enabled = False
        # Reset eyes to center
        self.current_eye_offsets = [(0.0, 0.0) for _ in self.eye_positions]
    
    def _update_eye_image(self):
        """Update eye image based on current mode."""
        if self.eye_mode == 1:
            scale = self.pixel_art_scale
        elif self.eye_mode == 2:
            # Use integer scale to avoid blurring pixel art
            scale = max(1, self.pixel_art_scale - 1)  # e.g., 3->2, 2->1
        else:
            scale = self.pixel_art_scale
        
        eye_width = int(self.eye_image_original.get_width() * scale)
        eye_height = int(self.eye_image_original.get_height() * scale)
        self.eye_image = pygame.transform.scale(self.eye_image_original, (eye_width, eye_height))

    def set_eye_mode(self, mode):
        """Set eye mode to 1 or 2 eyes (default offsets for 2 eyes)."""
        if mode == 1:
            self.eye_mode = 1
            self.eye_positions = [(0, 0)]
        elif mode == 2:
            self.eye_mode = 2
            offset_x = 6 * self.pixel_art_scale
            offset_y = 0
            self.eye_positions = [(-offset_x, offset_y), (offset_x, offset_y)]
        else:
            raise ValueError("eye mode must be 1 or 2")

        self._update_eye_image()
        self.current_eye_offsets = [(0.0, 0.0) for _ in self.eye_positions]

    def set_eye_positions(self, positions):
        """Set custom eye positions relative to pet center."""
        self.eye_positions = positions
        self.eye_mode = len(positions)
        self.current_eye_offsets = [(0.0, 0.0) for _ in self.eye_positions]

    def _draw_eye(self, screen, x, y, cursor_x, cursor_y, eye_index):
        base_offset_x, base_offset_y = self.eye_positions[eye_index]
        eye_center_x = x + base_offset_x
        eye_center_y = y + base_offset_y

        if self.eye_tracking_enabled:
            dx = cursor_x - eye_center_x
            dy = cursor_y - eye_center_y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance > 0:
                target_eye_offset_x = (dx / distance) * min(distance, self.max_eye_offset)
                target_eye_offset_y = (dy / distance) * min(distance, self.max_eye_offset)
            else:
                target_eye_offset_x = 0
                target_eye_offset_y = 0

            current_offset_x, current_offset_y = self.current_eye_offsets[eye_index]
            current_offset_x += (target_eye_offset_x - current_offset_x) * self.eye_smoothness
            current_offset_y += (target_eye_offset_y - current_offset_y) * self.eye_smoothness
            self.current_eye_offsets[eye_index] = (current_offset_x, current_offset_y)
        else:
            # When tracking is disabled, gradually return to center
            current_offset_x, current_offset_y = self.current_eye_offsets[eye_index]
            current_offset_x *= 0.9
            current_offset_y *= 0.9
            self.current_eye_offsets[eye_index] = (current_offset_x, current_offset_y)

        eye_rect = self.eye_image.get_rect(
            center=(int(eye_center_x + current_offset_x), int(eye_center_y + current_offset_y))
        )
        screen.blit(self.eye_image, eye_rect)
    
    def draw(self, screen, x, y):
        """
        Draw the pet avatar and eyes.
        
        Args:
            screen: pygame screen surface
            x: x position of pet center
            y: y position of pet center
        """
        # Draw the pet body
        pet_rect = self.pet_image.get_rect(center=(int(x), int(y)))
        pygame.draw.rect(screen, (0, 0, 0), pet_rect.inflate(-8, -8))
        screen.blit(self.pet_image, pet_rect)
        
        # Draw eyes that follow mouse
        cursor_pos = win32api.GetCursorPos()
        cursor_x, cursor_y = cursor_pos[0], cursor_pos[1]

        for eye_index in range(len(self.eye_positions)):
            self._draw_eye(screen, x, y, cursor_x, cursor_y, eye_index)
    
    
    
    def show_preview(self, duration=500000):
        """
        Show a preview window of the pet avatar with eye tracking.
        
        Args:
            duration: How long to show preview in milliseconds (0 = until closed)
        """
        # Create preview window
        preview_width = 400
        preview_height = 400
        preview_screen = pygame.display.set_mode((preview_width, preview_height))
        pygame.display.set_caption("Pet Avatar Preview")
        
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            if duration > 0 and current_time - start_time > duration:
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        self.set_eye_mode(1)
                    elif event.key == pygame.K_2:
                        self.set_eye_mode(2)
            
            # Clear screen with white background
            preview_screen.fill((200, 200, 200))
            
            # Draw pet at center
            center_x = preview_width // 2
            center_y = preview_height // 2
            self.draw(preview_screen, center_x, center_y)
            
            # Display instructions
            font = pygame.font.Font(None, 24)
            text = font.render("Press 1 or 2 to switch eye mode | ESC to close", True, (50, 50, 50))
            preview_screen.blit(text, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()


if __name__ == "__main__":
    # Only run preview when this file is executed directly
    pygame.init()
    # Create a temporary display for image loading
    temp_screen = pygame.display.set_mode((1, 1))
    
    pet_avatar = PetAvatar()
    pet_avatar.disable_eye_tracking()
    pet_avatar.show_preview()