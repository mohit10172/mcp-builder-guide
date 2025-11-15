#!/usr/bin/env python3
"""
Simple Dice Roller MCP Server - Roll dice, flip coins, and generate random outcomes for games
"""
import os
import sys
import logging
import random
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("dice-roller-server")

# Initialize MCP server
mcp = FastMCP("dice_roller")

# === UTILITY FUNCTIONS ===

def roll_single_die(sides: int) -> int:
    """Roll a single die with the specified number of sides."""
    return random.randint(1, sides)

def parse_dice_notation(notation: str):
    """Parse dice notation like '2d6' or '1d20' into count and sides."""
    try:
        notation = notation.strip().lower()
        if 'd' not in notation:
            return None, None
        
        parts = notation.split('d')
        if len(parts) != 2:
            return None, None
        
        count = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        
        if count < 1 or count > 100:
            return None, None
        if sides < 2 or sides > 1000:
            return None, None
        
        return count, sides
    except:
        return None, None

def format_roll_result(rolls, total, notation):
    """Format the result of a dice roll nicely."""
    if len(rolls) == 1:
        return f"🎲 Rolled {notation}: **{total}**"
    else:
        rolls_str = ", ".join(str(r) for r in rolls)
        return f"🎲 Rolled {notation}: [{rolls_str}] = **{total}**"

# === MCP TOOLS ===

@mcp.tool()
async def roll_dice(notation: str = "1d6") -> str:
    """Roll dice using standard notation like 1d20, 2d6, 3d8, etc."""
    logger.info(f"Rolling dice: {notation}")
    
    if not notation.strip():
        return "❌ Error: Please specify dice notation (e.g., 1d20, 2d6)"
    
    try:
        count, sides = parse_dice_notation(notation)
        
        if count is None or sides is None:
            return "❌ Error: Invalid dice notation. Use format like '1d20' or '2d6' (max 100 dice, 1000 sides)"
        
        rolls = [roll_single_die(sides) for _ in range(count)]
        total = sum(rolls)
        
        return format_roll_result(rolls, total, notation)
    
    except Exception as e:
        logger.error(f"Error rolling dice: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def flip_coin(count: str = "1") -> str:
    """Flip one or more coins and get heads or tails results."""
    logger.info(f"Flipping {count} coin(s)")
    
    try:
        num_flips = int(count) if count.strip() else 1
        
        if num_flips < 1 or num_flips > 100:
            return "❌ Error: Count must be between 1 and 100"
        
        flips = [random.choice(["Heads", "Tails"]) for _ in range(num_flips)]
        
        if num_flips == 1:
            result = flips[0]
            emoji = "👑" if result == "Heads" else "🪙"
            return f"{emoji} Coin flip: **{result}**"
        else:
            heads_count = flips.count("Heads")
            tails_count = flips.count("Tails")
            flips_str = ", ".join(flips)
            return f"""🪙 Flipped {num_flips} coins:
{flips_str}

Summary: {heads_count} Heads, {tails_count} Tails"""
    
    except ValueError:
        return f"❌ Error: Invalid count value: {count}"
    except Exception as e:
        logger.error(f"Error flipping coin: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def roll_stats(method: str = "standard") -> str:
    """Roll ability scores for D&D character creation using different methods."""
    logger.info(f"Rolling stats with method: {method}")
    
    try:
        method = method.strip().lower()
        
        if method == "standard" or method == "":
            # Roll 4d6, drop lowest, six times
            stats = []
            for _ in range(6):
                rolls = [roll_single_die(6) for _ in range(4)]
                rolls.sort()
                stat = sum(rolls[1:])  # Drop lowest
                stats.append(stat)
            
            stats_str = ", ".join(str(s) for s in stats)
            total = sum(stats)
            avg = total / 6
            
            return f"""🎲 D&D Ability Scores (4d6 drop lowest):
{stats_str}

Total: {total} | Average: {avg:.1f}"""
        
        elif method == "heroic":
            # Roll 2d6+6, six times
            stats = [roll_single_die(6) + roll_single_die(6) + 6 for _ in range(6)]
            stats_str = ", ".join(str(s) for s in stats)
            total = sum(stats)
            avg = total / 6
            
            return f"""🎲 D&D Ability Scores (2d6+6):
{stats_str}

Total: {total} | Average: {avg:.1f}"""
        
        elif method == "straight":
            # Roll 3d6, six times
            stats = [sum([roll_single_die(6) for _ in range(3)]) for _ in range(6)]
            stats_str = ", ".join(str(s) for s in stats)
            total = sum(stats)
            avg = total / 6
            
            return f"""🎲 D&D Ability Scores (3d6):
{stats_str}

Total: {total} | Average: {avg:.1f}"""
        
        else:
            return "❌ Error: Invalid method. Use 'standard', 'heroic', or 'straight'"
    
    except Exception as e:
        logger.error(f"Error rolling stats: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def roll_with_advantage(sides: str = "20", advantage_type: str = "advantage") -> str:
    """Roll with advantage or disadvantage (roll twice, take higher/lower)."""
    logger.info(f"Rolling with {advantage_type}")
    
    try:
        num_sides = int(sides) if sides.strip() else 20
        
        if num_sides < 2 or num_sides > 1000:
            return "❌ Error: Sides must be between 2 and 1000"
        
        roll1 = roll_single_die(num_sides)
        roll2 = roll_single_die(num_sides)
        
        adv_type = advantage_type.strip().lower()
        
        if adv_type == "advantage" or adv_type == "adv":
            result = max(roll1, roll2)
            emoji = "⬆️"
            type_name = "Advantage"
        elif adv_type == "disadvantage" or adv_type == "dis" or adv_type == "disadv":
            result = min(roll1, roll2)
            emoji = "⬇️"
            type_name = "Disadvantage"
        else:
            return "❌ Error: Type must be 'advantage' or 'disadvantage'"
        
        return f"""{emoji} Rolling d{num_sides} with {type_name}:
Rolls: {roll1}, {roll2}
Result: **{result}**"""
    
    except ValueError:
        return f"❌ Error: Invalid sides value: {sides}"
    except Exception as e:
        logger.error(f"Error rolling with advantage: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def percentile_roll() -> str:
    """Roll percentile dice (d100) for percentage-based checks."""
    logger.info("Rolling percentile dice")
    
    try:
        result = random.randint(1, 100)
        
        if result <= 5:
            quality = "Critical Success! 🌟"
        elif result <= 25:
            quality = "Success ✅"
        elif result <= 75:
            quality = "Moderate 📊"
        elif result <= 95:
            quality = "Failure ❌"
        else:
            quality = "Critical Failure! 💥"
        
        return f"""🎲 Percentile Roll (d100): **{result}**
{quality}"""
    
    except Exception as e:
        logger.error(f"Error rolling percentile: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def roll_initiative(bonus: str = "0", count: str = "1") -> str:
    """Roll initiative for combat (d20 + bonus) for one or more characters."""
    logger.info(f"Rolling initiative for {count} character(s)")
    
    try:
        num_count = int(count) if count.strip() else 1
        bonus_val = int(bonus) if bonus.strip() else 0
        
        if num_count < 1 or num_count > 20:
            return "❌ Error: Count must be between 1 and 20"
        
        if bonus_val < -10 or bonus_val > 20:
            return "❌ Error: Bonus must be between -10 and +20"
        
        initiatives = []
        for i in range(num_count):
            roll = roll_single_die(20)
            total = roll + bonus_val
            initiatives.append((i + 1, roll, total))
        
        # Sort by total (descending)
        initiatives.sort(key=lambda x: x[2], reverse=True)
        
        if num_count == 1:
            _, roll, total = initiatives[0]
            bonus_str = f"+{bonus_val}" if bonus_val >= 0 else str(bonus_val)
            return f"⚔️ Initiative: {roll} {bonus_str} = **{total}**"
        else:
            result_lines = ["⚔️ Initiative Order:"]
            for char_num, roll, total in initiatives:
                bonus_str = f"+{bonus_val}" if bonus_val >= 0 else str(bonus_val)
                result_lines.append(f"Character {char_num}: {roll} {bonus_str} = **{total}**")
            
            return "\n".join(result_lines)
    
    except ValueError as ve:
        return f"❌ Error: Invalid number value"
    except Exception as e:
        logger.error(f"Error rolling initiative: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def random_choice(options: str = "") -> str:
    """Pick a random option from a comma-separated list."""
    logger.info("Making random choice")
    
    if not options.strip():
        return "❌ Error: Please provide comma-separated options (e.g., 'attack, defend, flee')"
    
    try:
        choices = [opt.strip() for opt in options.split(",") if opt.strip()]
        
        if len(choices) < 2:
            return "❌ Error: Please provide at least 2 options separated by commas"
        
        if len(choices) > 50:
            return "❌ Error: Maximum 50 options allowed"
        
        choice = random.choice(choices)
        
        return f"""🎯 Random Choice:
Options: {', '.join(choices)}
Selected: **{choice}**"""
    
    except Exception as e:
        logger.error(f"Error making random choice: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def roll_loot(rarity: str = "common") -> str:
    """Generate random loot quality based on rarity tier."""
    logger.info(f"Rolling for {rarity} loot")
    
    try:
        rarity_level = rarity.strip().lower()
        
        if rarity_level == "common" or rarity_level == "":
            roll = roll_single_die(100)
            if roll <= 60:
                quality = "Poor quality item"
            elif roll <= 90:
                quality = "Average quality item"
            else:
                quality = "Good quality item"
        
        elif rarity_level == "uncommon":
            roll = roll_single_die(100)
            if roll <= 50:
                quality = "Average quality item"
            elif roll <= 85:
                quality = "Good quality item"
            else:
                quality = "Exceptional item! ✨"
        
        elif rarity_level == "rare":
            roll = roll_single_die(100)
            if roll <= 40:
                quality = "Good quality item"
            elif roll <= 80:
                quality = "Exceptional item! ✨"
            else:
                quality = "Masterwork item! ⭐"
        
        elif rarity_level == "legendary":
            roll = roll_single_die(100)
            if roll <= 30:
                quality = "Exceptional item! ✨"
            elif roll <= 70:
                quality = "Masterwork item! ⭐"
            else:
                quality = "Legendary artifact! 🏆"
        
        else:
            return "❌ Error: Rarity must be 'common', 'uncommon', 'rare', or 'legendary'"
        
        return f"""💎 Loot Roll ({rarity_level.capitalize()}):
Roll: {roll}
Result: {quality}"""
    
    except Exception as e:
        logger.error(f"Error rolling loot: {e}")
        return f"❌ Error: {str(e)}"

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Dice Roller MCP server...")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)