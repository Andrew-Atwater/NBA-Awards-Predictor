# NBA Stats collector using NBA API playergamelog endpoint
import pandas as pd
import requests
import time
import json
from datetime import datetime
import random

class NBAStatsCollector:
    def __init__(self):
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://stats.nba.com/',
            'Origin': 'https://stats.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true'
        }
        
    def season_to_year(self, season_str):
        return season_str
    
    def get_player_id(self, player_name, season):
        url = f"{self.base_url}/commonallplayers"
        params = {
            'LeagueID': '00',
            'Season': season,
            'IsOnlyCurrentSeason': '0'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            players = data['resultSets'][0]['rowSet']
            player_name_clean = player_name.lower().strip()
            
            for player in players:
                player_id, full_name = player[0], player[2].lower()
                if player_name_clean in full_name or full_name in player_name_clean:
                    return player_id
                    
            print(f"Player ID not found for {player_name}")
            return None
            
        except Exception as e:
            print(f"Error finding player ID for {player_name}: {e}")
            return None
    
    def get_player_season_stats(self, player_id, season):
        stats = {}
        # Get big 5 stats
        traditional_stats = self._get_traditional_stats(player_id, season)
        if traditional_stats:
            stats.update(traditional_stats)
        
        # Get advanced stats
        advanced_stats = self._get_advanced_stats(player_id, season)
        if advanced_stats:
            stats.update(advanced_stats)
            
        return stats
    
    def _get_traditional_stats(self, player_id, season):
        url = f"{self.base_url}/playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': season,
            'SeasonType': 'Regular Season'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            rows = data['resultSets'][0]['rowSet']
            headers = data['resultSets'][0]['headers']
            
            if not rows:
                return None
            
            # Calculate averages from game log
            gp = len(rows)
            totals = {
                'MIN': 0, 'PTS': 0, 'REB': 0, 'AST': 0, 'STL': 0, 'BLK': 0,
                'FGM': 0, 'FGA': 0, 'FG3M': 0, 'FG3A': 0, 'FTM': 0, 'FTA': 0
            }
            team = None
            
            wins = 0
            losses = 0
            
            for row in rows:
                row_dict = dict(zip(headers, row))
                if team is None:
                    team = row_dict.get('MATCHUP', '').split()[0]  # Get team abbreviation
                
                # Track W/L from game log
                wl = row_dict.get('WL', '')
                if wl == 'W':
                    wins += 1
                elif wl == 'L':
                    losses += 1
                
                totals['MIN'] += row_dict.get('MIN', 0) or 0
                totals['PTS'] += row_dict.get('PTS', 0) or 0
                totals['REB'] += row_dict.get('REB', 0) or 0
                totals['AST'] += row_dict.get('AST', 0) or 0
                totals['STL'] += row_dict.get('STL', 0) or 0
                totals['BLK'] += row_dict.get('BLK', 0) or 0
                totals['FGM'] += row_dict.get('FGM', 0) or 0
                totals['FGA'] += row_dict.get('FGA', 0) or 0
                totals['FG3M'] += row_dict.get('FG3M', 0) or 0
                totals['FG3A'] += row_dict.get('FG3A', 0) or 0
                totals['FTM'] += row_dict.get('FTM', 0) or 0
                totals['FTA'] += row_dict.get('FTA', 0) or 0
            
            # Calculate shooting percentages
            fg_pct = (totals['FGM'] / totals['FGA'] * 100) if totals['FGA'] > 0 else 0
            fg3_pct = (totals['FG3M'] / totals['FG3A'] * 100) if totals['FG3A'] > 0 else 0
            ft_pct = (totals['FTM'] / totals['FTA'] * 100) if totals['FTA'] > 0 else 0
            
            return {
                'GP': gp,
                'MPG': round(totals['MIN'] / gp, 1),
                'PTS': round(totals['PTS'] / gp, 1),
                'REB': round(totals['REB'] / gp, 1),
                'AST': round(totals['AST'] / gp, 1),
                'STL': round(totals['STL'] / gp, 1),
                'BLK': round(totals['BLK'] / gp, 1),
                'FG_PCT': round(fg_pct, 1),
                'FG3_PCT': round(fg3_pct, 1),
                'FT_PCT': round(ft_pct, 1),
                'TEAM': team or 'N/A',
                'TEAM_WINS': wins,
                'TEAM_LOSSES': losses
            }
            
        except Exception as e:
            print(f"Error getting Big 5 stats: {e}")
            return None
    
    def _get_advanced_stats(self, player_id, season):
        # I'm skipping advanced stats for now but will implement later
        # Likely will need to use a different method for this as well
        return {
            'USG_PCT': None,
            'OFF_RATING': None,
            'DEF_RATING': None,
            'NET_RATING': None,
            'PIE': None
        }
    
    def get_team_record(self, team_abbr, season):
        url = f"{self.base_url}/leaguestandingsv3"
        params = {
            'LeagueID': '00',
            'Season': season,
            'SeasonType': 'Regular Season'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            rows = data['resultSets'][0]['rowSet']
            headers = data['resultSets'][0]['headers']
            
            for row in rows:
                row_dict = dict(zip(headers, row))
                team_abbrev = row_dict.get('TeamAbbreviation', '')
                
                # Match by abbreviation
                if team_abbrev == team_abbr:
                    wins = row_dict.get('WINS', row_dict.get('W', 0))
                    losses = row_dict.get('LOSSES', row_dict.get('L', 0))
                    return f"{wins}-{losses}"
            
            # If not found, try alternate method with team info
            team_id = self._get_team_id(team_abbr)
            if team_id and team_id != '0':
                return self._get_team_record_by_id(team_id, season)
            
            return "N/A"
            
        except Exception as e:
            print(f"    Error getting team record: {e}")
            team_id = self._get_team_id(team_abbr)
            if team_id and team_id != '0':
                return self._get_team_record_by_id(team_id, season)
            return "N/A"
    
    def _get_team_record_by_id(self, team_id, season):
        """Backup method to get team record using team ID"""
        url = f"{self.base_url}/teaminfocommon"
        params = {
            'TeamID': team_id,
            'Season': season,
            'SeasonType': 'Regular Season'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            rows = data['resultSets'][0]['rowSet']
            headers = data['resultSets'][0]['headers']
            
            if rows:
                row_dict = dict(zip(headers, rows[0]))
                wins = row_dict.get('W', 0)
                losses = row_dict.get('L', 0)
                return f"{wins}-{losses}"
            
            return "N/A"
            
        except Exception as e:
            return "N/A"
    
    def _get_team_id(self, team_abbr):
        team_map = {
            'LAL': '1610612747', 'BOS': '1610612738', 'CHI': '1610612741',
            'MIA': '1610612748', 'GSW': '1610612744', 'SAS': '1610612759',
            'HOU': '1610612745', 'PHI': '1610612755', 'DEN': '1610612743',
            'MIL': '1610612749', 'PHX': '1610612756', 'OKC': '1610612760',
            'DAL': '1610612742', 'CLE': '1610612739', 'TOR': '1610612761',
            'MEM': '1610612763', 'POR': '1610612757', 'UTA': '1610612762',
            'ORL': '1610612753', 'MIN': '1610612750', 'NOP': '1610612740',
            'SAC': '1610612758', 'BKN': '1610612751', 'DET': '1610612765',
            'ATL': '1610612737', 'WAS': '1610612764', 'IND': '1610612754',
            'CHO': '1610612766', 'NYK': '1610612752', 'LAC': '1610612746'
        }
        return team_map.get(team_abbr, '0')
    
    def check_past_mvp_winner(self, player_name, season, mvp_data):
        season_year = int(season.split('-')[0])
        
        previous_seasons = mvp_data[mvp_data['Year'] < season_year]
        
        for _, row in previous_seasons.iterrows():
            season_data = mvp_data[mvp_data['Year'] == row['Year']]
            max_points = season_data['Points'].max()
            
            if row['Points'] == max_points and row['Player'] == player_name:
                return True
        
        return False
    
    def scrape_all_stats(self, input_csv='mvp_voting_results.csv', output_csv='mvp_complete_stats.csv'):
        print("Running Stat Collector")
        
        # Read existing data from csv
        mvp_data = pd.read_csv(input_csv)
        print(f"\nLoaded {len(mvp_data)} players from {input_csv}")
        
        try:
            existing_data = pd.read_csv(output_csv)
            completed = set(zip(existing_data['Player'], existing_data['Season']))
            print(f"Found existing data with {len(completed)} completed entries")
        except FileNotFoundError:
            completed = set()
            existing_data = None
        
        results = []
        
        for idx, row in mvp_data.iterrows():
            player_name = row['Player']
            season = row['Season']
            mvp_points = row['Points']
            
            if (player_name, season) in completed:
                print(f"\n[{idx+1}/{len(mvp_data)}] Skipping {player_name} ({season}) - already completed")
                continue
            
            print(f"\n[{idx+1}/{len(mvp_data)}] Processing {player_name} ({season})")
            
            player_id = self.get_player_id(player_name, season)
            if not player_id:
                print(f"Skipping - couldn't find player ID")
                time.sleep(1)
                continue
            
            print(f"Found player ID: {player_id}")
            
            stats = self.get_player_season_stats(player_id, season)
            
            if not stats:
                print(f"No stats found for this season")
                time.sleep(1)
                continue
            
            past_winner = self.check_past_mvp_winner(player_name, season, mvp_data)
            
            # Get team record from game log data
            team_record = "N/A"
            if 'TEAM_WINS' in stats and 'TEAM_LOSSES' in stats:
                team_record = f"{stats['TEAM_WINS']}-{stats['TEAM_LOSSES']}"
            
            result = {
                'Player': player_name,
                'Season': season,
                'MVP_Points': mvp_points,
                'GP': stats.get('GP', None),
                'MPG': stats.get('MPG', None),
                'PTS': stats.get('PTS', None),
                'REB': stats.get('REB', None),
                'AST': stats.get('AST', None),
                'STL': stats.get('STL', None),
                'BLK': stats.get('BLK', None),
                'FG_PCT': stats.get('FG_PCT', None),
                'FG3_PCT': stats.get('FG3_PCT', None),
                'FT_PCT': stats.get('FT_PCT', None),
                'USG_PCT': stats.get('USG_PCT', None),
                'OFF_RATING': stats.get('OFF_RATING', None),
                'DEF_RATING': stats.get('DEF_RATING', None),
                'NET_RATING': stats.get('NET_RATING', None),
                'PIE': stats.get('PIE', None),
                'TEAM': stats.get('TEAM', 'N/A'),
                'TEAM_RECORD': team_record,
                'PAST_MVP_WINNER': past_winner
            }
            
            results.append(result)
            
            print(f"Stats collected: {stats.get('PTS', 0)} PTS, {stats.get('REB', 0)} REB, {stats.get('AST', 0)} AST")
            
            if len(results) % 10 == 0:
                temp_df = pd.DataFrame(results)
                if existing_data is not None:
                    temp_df = pd.concat([existing_data, temp_df], ignore_index=True)
                temp_df.to_csv(output_csv, index=False)
                print(f"\nProgress saved ({len(results)} new entries)")
                existing_data = temp_df
                results = []
            
            time.sleep(random.uniform(0.6, 1.2))
        
        if results:
            final_df = pd.DataFrame(results)
            if existing_data is not None:
                final_df = pd.concat([existing_data, final_df], ignore_index=True)
            final_df.to_csv(output_csv, index=False)
        
        print(f"Complete; Data saved to {output_csv}")
        
        
        final_data = pd.read_csv(output_csv)
        print(f"\nFinal dataset: {len(final_data)} players with complete stats")
        print(f"Seasons covered: {final_data['Season'].nunique()}")
        print(f"Date range: {final_data['Season'].min()} to {final_data['Season'].max()}")


if __name__ == "__main__":
    collector = NBAStatsCollector()
    collector.scrape_all_stats()
