            "discards": ["M9", "P4", "S1"],
            "riichi": true
        }
        // ... more players
    },
    "winner_id": "2",  // Optional: indicates the winning player
    "legend": "Game description"  // Optional: additional game information
}
```

### Player numbering and positioning

- 4-player game:
  - Player 1: Top right
  - Player 2: Bottom right
  - Player 3: Bottom left
  - Player 4: Top left

- 3-player game:
  - Player 1: Top right
  - Player 2: Bottom right
  - Player 3: Top left

### Tile notation

Tiles are represented in the following format:
- Number tiles: Letter (M/P/S) followed by number 1-9
  - M: Man (Characters)
  - P: Pin (Dots)
  - S: Sou (Bamboo)
- Honor tiles:
  - Winds: E (East), S (South), W (West), N (North)
  - Dragons: G (Green), R (Red), W (White)

Examples:
- M1: 1 of Characters
- P5: 5 of Dots
- S9: 9 of Bamboo
- E: East Wind
- G: Green Dragon

## Output

The script generates:
1. A PNG image (default: 1200x1000 pixels) showing:
   - Central wind indicator
   - Player zones with:
     - Player information (ID, Wind, Score)
     - Hand tiles
     - Discards
     - Riichi indicator (if applicable)
     - Winner highlight (if specified)
2. A debug JSON file with layout information (same name as output with _debug.json suffix)

## Visual Elements

- Background: Dark green
- Player Zones: Forest green
- Winner Zone: Dark olive green
- Text: White
- Wind Indicator: Light gray
- Tiles: Floral white
- Riichi Indicator: Red border
- Zone Borders: Black

## Customization

The script includes several customizable parameters in the MahjongVisualizer class:
- DEFAULT_WIDTH = 1200
- DEFAULT_HEIGHT = 1000
- TILE_WIDTH = 30
- TILE_HEIGHT = 40
- TILE_SPACING = 5
- Various colors defined in the COLORS dictionary

## Debug Information

The debug JSON file contains:
- Image dimensions
- Zone positions and sizes
- Player positions
- Layout information for all visual elements

## Example Files

The repository includes several example JSON files:
- example_game_current.json: Current game state with winner
- example_game_3p.json: 3-player game example
- example_game.json: Basic 4-player game
- example_game_complex.json: Complex game state with various tile types

## Known Limitations

- Hand size must not exceed 13 tiles
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
