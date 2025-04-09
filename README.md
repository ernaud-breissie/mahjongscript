# Mahjong Game State Visualizer

A Python tool that generates visual representations of Mahjong game states from JSON data. This visualizer creates clear, graphical outputs displaying the current game state including players' hands, discards, wind positions, scores, and other game information.

## Features

- Supports both 3 and 4 player Mahjong games
- Visualizes each player's:
  - Hand tiles
  - Discarded tiles
  - Wind position
  - Score
  - Riichi status (if declared)
- Displays game information:
  - Current round wind
  - Remaining tiles count
  - Riichi bets on the table
  - Honba counter
- Highlights the winning player's area
- Uses proper Mahjong tile images with correct scaling
- Automatically adjusts layout based on game configuration
- Clear, color-coded interface for easy reading

## Installation & Dependencies

### Requirements

- Python 3.6+
- Pillow (PIL) library for image processing
- DejaVu fonts (system requirement)

```bash
# Install Pillow
pip install Pillow
```

### System Fonts
The visualizer uses DejaVu font family:
- DejaVuSans.ttf
- DejaVuSans-Bold.ttf

These fonts are commonly pre-installed on Linux distributions. If missing, install them:

```bash
# For Debian/Ubuntu systems
sudo apt-get install fonts-dejavu
```

### Image Assets
The visualizer requires tile images (35x46 pixels) in the `img/` directory following this naming convention:

- Numbered tiles (1-9):
  - Characters: `Man{n}-bordered-numbered.png`
  - Dots: `Pin{n}-bordered-numbered.png`
  - Bamboo: `Sou{n}-bordered-numbered.png`
  Where `{n}` is the number 1 through 9

- Honor tiles:
  - East wind: `Ton-bordered-lettered.png`
  - South wind: `Nan-bordered-lettered.png`
  - West wind: `Shaa-bordered-lettered.png`
  - North wind: `Pei-bordered-lettered.png`
  - Green Dragon: `Hatsu-bordered-lettered.png`
  - Red Dragon: `Chun-bordered-lettered.png`
  - White Dragon: `Haku-bordered-lettered.png`

Images should be PNG format with transparent backgrounds and consistent styling.

## Usage

### Command Line Syntax

```bash
python mahjong_visualizer.py input.json [output.png]
```

### Parameters

- `input.json`: Path to the JSON file containing the game state
- `output.png`: (Optional) Path for the output image file. Defaults to 'output.png'

### Example

```bash
# Basic usage
python mahjong_visualizer.py example_game.json

# Specify output filename
python mahjong_visualizer.py complex_game.json complex_output.png

# Generate a 3-player game visualization
python mahjong_visualizer.py test_3players.json 3player_game.png
```

The script will generate a PNG image showing the visualized game state with all players' information, game details, and current board state.

### Player Positioning

The visualizer uses a consistent layout for player positions:

- 4-player game:
  - Player 1: Top right (East seat)
  - Player 2: Bottom right (South seat)
  - Player 3: Bottom left (West seat)
  - Player 4: Top left (North seat)

- 3-player game:
  - Player 1: Top right (East seat)
  - Player 2: Bottom right (South seat)
  - Player 3: Top left (West seat)

The layout automatically adjusts based on the number of players in the game state.

## Input JSON Format

### Required Fields

```json
{
    "round_wind": "E",    /* Current round wind (E/S/W/N) */
    "players": {          /* Player data */
        "1": {            /* Player ID */
            "wind": "E",  /* Player's seat wind (E/S/W/N) */
            "score": 25000, /* Current score */
            "hand": [     /* Array of tiles in hand */
                "M1",     /* Tile notations */
                "P2",
                "S3"
            ]
        }
        /* Additional players (2, 3, 4) */
    }
}
```

### Optional Fields

```json
{
    "honba": 0,          /* Honba counter (defaults to 0) */
    "winner_id": "2",    /* ID of the winning player */
    "legend": "Text",    /* Description of the game */
    "players": {
        "1": {
            "discards": [ /* Array of discarded tiles */
                "M1",    /* Tile notations */
                "P2"
            ],
            "riichi": true /* Whether player has declared riichi */
        }
    }
}
```

### Tile Notation

Tiles are represented using the following notation system:

- **Man/Characters** (万子): `M1` through `M9`
- **Pin/Dots** (筒子): `P1` through `P9`
- **Sou/Bamboo** (索子): `S1` through `S9`
- **Winds** (風牌):
  - `E`: East (東)
  - `S`: South (南)
  - `W`: West (西)
  - `N`: North (北)
- **Dragons** (三元牌):
  - `G`: Green (發)
  - `R`: Red (中)
  - `W`: White (白)

## Field Descriptions

- `round_wind`: The current prevailing wind of the round (E/S/W/N)
- `players`: Dictionary of player data indexed by player ID (1-4)
  - `wind`: Player's seat wind position (E/S/W/N)
  - `score`: Player's current score as a number
  - `hand`: Array of tiles in the player's hand using tile notation
  - `discards`: (Optional) Array of tiles the player has discarded
  - `riichi`: (Optional) Boolean indicating if the player has declared riichi
- `honba`: (Optional) Number of honba counters in the current round
- `winner_id`: (Optional) ID of the winning player; highlights that player's area
- `legend`: (Optional) Text description of the game state

## Examples

### 4-Player Game

```json
{
    "round_wind": "E",
    "players": {
        "1": {
            "wind": "E",
            "score": 25000,
            "hand": ["M1", "M2", "M3", "P5", "P6", "P7", "S2", "S3", "S4", "E", "E", "E", "N"],
            "discards": ["M7", "P3", "S9"],
            "riichi": false
        },
        "2": {
            "wind": "S",
            "score": 24000,
            "hand": ["M4", "M5", "M6", "P1", "P1", "P1", "S5", "S6", "S7", "W", "W", "W"],
            "discards": ["M9", "P4", "S1", "N"],
            "riichi": true
        },
        "3": {
            "wind": "W",
            "score": 26000,
            "hand": ["M7", "M8", "M9", "P2", "P3", "P4", "S8", "S9", "N", "N", "N", "S", "S"],
            "discards": ["M2", "P8"],
            "riichi": false
        },
        "4": {
            "wind": "N",
            "score": 25000,
            "hand": ["M1", "M1", "M1", "P8", "P9", "S1", "S1", "S1", "S", "S", "S", "E", "E"],
            "discards": ["M6", "P7", "S2"],
            "riichi": false
        }
    },
    "winner_id": "2",
    "legend": "Example mahjong game with player 2 winning"
}
```

This example shows a standard 4-player game where:
- The round wind is East
- Player 2 has declared riichi and is the winner
- Player 1 has a triplet of East winds
- Player 3 has a triplet of North winds
- Player 4 has triplets of Man1, Sou1, and South winds
- Each player has a different number of discards

### Complex Game State

```json
{
    "round_wind": "S",
    "players": {
        "1": {
            "wind": "E",
            "score": 18500,
            "hand": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "P1", "P2", "P3", "S1"],
            "discards": ["S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "P4", "P5", "P6", "P7", "P8", "P9", "E", "S", "W", "N"],
            "riichi": false
        },
        "2": {
            "wind": "S",
            "score": 24300,
            "hand": ["P1", "P1", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P9"],
            "discards": ["M1", "M2", "M3", "S1", "S2", "S3"],
            "riichi": false
        },
        "3": {
            "wind": "W",
            "score": 26000,
            "hand": ["S1", "S1", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S9", "S9"],
            "discards": ["M1", "M2", "M3", "P1", "P2"],
            "riichi": true
        },
        "4": {
            "wind": "N",
            "score": 31200,
            "hand": ["E", "E", "E", "S", "S", "S", "W", "W", "W", "N", "N", "N", "M1"],
            "discards": ["M2", "M3", "M4", "P1", "P2", "P3", "S1", "S2"],
            "riichi": false
        }
    },
    "winner_id": "4",
    "legend": "Rare game with player 4 winning with a four-winds hand plus three dragons"
}
```

This complex example demonstrates:
- South round
- Player 1 has a full straight of Man tiles (1-9)
- Player 3 has all Sou tiles with triplets
- Player 4 has won with a rare and valuable hand containing all four wind sets
- Many more discards visible on the table
- Player 3 has declared riichi but didn't win

### 3-Player Game

```json
{
  "round_wind": "E",
  "honba": 1,
  "winner_id": "2",
  "players": {
    "1": {
      "wind": "E",
      "score": 27000,
      "hand": [
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9",
        "P1", "P2", "P3", "P4", "P5", "P6", "S1"
      ],
      "discards": [
        "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9",
        "E", "S", "W", "N", "M1", "P1", "S1", "M5"
      ]
    },
    "2": {
      "wind": "S",
      "score": 33000,
      "hand": [
        "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9",
        "S1", "S2", "S3", "S4", "S5", "S6", "S7"
      ],
      "discards": [
        "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8",
        "E", "S", "W", "N", "P1", "S1", "M9", "P9"
      ],
      "riichi": true
    },
    "3": {
      "wind": "W",
      "score": 40000,
      "hand": [
        "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9",
        "M1", "M2", "M3", "M4", "M5", "M6", "M7"
      ],
      "discards": [
        "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8",
        "E", "S", "W", "N", "S1", "M1", "S9", "P9"
      ]
    }
  }
}
```

This 3-player example shows:
- East round with 1 honba counter
- Player 2 has declared riichi and is the winner
- Larger hand sizes (16 tiles) typical in some 3-player variants
- Extensive discard piles
- Each player has a full straight of tiles in their hand
- The visualizer automatically adjusts its layout for a 3-player game configuration

## Output

The script generates:
1. A PNG image (default: 1400x1200 pixels) showing:
   - Central wind indicator
   - Player zones with:
     - Player information (ID, Wind, Score)
     - Hand tiles
     - Discards
     - Riichi indicator (if applicable)
     - Winner highlight (if specified)
2. A debug JSON file with layout information (same name as output with _debug.json suffix)

### Debug Information

The debug JSON file contains:
- Image dimensions
- Zone positions and sizes
- Player positions
- Layout information for all visual elements

### Output Examples

Below are examples of different game state visualizations:

#### Standard 4-Player Game
*Standard 4-player game layout showing:*
- All four player positions (East, South, West, North)
- Hand tiles and discards for each player
- Score displays and wind indicators
- Central round wind
- Game information panel
- Riichi declaration indicators
- Clear tile arrangements and spacing

#### Standard 3-Player Game
*3-player variant showing:*
- Modified layout with three player positions
- Larger hand sizes (16 tiles)
- Extended discard areas
- Riichi indicator for Player 2
- Honba counter in game info
- Grid-based discard arrangement
- Efficient space utilization

The visualizer automatically adjusts its layout and scaling based on:
- Number of players (3 or 4)
- Hand sizes
- Number of discards
- Screen resolution and dimensions
- Special game states (riichi, winner)

Each visualization includes a game information panel showing the round wind, remaining tiles, riichi bets, and other relevant game details.

## Configuration

### Visual Elements

The visualizer uses a consistent color scheme:
- Background: Dark green
- Player Zones: Forest green
- Winner Zone: Dark olive green
- Text: White
- Wind Indicator: Light gray
- Tiles: Floral white
- Riichi Indicator: Red border
- Zone Borders: Black

### Customization

The script includes several customizable parameters in the MahjongVisualizer class:
- DEFAULT_WIDTH = 1400
- DEFAULT_HEIGHT = 1200
- TILE_WIDTH = 35
- TILE_HEIGHT = 46
- TILE_SPACING = 6
- Various colors defined in the COLORS dictionary

## Example Files

The repository includes several example JSON files demonstrating different game scenarios:

### example_game.json
- Basic 4-player game setup
- Demonstrates standard hand sizes and basic tile arrangements
- Shows riichi declaration and winner marking
- Output: example_output.png

### complex_game.json
- Advanced 4-player game state
- Features rare hand combinations and extensive discards
- Demonstrates four-winds hand and multiple triplets
- Output: complex_output.png, complex_output_debug.json

### test_3players.json
- Complete 3-player game example
- Shows larger hand sizes (16 tiles)
- Demonstrates honba counter usage
- Features extensive discard piles
- Output: test_3players_final.png

Each example generates both a visualization PNG and a corresponding debug JSON file containing layout information. These examples serve as templates for creating your own game state files and testing different scenarios.

## Known Limitations

- Maximum hand size of 16 tiles (for 3-player games)
- Discards are displayed in a simple grid layout
- Called tiles (chi, pon, kan) are not yet specially formatted
- Fixed font sizes and positions

## Future Enhancements

Planned features:
- Support for called tile grouping visualization
- Customizable colors and dimensions via command line arguments
- Support for different tile styles and themes
- Animation support for game replay
- Support for dora indicators
- Better handling of variable hand sizes
- Optional display of point stick (thousand sticks) count

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
