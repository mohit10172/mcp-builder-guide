# Dice Roller MCP Server

A Model Context Protocol (MCP) server that provides comprehensive dice rolling and random selection tools for tabletop gaming, D&D, and general randomization needs.

## Purpose

This MCP server provides a secure interface for AI assistants to roll dice, flip coins, generate D&D character stats, and make random selections for gaming and decision-making purposes.

## Features

### Current Implementation

- **`roll_dice`** - Roll any dice using standard notation (1d20, 2d6, 3d8, etc.)
- **`flip_coin`** - Flip one or multiple coins with heads/tails results
- **`roll_stats`** - Generate D&D ability scores using standard, heroic, or straight roll methods
- **`roll_with_advantage`** - Roll with advantage or disadvantage (D&D 5e style)
- **`percentile_roll`** - Roll d100 for percentage-based checks with quality indicators
- **`roll_initiative`** - Roll initiative for combat with optional bonuses
- **`random_choice`** - Pick a random option from a comma-separated list
- **`roll_loot`** - Generate loot quality based on rarity tiers

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)

## Installation

See the step-by-step instructions provided with the files.

## Usage Examples

In Claude Desktop, you can ask:

- "Roll 2d6 for damage"
- "Flip a coin"
- "Roll D&D stats using the standard method"
- "Roll with advantage on a d20"
- "Roll percentile dice"
- "Roll initiative with +3 bonus for 4 characters"
- "Choose randomly between attack, defend, or flee"
- "Roll for rare loot"

## Architecture
```
Claude Desktop → MCP Gateway → Dice Roller MCP Server → Python random module
```

## Development

### Local Testing
```bash
# Run directly
python dice_roller_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python dice_roller_server.py
```

### Adding New Tools

1. Add the function to `dice_roller_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## Troubleshooting

### Tools Not Appearing

- Verify Docker image built successfully: `docker images | grep dice-roller`
- Check catalog and registry files
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop completely

### Random Results Not Varied Enough

- The server uses Python's random module with system entropy
- Each roll is independent and truly random

## Security Considerations

- No external API calls required
- No secrets needed
- Running as non-root user in container
- Uses system random number generator

## License

MIT License