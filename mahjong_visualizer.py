import json
import sys
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
import os.path

class MahjongVisualizerError(Exception):
    """Base exception for MahjongVisualizer"""
    pass

class InvalidInputError(MahjongVisualizerError):
    """Raised when input JSON is invalid"""
    pass

class MahjongVisualizer:
    DEFAULT_WIDTH = 1400
    DEFAULT_HEIGHT = 1200
    
    # Cache for loaded tile images
    tile_images = {}
    
    COLORS = {
        'background': (0, 100, 0),      # dark green
        'player_zone': (34, 139, 34),   # forest green
        'winner_zone': (85, 107, 47),   # dark olive green
        'text': (255, 255, 255),        # white
        'wind_indicator': (211, 211, 211), # light gray
        'center_wind': (240, 230, 140),  # khaki
        'border': (0, 0, 0),            # black
        'tile': (255, 250, 240),        # floral white
        'honor_tile': (255, 245, 238),  # seashell
        'riichi_indicator': (255, 0, 0), # red
        'dora_box': (218, 165, 32),     # goldenrod
        'section_label': (245, 245, 220), # beige
        'info_box': (47, 79, 79),       # dark slate gray
        'riichi_stick': (255, 215, 0)   # gold
    }

    # Increase tile dimensions by 15%
    TILE_WIDTH = 35  # Was 30
    TILE_HEIGHT = 46  # Was 40
    TILE_SPACING = 6  # Was 5
    
    def __init__(self, game_data, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.game_data = game_data
        self.validate_game_data(self.game_data)
        self.width = width
        self.height = height
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.player_width = int(self.width * 0.35)
        self.player_height = int(self.height * 0.35)
        
        # Initialize the image with background color
        self.image = Image.new('RGB', (self.width, self.height), self.COLORS['background'])
        self.draw = ImageDraw.Draw(self.image)
        
        # Try to load fonts
        try:
            self.font_normal = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            self.font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
            self.font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
            self.font_info = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            self.font_info_normal = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        except:
            self.font_normal = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font_info = ImageFont.load_default()
            self.font_info_normal = ImageFont.load_default()
        
        # Preload tile images
        # Preload tile images
        self.load_tile_images()

    def validate_game_data(self, data):
        """Validate the game data structure"""
        # Check required top-level keys
        if not isinstance(data, dict):
            raise InvalidInputError("Game data must be a dictionary")
            
        if 'players' not in data:
            raise InvalidInputError("Game data missing 'players' field")
            
        if 'round_wind' not in data:
            raise InvalidInputError("Game data missing 'round_wind' field")
            
        # Validate players
        if not isinstance(data['players'], dict):
            raise InvalidInputError("Players data must be a dictionary")
            
        if not data['players']:
            raise InvalidInputError("Players data cannot be empty")
            
        for player_id, player_data in data['players'].items():
            # Check player data structure
            if not isinstance(player_data, dict):
                raise InvalidInputError(f"Player {player_id} data must be a dictionary")
                
            # Check required player fields
            for field in ['wind', 'score', 'hand']:
                if field not in player_data:
                    raise InvalidInputError(f"Player {player_id} missing required field: {field}")
            
            # Validate score is a number
            if not isinstance(player_data['score'], (int, float)):
                raise InvalidInputError(f"Player {player_id} score must be a number")
                
            # Validate hand is a list
            if not isinstance(player_data['hand'], list):
                raise InvalidInputError(f"Player {player_id} hand must be a list")
                
            # Validate optional discards
            if 'discards' in player_data and not isinstance(player_data['discards'], list):
                raise InvalidInputError(f"Player {player_id} discards must be a list")
                
            # Validate riichi flag
            if 'riichi' in player_data and not isinstance(player_data['riichi'], bool):
                raise InvalidInputError(f"Player {player_id} riichi must be a boolean")
        
        # Validate optional winner_id
        if 'winner_id' in data and str(data['winner_id']) not in data['players']:
            raise InvalidInputError(f"Winner ID {data['winner_id']} is not a valid player ID")
            
        # All validations passed
        return True

    def get_tile_image_filename(self, tile):
        if len(tile) == 1:
            # Honor tile (wind or dragon)
            if tile == 'E':
                return "Ton-bordered-lettered.png"
            elif tile == 'S':
                return "Nan-bordered-lettered.png"
            elif tile == 'W':
                return "Shaa-bordered-lettered.png"
            elif tile == 'N':
                return "Pei-bordered-lettered.png"
            else:
                # Default case if unknown
                return None
        elif len(tile) == 2:
            # Numbered tiles (Man, Pin, Sou)
            suit = tile[0]
            number = tile[1]
            
            if suit == 'M':
                return f"Man{number}-bordered-numbered.png"
            elif suit == 'P':
                return f"Pin{number}-bordered-numbered.png"
            elif suit == 'S':
                return f"Sou{number}-bordered-numbered.png"
            else:
                return None
        return None

    def load_tile_images(self):
        """Load and cache all tile images"""
        # Man (Characters) 1-9
        for i in range(1, 10):
            tile_code = f"M{i}"
            filename = f"Man{i}-bordered-numbered.png"
            self.load_and_cache_tile_image(tile_code, filename)
        
        # Pin (Dots) 1-9
        for i in range(1, 10):
            tile_code = f"P{i}"
            filename = f"Pin{i}-bordered-numbered.png"
            self.load_and_cache_tile_image(tile_code, filename)
        
        # Sou (Bamboo) 1-9
        for i in range(1, 10):
            tile_code = f"S{i}"
            filename = f"Sou{i}-bordered-numbered.png"
            self.load_and_cache_tile_image(tile_code, filename)
        
        # Honor tiles - Winds
        self.load_and_cache_tile_image("E", "Ton-bordered-lettered.png")
        self.load_and_cache_tile_image("S", "Nan-bordered-lettered.png")
        self.load_and_cache_tile_image("W", "Shaa-bordered-lettered.png")
        self.load_and_cache_tile_image("N", "Pei-bordered-lettered.png")

    def load_and_cache_tile_image(self, tile_code, filename):
        """Load a single tile image and cache it"""
        try:
            img_path = os.path.join("img", filename)
            if os.path.exists(img_path):
                # Load and resize the image
                img = Image.open(img_path)
                img = img.resize((self.TILE_WIDTH, self.TILE_HEIGHT), Image.Resampling.LANCZOS)
                # Store in cache
                self.tile_images[tile_code] = img
        except Exception as e:
            print(f"Warning: Failed to load tile image {filename}: {e}")

    def calculate_remaining_tiles(self):
        """Calculate the number of remaining tiles in the wall"""
        total_tiles = 136  # Total tiles in a standard set
        used_tiles = 0
        
        for player in self.game_data['players'].values():
            used_tiles += len(player['hand'])
            if 'discards' in player:
                used_tiles += len(player['discards'])
        
        return total_tiles - used_tiles

    def count_riichi_bets(self):
        """Count the number of riichi bets on the table"""
        return sum(1 for player in self.game_data['players'].values() 
                  if player.get('riichi', False))

    def draw_game_info(self):
        """Draw game information box"""
        info_width = 280
        info_width = 300
        info_height = 220
        padding = 20
        # Position in center right of the screen
        x = self.width - info_width - 30
        y = (self.height - info_height) // 2
        
        # Draw info box
        self.draw.rectangle(
            [x, y, x + info_width, y + info_height],
            fill=self.COLORS['info_box'],
            outline=self.COLORS['border'],
            width=3
        )
        
        # Calculate game information
        remaining_tiles = self.calculate_remaining_tiles()
        riichi_bets = self.count_riichi_bets()
        
        # Draw title
        title = "Game Information"
        title_bbox = self.draw.textbbox((0, 0), title, font=self.font_info)
        title_width = title_bbox[2] - title_bbox[0]
        
        self.draw.text(
            (x + (info_width - title_width) // 2, y + padding),
            title,
            fill=self.COLORS['text'],
            font=self.font_info
        )
        
        # Draw separator line
        separator_y = y + padding*3
        self.draw.line(
            [x + padding, separator_y, x + info_width - padding, separator_y],
            fill=self.COLORS['text'],
            width=2
        )
        
        # Draw information text
        info_items = [
            ["Round:", f"{self.game_data['round_wind']}"],
            ["Remaining:", f"{remaining_tiles}"],
            ["Riichi Bets:", f"{riichi_bets}"],
            ["Honba:", f"{self.game_data.get('honba', 0)}"]
        ]
        
        text_y = separator_y + padding*2
        line_spacing = 35  # Increased line spacing
        
        for label, value in info_items:
            # Draw label
            self.draw.text(
                (x + padding*2, text_y),
                label,
                fill=self.COLORS['text'],
                font=self.font_info_normal
            )
            
            # Calculate value text dimensions to ensure it stays within bounds
            value_bbox = self.draw.textbbox((0, 0), value, font=self.font_info_normal)
            value_width = value_bbox[2] - value_bbox[0]
            
            # Calculate maximum width available for the value
            # Calculate maximum width available for the value
            max_value_width = info_width - padding*5 - 110  # Increased margin for better separation
            # If value text is too long, truncate or adjust
            display_value = value
            if value_width > max_value_width:
                display_value = value[:10] + "..."  # Simple truncation approach
            
            # Draw value text
            self.draw.text(
                (x + info_width - padding*2 - value_width, text_y),
                display_value,
                fill=self.COLORS['text'],
                font=self.font_info_normal
            )
            
            text_y += line_spacing

    def draw_riichi_sticks(self, player_x, player_y, is_riichi):
        """Draw riichi stick indication"""
        if not is_riichi:
            return
            
        stick_width = 40
        stick_height = 8
        padding = 5
        
        # Draw stick at the top of player zone
        self.draw.rectangle(
            [player_x + padding, 
             player_y + padding,
             player_x + padding + stick_width,
             player_y + padding + stick_height],
            fill=self.COLORS['riichi_stick'],
            outline=self.COLORS['border'],
            width=1
        )

    def draw_tile(self, x, y, tile):
        """Draw a single mahjong tile"""
        # Check if we have the image in our cache
        if tile in self.tile_images:
            # Paste the tile image
            self.image.paste(self.tile_images[tile], (x, y))
        else:
            # Fallback to text-based drawing if image not available
            is_honor = len(tile) == 1 or tile[0] in ['E', 'S', 'W', 'N', 'G', 'R']
            
            # Draw tile background
            self.draw.rectangle(
                [x, y, x + self.TILE_WIDTH, y + self.TILE_HEIGHT],
                fill=self.COLORS['honor_tile'] if is_honor else self.COLORS['tile'],
                outline=self.COLORS['border'],
                width=1
            )
            
            # Draw tile text
            text_bbox = self.draw.textbbox((0, 0), tile, font=self.font_small)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = x + (self.TILE_WIDTH - text_width) // 2
            text_y = y + (self.TILE_HEIGHT - text_height) // 2
            
            self.draw.text(
                (text_x, text_y),
                tile,
                fill=self.COLORS['border'],
                font=self.font_small
            )

    def draw_tiles(self, x, y, tiles, is_discards=False):
        """Draw a group of tiles"""
        if not tiles:
            return
            
        # Draw section label with clear visual marking
        label = "Discards" if is_discards else "Hand"
        label_height = self.draw_section_label(x, y, label)
        y += label_height + 5
        
        # Calculate available space
        available_width = self.player_width - 20  # Allow for margin
        
        if is_discards:
            # Remove separating line for cleaner look
            
            # Calculate grid layout for discards
            # Calculate grid layout for discards - optimized for larger tiles
            max_cols = int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))
            if max_cols < 1:
                max_cols = 1
                
            # Ensure we can fit at least 6 tiles per row for up to 18 tiles
            max_cols = min(max_cols, 6)
                
            # Check how many rows we can fit - account for larger tiles
            max_rows = int((self.player_height - (y - int(self.player_height * 0.3)) - 20) // (self.TILE_HEIGHT + self.TILE_SPACING))
            if max_rows < 1:
                max_rows = 1
                
            # Calculate total tiles that can be displayed
            total_tiles_displayable = max_cols * max_rows
            
            # If we have more tiles than can fit, limit the display
            tiles_to_display = tiles[:total_tiles_displayable] if len(tiles) > total_tiles_displayable else tiles
            
            for i, tile in enumerate(tiles_to_display):
                col = i % max_cols
                row = i // max_cols
                
                tile_x = x + col * (self.TILE_WIDTH + self.TILE_SPACING)
                tile_y = y + row * (self.TILE_HEIGHT + self.TILE_SPACING)
                
                self.draw_tile(tile_x, tile_y, tile)
        else:
            # For hand tiles, calculate how many can fit in a row
            # For hand tiles, calculate how many can fit in a row
            # For hand tiles, calculate how many can fit in a row - optimized for larger tiles
            tiles_per_row = int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))
            if tiles_per_row < 1:
                tiles_per_row = 1
            
            # Ensure we can fit at least 6 tiles per row for up to 18 tiles
            tiles_per_row = min(tiles_per_row, 6)
            for i, tile in enumerate(tiles):
                row = i // tiles_per_row
                col = i % tiles_per_row
                
                tile_x = x + col * (self.TILE_WIDTH + self.TILE_SPACING)
                tile_y = y + row * (self.TILE_HEIGHT + self.TILE_SPACING)
                
                self.draw_tile(tile_x, tile_y, tile)

    def draw_section_label(self, x, y, text):
        """Draw a labeled section with background"""
        text_bbox = self.draw.textbbox((0, 0), text, font=self.font_small)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        padding = 3  # Reduced padding
        label_width = text_width + 2 * padding
        label_height = text_height + 2 * padding
        
        # Draw label background
        self.draw.rectangle(
            [x, y, x + label_width, y + label_height],
            fill=self.COLORS['section_label'],
            outline=None  # Remove the border for a cleaner look
        )
        
        # Draw label text
        self.draw.text(
            (x + padding, y + padding),
            text,
            fill=self.COLORS['border'],
            font=self.font_small
        )
        
        return label_height

    def draw_player_zone(self, player_id, position):
        """Draw a player's zone with all components"""
        positions = {
            'top_right': (self.width - self.player_width, 0),
            'bottom_right': (self.width - self.player_width, self.height - self.player_height),
            'bottom_left': (0, self.height - self.player_height),
            'top_left': (0, 0)
        }
        
        x, y = positions[position]
        player_data = self.game_data['players'][str(player_id)]
        is_winner = str(player_id) == self.game_data.get('winner_id', '')
        
        # Draw zone background
        self.draw.rectangle(
            [x, y, x + self.player_width, y + self.player_height],
            fill=self.COLORS['winner_zone'] if is_winner else self.COLORS['player_zone'],
            outline=self.COLORS['border'],
            width=3  # Make the border thicker for better visibility
        )
        
        # Calculate total available space for content
        total_available_height = self.player_height - 30  # Allocate space for margins
        
        # Draw player information
        info_y = y + 10  # Reduced top margin
        player_info = [
            f'Player {player_id}' + (' (Winner)' if is_winner else ''),
            f'Wind: {player_data["wind"]}',
            f'Score: {player_data["score"]}'
        ]
        
        # Draw information box background for better readability
        text_width = max(self.draw.textbbox((0, 0), line, font=self.font_bold)[2] for line in player_info)
        text_height = len(player_info) * 25  # Reduced line height
        info_box_height = text_height + 8  # Reduced padding
        
        self.draw.rectangle(
            [x + 8, info_y - 5, x + text_width + 25, info_y + text_height + 5],
            fill=self.COLORS['info_box'],
            outline=self.COLORS['border'],
            width=1
        )
        
        for line in player_info:
            self.draw.text(
                (x + 15, info_y),  # Increased left margin
                line,
                fill=self.COLORS['text'],
                font=self.font_bold
            )
            info_y += 25  # Reduced line spacing
        
        # Draw riichi stick if applicable
        if player_data.get('riichi', False):
            self.draw_riichi_sticks(x, y, True)
        
        # Calculate available width for tiles
        available_width = self.player_width - 30  # Increased margin for safety
        
        # Calculate optimal tiles per row based on available width
        tiles_per_row = max(1, min(6, int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))))
        
        # Calculate space needed for hand and discards
        # Start hand zone after info box with padding
        hand_y = y + info_box_height + 30  # Reduced padding
        
        # Calculate maximum available height for the rest of the content
        max_remaining_height = self.player_height - (hand_y - y) - 20  # 20px bottom margin
        
        # Calculate how many rows we can fit for hand tiles
        max_hand_rows = max(1, (max_remaining_height // 2 - 30) // (self.TILE_HEIGHT + self.TILE_SPACING))
        
        # Limit hand rows if we have too many tiles
        hand_rows_needed = (len(player_data['hand']) + tiles_per_row - 1) // tiles_per_row
        hand_rows = min(hand_rows_needed, max_hand_rows)
        
        # Calculate actual hand height with optimized rows
        hand_height = hand_rows * (self.TILE_HEIGHT + self.TILE_SPACING) + 20  # Reduced label height
        
        # Calculate remaining space after hand
        remaining_height = max_remaining_height - hand_height - 50  # 50px min spacing
        # Check if we have discards to display
        if 'discards' in player_data and player_data['discards']:
            # Calculate discards space requirements
            discards_tiles = player_data['discards']
            discards_tiles_per_row = max(1, min(6, int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))))
            
            # Calculate how many rows we can fit in remaining space
            max_discard_rows = max(1, (remaining_height - 20) // (self.TILE_HEIGHT + self.TILE_SPACING))
            
            # Limit discard rows if we have too many tiles
            discard_rows_needed = (len(discards_tiles) + discards_tiles_per_row - 1) // discards_tiles_per_row
            discard_rows = min(discard_rows_needed, max_discard_rows)
            
            # Calculate actual discards height with optimized rows
            discards_height = discard_rows * (self.TILE_HEIGHT + self.TILE_SPACING) + 20  # Reduced label height
            
            # Ensure minimum spacing between hand and discards (at least 50px)
            min_spacing = 50
            
            # Calculate discards position with sufficient spacing
            discards_y = hand_y + hand_height + min_spacing
            # Strict boundary check for discards zone
            if (discards_y + discards_height) > (y + self.player_height - 10):
                # Emergency adjustment - reduce spacing if still too tight
                if min_spacing > 30:
                    min_spacing = 30
                    discards_y = hand_y + hand_height + min_spacing
                
                # Final check to ensure we're within boundaries
                max_allowed_height = (y + self.player_height - 10) - discards_y
                max_allowed_rows = max(1, int(max_allowed_height - 20) // (self.TILE_HEIGHT + self.TILE_SPACING))
                
                # Adjust display if still not enough space
                if max_allowed_rows < discard_rows:
                    discard_rows = max_allowed_rows
                    
                    # Add an indicator that not all discards are shown
                    truncated_message = f"(Showing {max_allowed_rows * discards_tiles_per_row} of {len(discards_tiles)} discards)"
                    self.draw.text(
                        (x + 15, discards_y - 15),
                        truncated_message,
                        fill=self.COLORS['text'],
                        font=self.font_small
                    )
            
            # Draw hand tiles first
            self.draw_tiles(x + 15, hand_y, player_data['hand'])
            
            # Draw discards below with proper spacing
            self.draw_tiles(x + 15, discards_y, player_data['discards'], True)
            
            # Limit the number of discards shown based on available space
            tiles_to_show = min(len(discards_tiles), discard_rows * discards_tiles_per_row)
            
            # Draw hand tiles first
            self.draw_tiles(x + 15, hand_y, player_data['hand'][:hand_rows * tiles_per_row])
            
            # Draw discards below with proper spacing
            self.draw_tiles(x + 15, discards_y, discards_tiles[:tiles_to_show], True)
            
            # Draw debug measurements if needed - uncomment for debugging
            # debug_color = (255, 0, 0)  # red
            # self.draw.line([x + 5, y + self.player_height - 10, x + self.player_width - 5, y + self.player_height - 10], fill=debug_color, width=2)
            # self.draw.line([x + 5, hand_y, x + self.player_width - 5, hand_y], fill=debug_color, width=1)
            # self.draw.line([x + 5, hand_y + hand_height, x + self.player_width - 5, hand_y + hand_height], fill=debug_color, width=1)
            # self.draw.line([x + 5, discards_y, x + self.player_width - 5, discards_y], fill=debug_color, width=1)
            # self.draw.line([x + 5, discards_y + discards_height, x + self.player_width - 5, discards_y + discards_height], fill=debug_color, width=1)
        else:
            # Only hand tiles to draw - can use more space
            max_hand_rows = max(1, (max_remaining_height - 20) // (self.TILE_HEIGHT + self.TILE_SPACING))
            hand_rows = min((len(player_data['hand']) + tiles_per_row - 1) // tiles_per_row, max_hand_rows)
            tiles_to_show = min(len(player_data['hand']), hand_rows * tiles_per_row)
            
            self.draw_tiles(x + 15, hand_y, player_data['hand'][:tiles_to_show])

    def draw_all_player_zones(self):
        """Draw all player zones"""
        positions_4_players = {
            '1': 'top_right',
            '2': 'bottom_right',
            '3': 'bottom_left',
            '4': 'top_left'
        }
        
        positions_3_players = {
            '1': 'top_right',
            '2': 'bottom_right',
            '3': 'top_left'
        }
        
        positions = positions_4_players if len(self.game_data['players']) == 4 else positions_3_players
        
        for player_id, position in positions.items():
            if player_id in self.game_data['players']:
                self.draw_player_zone(player_id, position)

    def draw_center_wind(self):
        """Draw the round wind in the center of the board"""
        wind = self.game_data['round_wind']
        
        # Create a circular background for the wind indicator
        circle_radius = 140  # Larger circle for more prominence
        
        # Draw circle background
        self.draw.ellipse(
            (self.center_x - circle_radius, 
             self.center_y - circle_radius,
             self.center_x + circle_radius, 
             self.center_y + circle_radius),
            fill=self.COLORS['center_wind'],
            outline=self.COLORS['border'],
            width=4  # Thicker outline for better visibility
        )
        
        # Draw wind character - get appropriate large font
        try:
            wind_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 120)  # Larger font for better prominence
        except:
            wind_font = self.font_info
        
        # Draw wind text
        wind_text = wind
        text_bbox = self.draw.textbbox((0, 0), wind_text, font=wind_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        self.draw.text(
            (self.center_x - text_width // 2, self.center_y - text_height // 2),
            wind_text,
            fill=self.COLORS['border'],
            font=wind_font
        )
        
        # Add "Round Wind" text below the circle
        label_text = "Round Wind"
        label_bbox = self.draw.textbbox((0, 0), label_text, font=self.font_bold)
        label_width = label_bbox[2] - label_bbox[0]
        
        self.draw.text(
            (self.center_x - label_width // 2, self.center_y + circle_radius + 10),
            label_text,
            fill=self.COLORS['text'],
            font=self.font_info  # Use larger font for better visibility
        )

    def generate(self, output_path):
        """Generate the visualization"""
        self.draw_all_player_zones()
        self.draw_center_wind()
        self.draw_game_info()
        self.image.save(output_path)

def main():
    if len(sys.argv) < 2:
        print('Usage: python mahjong_visualizer.py input.json [output.png]')
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output.png'

    try:
        with open(input_file, 'r') as f:
            game_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    try:
        visualizer = MahjongVisualizer(game_data)
        visualizer.generate(output_file)
    except MahjongVisualizerError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
