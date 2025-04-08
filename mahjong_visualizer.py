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
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 1000
    
    # Cache for loaded tile images
    tile_images = {}
    
    COLORS = {
        'background': (0, 100, 0),      # dark green
        'player_zone': (34, 139, 34),   # forest green
        'winner_zone': (85, 107, 47),   # dark olive green
        'text': (255, 255, 255),        # white
        'wind_indicator': (211, 211, 211), # light gray
        'border': (0, 0, 0),            # black
        'tile': (255, 250, 240),        # floral white
        'honor_tile': (255, 245, 238),  # seashell
        'riichi_indicator': (255, 0, 0), # red
        'dora_box': (218, 165, 32),     # goldenrod
        'section_label': (245, 245, 220), # beige
        'info_box': (47, 79, 79),       # dark slate gray
        'riichi_stick': (255, 215, 0)   # gold
    }

    TILE_WIDTH = 30
    TILE_HEIGHT = 40
    TILE_SPACING = 5
    
    def __init__(self, game_data, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.game_data = game_data
        self.validate_game_data(self.game_data)
        self.width = width
        self.height = height
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.player_width = int(self.width * 0.3)
        self.player_height = int(self.height * 0.3)
        
        # Initialize the image with background color
        self.image = Image.new('RGB', (self.width, self.height), self.COLORS['background'])
        self.draw = ImageDraw.Draw(self.image)
        
        # Try to load fonts
        try:
            self.font_normal = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            self.font_bold = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
            self.font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        except:
            self.font_normal = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
        
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
                img = img.resize((self.TILE_WIDTH, self.TILE_HEIGHT), Image.LANCZOS)
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
        info_width = 200
        info_height = 120
        padding = 10
        
        # Position in center right of the screen
        x = self.width - info_width - 20
        y = (self.height - info_height) // 2
        
        # Position in center right of the screen
        x = self.width - info_width - 20
        y = (self.height - info_height) // 2
        
        # Draw info box
        self.draw.rectangle(
            [x, y, x + info_width, y + info_height],
            fill=self.COLORS['info_box'],
            outline=self.COLORS['border'],
            width=2
        )
        
        # Calculate game information
        remaining_tiles = self.calculate_remaining_tiles()
        riichi_bets = self.count_riichi_bets()
        
        # Draw information text
        info_text = [
            "Game Information:",
            f"Round: {self.game_data['round_wind']}",
            f"Remaining: {remaining_tiles}",
            f"Riichi Bets: {riichi_bets}",
            f"Honba: {self.game_data.get('honba', 0)}"
        ]
        
        text_y = y + padding
        for line in info_text:
            self.draw.text(
                (x + padding, text_y),
                line,
                fill=self.COLORS['text'],
                font=self.font_normal
            )
            text_y += 25

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
            # Draw a separating line above discards for better visual separation
            self.draw.line(
                [x, y - 2, x + available_width, y - 2],
                fill=self.COLORS['border'],
                width=1
            )
            
            # Calculate grid layout for discards
            max_cols = int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))
            if max_cols < 1:
                max_cols = 1
                
            # Check how many rows we can fit
            max_rows = int((self.player_height - (y - int(self.player_height * 0.3)) - 10) // (self.TILE_HEIGHT + self.TILE_SPACING))
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
            tiles_per_row = int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))
            if tiles_per_row < 1:
                tiles_per_row = 1
            # Draw hand tiles with potential wrapping
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
        
        padding = 4
        label_width = text_width + 2 * padding
        label_height = text_height + 2 * padding
        
        # Draw label background
        self.draw.rectangle(
            [x, y, x + label_width, y + label_height],
            fill=self.COLORS['section_label'],
            outline=self.COLORS['border'],
            width=1
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
            width=2
        )
        
        # Draw riichi stick if applicable
        self.draw_riichi_sticks(x, y, player_data.get('riichi', False))
        
        # Draw player information
        info_y = y + 20
        player_info = [
            f'Player {player_id}' + (' (Winner)' if is_winner else ''),
            f'Wind: {player_data["wind"]}',
            f'Score: {player_data["score"]}'
        ]
        
        for line in player_info:
            self.draw.text(
                (x + 10, info_y),
                line,
                fill=self.COLORS['text'],
                font=self.font_bold
            )
            info_y += 25
        
        # Draw hand and discards with clear visual separation
        hand_y = y + 90
        
        # Calculate available width for tiles
        available_width = self.player_width - 20  # Allow for margin
        
        # Draw hand area with visual boundary
        self.draw.rectangle(
            [x + 5, hand_y - 5, x + self.player_width - 5, hand_y + self.TILE_HEIGHT * 2 + 15],
            outline=self.COLORS['border'],
            width=1
        )
        self.draw_tiles(x + 10, hand_y, player_data['hand'])
        
        # Calculate hand height based on number of tiles and width
        # Calculate hand height based on number of tiles and width
        tiles_per_row = int(available_width // (self.TILE_WIDTH + self.TILE_SPACING))
        if tiles_per_row < 1:
            tiles_per_row = 1
        hand_rows = (len(player_data['hand']) + tiles_per_row - 1) // tiles_per_row
        hand_height = hand_rows * (self.TILE_HEIGHT + self.TILE_SPACING)
        
        # Position discard zone below hand with proper spacing
        discards_y = hand_y + hand_height + 25  # Add extra spacing for clear separation
        
        # Draw discard area with visual boundary if there are discards
        if 'discards' in player_data and player_data['discards']:
            # Calculate maximum height for discards
            max_discard_height = self.player_height - (discards_y - y) - 10
            
            # Draw discard zone boundary
            self.draw.rectangle(
                [x + 5, discards_y - 5, x + self.player_width - 5, discards_y + max_discard_height],
                outline=self.COLORS['border'],
                width=1
            )
            
            # Draw connecting line between zones
            # Draw connecting line between zones
            self.draw.line(
                [x + int(self.player_width // 2), hand_y + hand_height + 5, 
                 x + int(self.player_width // 2), discards_y - 5],
                fill=self.COLORS['border'],
                width=1
            )
            
            self.draw_tiles(x + 10, discards_y, player_data['discards'], True)

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

    def generate(self, output_path):
        """Generate the visualization"""
        self.draw_all_player_zones()
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
