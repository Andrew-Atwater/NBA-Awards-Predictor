# NBA-Awards-Predictor
COS482 Final Project

## Overview

A data collection and analysis project to predict NBA award winners for the 2026 Season.

## Data Collection

The scraper collects the following statistics for MVP candidates:

### Basic Stats
- **Big 5**: Points (PTS), Rebounds (REB), Assists (AST), Steals (STL), Blocks (BLK)
- **MPG**: Minutes Per Game
- **GP**: Games Played
- **Shooting Splits**: Field Goal % (FG%), Three-Point % (3P%), Free Throw % (FT%)

### Advanced Stats
- **USG%**: Usage Percentage
- **PER**: Player Efficiency Rating
- **VORP**: Value Over Replacement Player
- **WS**: Win Shares
- **BPM**: Box Plus/Minus

### Team Context
- **Team Record**: Wins, Losses, Win Percentage
- **Past Winner**: Binary indicator if player has won MVP before

#### In current state it is only scraping MVP names with over 100 voting points