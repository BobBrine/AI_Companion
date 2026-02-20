import pygame
import math
from pet_avatar import PetAvatar

class UI:
    """Handles UI rendering including hover effects, menus, and typing indicator."""

    def __init__(self, font_name="Segoe UI"):
        self.pet_avatar = PetAvatar()
        self.pet_radius = self.pet_avatar.pet_radius
        self.font_name = font_name

        # Text box selection state
        self.text_box_text = ""
        self.text_box_lines = []
        self.text_box_line_start_indices = []
        self.text_box_font = None
        self.text_box_line_height = 0
        self.text_box_scroll_offset = 0
        self.text_box_padding = 8
        self.text_box_selection_start = 0
        self.text_box_selection_end = 0
        self.text_box_selecting = False

    def draw_hover_glow(self, screen, x, y):
        """Draw a white glow around the pet when hovering."""
        pet_rect = self.pet_avatar.pet_image.get_rect(center=(int(x), int(y)))
        pygame.draw.rect(screen, (255, 255, 255), pet_rect.inflate(4, 4))

    def draw_menu(self, screen, input_handler, mouse_pos, menu_width, menu_full_height,
                  button_height, color_bg, color_accent, color_text, color_hover, font):
        if not input_handler.menu_open or input_handler.menu_anim_height < 2:
            return

        full_menu_surf = pygame.Surface((menu_width, menu_full_height), pygame.SRCALPHA)
        pygame.draw.rect(full_menu_surf, color_bg, (0, 0, menu_width, menu_full_height), border_radius=8)

        if input_handler.is_opening_left:
            pygame.draw.rect(full_menu_surf, color_accent, (menu_width - 4, 0, 4, menu_full_height),
                             border_top_right_radius=8, border_bottom_right_radius=8)
        else:
            pygame.draw.rect(full_menu_surf, color_accent, (0, 0, 4, menu_full_height),
                             border_top_left_radius=8, border_bottom_left_radius=8)

        if input_handler.is_mouse_over_menu_button(mouse_pos, 0, button_height):
            pygame.draw.rect(full_menu_surf, color_hover, (0, 0, menu_width, button_height),
                             border_top_left_radius=8, border_top_right_radius=8)

        if input_handler.is_mouse_over_menu_button(mouse_pos, 1, button_height):
            pygame.draw.rect(full_menu_surf, color_hover, (0, button_height, menu_width, button_height),
                             border_bottom_left_radius=8, border_bottom_right_radius=8)

        text_padding = 15
        full_menu_surf.blit(font.render("Settings", True, color_text), (text_padding, 8))
        full_menu_surf.blit(font.render("Close Pet", True, color_text), (text_padding, button_height + 8))

        src_rect = pygame.Rect(0, menu_full_height - int(input_handler.menu_anim_height),
                               menu_width, int(input_handler.menu_anim_height))
        current_menu_x, current_menu_y = input_handler.get_menu_render_position()
        screen.blit(full_menu_surf, (current_menu_x, current_menu_y), src_rect)

    def draw_text_input(self, screen, x, y, text, cursor_pos, selection_start, selection_end,
                        drag_drop_cursor_pos, font, min_width=100, max_width=500, box_height=28):
        padding_y = 8
        padding_x = 8

        if text:
            text_width = font.size(text)[0] + padding_x * 2 + 10
            box_width = max(min_width, min(text_width, max_width))
        else:
            box_width = min_width

        input_x = int(x - box_width / 2)
        input_y = int(y + self.pet_radius + padding_y)

        screen_width = screen.get_width()
        if input_x < 6:
            input_x = 6
        if input_x + box_width > screen_width - 6:
            input_x = screen_width - box_width - 6
            box_width = screen_width - input_x - 6

        rect = pygame.Rect(input_x, input_y, box_width, box_height)

        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1, border_radius=6)

        text_surf = font.render(text, True, (0, 0, 0))
        cursor_text = text[:cursor_pos]
        cursor_offset = font.size(cursor_text)[0]

        scroll_x = 0
        available_width = box_width - padding_x * 2

        if cursor_offset > available_width:
            scroll_x = cursor_offset - available_width + 20

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

        screen.blit(text_surf, (rect.x + padding_x - scroll_x, rect.centery - text_surf.get_height() // 2))

        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = rect.x + padding_x + cursor_offset - scroll_x
            cursor_y_top = rect.centery - 8
            cursor_y_bottom = rect.centery + 8
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y_top), (cursor_x, cursor_y_bottom), 2)

        if drag_drop_cursor_pos != -1:
            drop_x = rect.x + padding_x + font.size(text[:drag_drop_cursor_pos])[0] - scroll_x
            pygame.draw.line(screen, (100, 100, 255),
                             (drop_x, rect.centery - 12),
                             (drop_x, rect.centery + 12), 4)

        screen.set_clip(None)

        render_info = {
            "text_x_start": rect.x + padding_x - scroll_x,
            "scroll_x": scroll_x,
            "padding_x": padding_x,
            "font": font
        }

        return rect, render_info

    def draw_typing_indicator(self, screen, pet_x, pet_y, current_time):
        bubble_width = 70
        bubble_height = 40
        tail_size = 12

        bubble_x = pet_x - bubble_width // 2
        bubble_y = pet_y - self.pet_radius - bubble_height - tail_size // 2

        if bubble_x < 5:
            bubble_x = 5
        if bubble_x + bubble_width > screen.get_width() - 5:
            bubble_x = screen.get_width() - bubble_width - 5

        bubble_surf = pygame.Surface((bubble_width, bubble_height + tail_size), pygame.SRCALPHA)

        body_rect = pygame.Rect(0, 0, bubble_width, bubble_height)
        pygame.draw.rect(bubble_surf, (255, 255, 255), body_rect, border_radius=10)
        pygame.draw.rect(bubble_surf, (0, 0, 0), body_rect, 2, border_radius=10)

        tail_points = [
            (bubble_width // 2 - tail_size // 2, bubble_height),
            (bubble_width // 2 + tail_size // 2, bubble_height),
            (bubble_width // 2, bubble_height + tail_size)
        ]
        pygame.draw.polygon(bubble_surf, (255, 255, 255), tail_points)
        pygame.draw.polygon(bubble_surf, (0, 0, 0), tail_points, 2)

        dot_radius = 4
        dot_spacing = 15
        dot_base_y = bubble_height // 2

        speed = 0.008
        phase = current_time * speed
        offsets = [
            math.sin(phase) * 6,
            math.sin(phase + 2.094) * 6,
            math.sin(phase + 4.188) * 6
        ]

        for i, offset in enumerate(offsets):
            dot_x = bubble_width // 2 - dot_spacing + i * dot_spacing
            dot_y = dot_base_y + offset
            pygame.draw.circle(bubble_surf, (0, 0, 0), (dot_x, int(dot_y)), dot_radius)

        screen.blit(bubble_surf, (bubble_x, bubble_y))

    # ------------------------------------------------------------------
    # Text box with selection support
    # ------------------------------------------------------------------
    def draw_text_box(self, screen, pet_x, pet_y, text, typing_active, base_font, scroll_offset=0):
        """
        Draw a text box above the pet with fixed font size.
        Box height expands to fit content, up to a max height; then scrolling.
        Width is fixed at 160px.
        Newlines (\n) are respected and displayed as line breaks.
        Returns (rect, total_text_height, scroll_needed).
        """
        # Fixed dimensions
        box_width = 160
        max_box_height = 200
        padding = self.text_box_padding

        # Use the passed font (size 14 bold from main) as the fixed font
        font = base_font
        line_height = font.get_linesize()

        # Helper to split a word that is too long
        def split_word_to_fit(word, font, max_width):
            """Break a word into chunks that each fit within max_width."""
            if font.size(word)[0] <= max_width:
                return [word]
            chunks = []
            current_chunk = ""
            for ch in word:
                test = current_chunk + ch
                if font.size(test)[0] <= max_width:
                    current_chunk = test
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = ch
            if current_chunk:
                chunks.append(current_chunk)
            return chunks

        # Split text by newlines, preserving empty lines
        paragraphs = text.split('\n')
        # We need to build the final display lines and their starting character indices
        lines = []                 # list of strings to display
        line_start_indices = []    # character index of the first char of each line
        char_count = 0             # total characters processed so far in original text

        for para_idx, paragraph in enumerate(paragraphs):
            # If paragraph is empty (i.e., we had a double newline), add a blank line
            if paragraph == "":
                lines.append("")
                line_start_indices.append(char_count)  # blank line has start index at current position
                # char_count does not increase because there are no characters
                # But note: the newline character itself was already consumed in split, so we don't add it.
                continue

            # Wrap this paragraph using space-splitting + long-word breaking
            words = paragraph.split(' ')
            current_line = ""
            for word in words:
                # Check if word fits in current line
                test_line = current_line + (" " if current_line else "") + word
                if font.size(test_line)[0] <= box_width - 2 * padding:
                    # It fits – add to current line
                    if not current_line:
                        # Starting a new line, record its start index
                        line_start_indices.append(char_count)
                    current_line = test_line
                    # Update char_count (add space if needed, then word length)
                    if current_line != word:   # we added a space
                        char_count += 1        # space
                    char_count += len(word)
                else:
                    # Word does not fit in current line
                    if current_line:
                        # Finish current line
                        lines.append(current_line)
                        current_line = ""
                    # Now handle the word itself – it might need splitting
                    # First, check if the word alone fits (with no preceding space)
                    if font.size(word)[0] <= box_width - 2 * padding:
                        # Word fits on its own line
                        line_start_indices.append(char_count)
                        current_line = word
                        char_count += len(word)
                    else:
                        # Word is too long – split it
                        chunks = split_word_to_fit(word, font, box_width - 2 * padding)
                        for i, chunk in enumerate(chunks):
                            line_start_indices.append(char_count)
                            lines.append(chunk)
                            char_count += len(chunk)
                            # No trailing space after chunk
                        current_line = ""   # after splitting, we start fresh for next word

            # After processing all words in the paragraph, add the last line if any
            if current_line:
                lines.append(current_line)
                # Its start index was already recorded when the line started

            # After the paragraph, if this is not the last paragraph, we need to account for the newline character
            # The newline itself is not part of the paragraph text, but we must increment char_count by 1
            # so that the next paragraph's start index is correct.
            if para_idx < len(paragraphs) - 1:
                # There is a newline between paragraphs
                char_count += 1  # the newline character

        # If no lines at all (empty text), create a dummy line
        if not lines:
            lines = [""]
            line_start_indices = [0]

        # Ensure line_start_indices length matches lines
        if len(line_start_indices) < len(lines):
            # Fallback – should not happen, but just in case
            # Fill missing start indices based on previous line
            for i in range(len(line_start_indices), len(lines)):
                # Approximate: start at previous line's start + length of previous line
                prev_start = line_start_indices[i-1]
                prev_line = lines[i-1]
                line_start_indices.append(prev_start + len(prev_line))

        # Calculate required height
        required_height = len(lines) * line_height + 2 * padding
        scroll_needed = required_height > max_box_height
        if scroll_needed:
            box_height = max_box_height
            # Clamp scroll offset
            max_scroll = required_height - box_height + 2 * padding
            scroll_offset = max(0, min(scroll_offset, max_scroll))
        else:
            box_height = required_height
            scroll_offset = 0

        # Position box above pet or typing indicator
        gap = 5
        base_y = pet_y - self.pet_radius - box_height - gap
        if typing_active:
            # Typing indicator dimensions
            bubble_height = 40
            tail_size = 12
            typing_top_y = pet_y - self.pet_radius - bubble_height - tail_size // 2
            box_y = typing_top_y - box_height - gap
        else:
            box_y = base_y

        # Center horizontally, clamp to screen edges
        box_x = pet_x - box_width // 2
        screen_width = screen.get_width()
        if box_x < 5:
            box_x = 5
        if box_x + box_width > screen_width - 5:
            box_x = screen_width - box_width - 5

        rect = pygame.Rect(box_x, box_y, box_width, box_height)

        # Store data for selection handling
        self.text_box_text = text
        self.text_box_lines = lines
        self.text_box_line_start_indices = line_start_indices
        self.text_box_font = font
        self.text_box_line_height = line_height
        self.text_box_scroll_offset = scroll_offset
        self.text_box_padding = padding

        # Draw background and border
        pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=8)

        # Draw selection highlight (if any)
        if self.text_box_selection_start != self.text_box_selection_end:
            sel_a = min(self.text_box_selection_start, self.text_box_selection_end)
            sel_b = max(self.text_box_selection_start, self.text_box_selection_end)
            for idx, line in enumerate(lines):
                line_start = line_start_indices[idx]
                line_end = line_start_indices[idx+1] if idx+1 < len(line_start_indices) else len(text)
                if sel_a < line_end and sel_b > line_start:
                    overlap_start = max(sel_a, line_start)
                    overlap_end = min(sel_b, line_end)
                    # Prefix within line (before selection)
                    prefix = text[line_start:overlap_start]
                    selected_part = text[overlap_start:overlap_end]
                    prefix_width = font.size(prefix)[0]
                    selected_width = font.size(selected_part)[0]
                    y_pos = box_y + padding + idx * line_height - scroll_offset
                    if box_y <= y_pos < box_y + box_height - padding:
                        highlight_rect = pygame.Rect(
                            box_x + padding + prefix_width,
                            y_pos,
                            selected_width,
                            line_height
                        )
                        pygame.draw.rect(screen, (173, 216, 230), highlight_rect)

        # Draw scrollbar if needed
        if scroll_needed:
            scrollbar_height = box_height * (box_height - 2 * padding) / required_height
            scrollbar_y = box_y + (scroll_offset / required_height) * box_height
            pygame.draw.rect(screen, (100, 100, 100),
                            (box_x + box_width - 8, scrollbar_y, 4, scrollbar_height),
                            border_radius=4)

        # Clip to box area and draw text
        clip_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        screen.set_clip(clip_rect)

        for i, line in enumerate(lines):
            y_pos = box_y + padding + i * line_height - scroll_offset
            if box_y <= y_pos < box_y + box_height - padding:
                text_surf = font.render(line, True, (0, 0, 0))
                screen.blit(text_surf, (box_x + padding, y_pos))

        screen.set_clip(None)

        return rect, required_height, scroll_needed
    # ------------------------------------------------------------------
    # Selection handling methods
    # ------------------------------------------------------------------
    def start_text_box_selection(self, pos, box_rect):
        """Call on mouse button down over the text box."""
        self.text_box_selecting = True
        self.text_box_selection_start = self._get_char_index_at_pos(pos, box_rect)
        self.text_box_selection_end = self.text_box_selection_start

    def update_text_box_selection(self, pos, box_rect):
        """Call on mouse motion while selecting."""
        if self.text_box_selecting:
            self.text_box_selection_end = self._get_char_index_at_pos(pos, box_rect)

    def stop_text_box_selection(self):
        """Call on mouse button up."""
        self.text_box_selecting = False

    def clear_text_box_selection(self):
        """Clear selection (e.g., when clicking outside)."""
        self.text_box_selection_start = 0
        self.text_box_selection_end = 0
        self.text_box_selecting = False

    def is_selecting_text_box(self):
        return self.text_box_selecting

    def has_text_box_selection(self):
        return self.text_box_selection_start != self.text_box_selection_end

    def get_selected_text(self):
        """Return the currently selected substring."""
        if not self.has_text_box_selection():
            return ""
        start = min(self.text_box_selection_start, self.text_box_selection_end)
        end = max(self.text_box_selection_start, self.text_box_selection_end)
        # Clamp to text length
        text = self.text_box_text
        if not text:
            return ""
        start = max(0, min(start, len(text)))
        end = max(0, min(end, len(text)))
        return text[start:end]

    def _get_char_index_at_pos(self, pos, box_rect):
        """Convert screen position to character index in the text."""
        if not self.text_box_lines or not self.text_box_font:
            return 0

        # Local coordinates relative to box top-left, with scroll offset
        x = pos[0] - box_rect.x - self.text_box_padding
        y = pos[1] - box_rect.y + self.text_box_scroll_offset - self.text_box_padding

        # Determine which line
        line_idx = int(y // self.text_box_line_height)
        if line_idx < 0:
            return 0
        if line_idx >= len(self.text_box_lines):
            return len(self.text_box_text)

        # Get the character range for this line
        line_start = self.text_box_line_start_indices[line_idx]
        line_end = (self.text_box_line_start_indices[line_idx+1]
                    if line_idx+1 < len(self.text_box_line_start_indices)
                    else len(self.text_box_text))
        line_text = self.text_box_text[line_start:line_end]

        # Find character within line based on x position
        # Iterate through characters until cumulative width exceeds x
        cumulative_width = 0
        for i, ch in enumerate(line_text):
            ch_width = self.text_box_font.size(ch)[0]
            if cumulative_width + ch_width / 2 > x:  # use half‑width threshold
                return line_start + i
            cumulative_width += ch_width
        # If we reach the end, return the index after the last character
        return line_end