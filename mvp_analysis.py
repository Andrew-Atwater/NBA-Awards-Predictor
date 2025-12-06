import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

class MVPAnalyzer:
    def __init__(self, data_file='mvp_complete_stats.csv'):
        self.df = pd.read_csv(data_file)
        print(f"Loaded {len(self.df)} MVP candidates from {data_file}")
        print(f"Seasons: {self.df['Season'].min()} to {self.df['Season'].max()}\n")
        
        self.plot_dir = 'mvp_analysis_plots'
        if not os.path.exists(self.plot_dir):
            os.makedirs(self.plot_dir)
            print(f"Created directory: {self.plot_dir}\n")
        
        # Create MVP winner flag for player who recieved the most votes
        self.df['MVP_WINNER'] = False
        for season in self.df['Season'].unique():
            season_data = self.df[self.df['Season'] == season]
            max_points = season_data['MVP_Points'].max()
            winner_mask = (self.df['Season'] == season) & (self.df['MVP_Points'] == max_points)
            self.df.loc[winner_mask, 'MVP_WINNER'] = True
        
        # Flag for top 3
        self.df['TOP_3'] = False
        for season in self.df['Season'].unique():
            season_data = self.df[self.df['Season'] == season].nlargest(3, 'MVP_Points')
            top3_mask = self.df.index.isin(season_data.index)
            self.df.loc[top3_mask, 'TOP_3'] = True
    
    def mvp_winner_thresholds(self):
        print("MVP WINNER STATISTICAL THRESHOLDS")
        
        winners = self.df[self.df['MVP_WINNER'] == True]
        
        print(f"\nTotal MVP Winners Analyzed: {len(winners)}")
        print(f"Seasons: {winners['Season'].min()} to {winners['Season'].max()}\n")
        
        # Key stats to analyze
        stat_columns = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT',
                       'TEAM_WIN_PCT', 'GAME_SCORE', 'SIMPLE_PER', 'IMPACT_SCORE']
        
        thresholds = {}
        
        print("MINIMUM THRESHOLDS FOR MVP WINNERS:")
        for stat in stat_columns:
            if stat in winners.columns:
                min_val = winners[stat].min()
                max_val = winners[stat].max()
                mean_val = winners[stat].mean()
                median_val = winners[stat].median()
                
                thresholds[stat] = {
                    'min': min_val,
                    'max': max_val,
                    'mean': mean_val,
                    'median': median_val
                }
                
                print(f"{stat:15} | Min: {min_val:6.1f} | Median: {median_val:6.1f} | Mean: {mean_val:6.1f} | Max: {max_val:6.1f}")
        
        print("\n")
        print("RECOMMENDED 2025-26 MVP THRESHOLDS (Based on Median):")
        print("\nA player should meet MOST of these criteria to be a serious MVP candidate:\n")
        
        recommendations = {
            'PTS': thresholds['PTS']['median'],
            'REB': thresholds['REB']['median'],
            'AST': thresholds['AST']['median'],
            'TEAM_WIN_PCT': thresholds['TEAM_WIN_PCT']['median'],
            'GAME_SCORE': thresholds['GAME_SCORE']['median'],
            'SIMPLE_PER': thresholds['SIMPLE_PER']['median']
        }
        
        for stat, threshold in recommendations.items():
            print(f"  • {stat}: ≥ {threshold:.1f}")
        
        print(f"\n  • Team Record: Top 3 seed in conference (Win% ≥ {thresholds['TEAM_WIN_PCT']['median']:.1f}%)")
        print("  • Narrative: Best player on winning team OR historic individual season")
        
        return thresholds
    
    def top3_analysis(self):
        print("\n\n")
        print("TOP 3 MVP FINISHERS VS REST OF FIELD")
        
        top3 = self.df[self.df['TOP_3'] == True]
        rest = self.df[self.df['TOP_3'] == False]
        
        print(f"\nTop 3 Finishers: {len(top3)} players")
        print(f"Rest of Field: {len(rest)} players\n")
        
        stat_columns = ['PTS', 'REB', 'AST', 'TEAM_WIN_PCT', 'GAME_SCORE', 'SIMPLE_PER']
        
        print(f"{'Stat':<15} | {'Top 3 Avg':<12} | {'Rest Avg':<12} | {'Difference':<12}")
        print("-" * 70)
        
        for stat in stat_columns:
            if stat in self.df.columns:
                top3_avg = top3[stat].mean()
                rest_avg = rest[stat].mean()
                diff = top3_avg - rest_avg
                print(f"{stat:<15} | {top3_avg:>11.1f} | {rest_avg:>11.1f} | {diff:>+11.1f}")
        
        return {'top3': top3, 'rest': rest}
    
    def team_record_importance(self):
        print("\n\n")
        print("TEAM SUCCESS AND MVP VOTING")
        
        winners = self.df[self.df['MVP_WINNER'] == True]
        
        print(f"\nMVP Winners by Team Win Percentage:")
        
        # Categorize by win percentage
        elite_teams = winners[winners['TEAM_WIN_PCT'] >= 70]
        good_teams = winners[(winners['TEAM_WIN_PCT'] >= 60) & (winners['TEAM_WIN_PCT'] < 70)]
        average_teams = winners[winners['TEAM_WIN_PCT'] < 60]
        
        print(f"  Elite Teams (70%+ wins):    {len(elite_teams)} MVPs ({len(elite_teams)/len(winners)*100:.1f}%)")
        print(f"  Good Teams (60-69% wins):   {len(good_teams)} MVPs ({len(good_teams)/len(winners)*100:.1f}%)")
        print(f"  Average Teams (<60% wins):  {len(average_teams)} MVPs ({len(average_teams)/len(winners)*100:.1f}%)")
        
        print(f"\n  Average Team Win% for MVP Winners: {winners['TEAM_WIN_PCT'].mean():.1f}%")
        print(f"  Minimum Team Win% for MVP Winner:  {winners['TEAM_WIN_PCT'].min():.1f}%")
        
        # Correlation analysis
        corr = self.df['MVP_Points'].corr(self.df['TEAM_WIN_PCT'])
        print(f"\n  Correlation between MVP Points and Team Win%: {corr:.3f}")
        print("  (1.0 = perfect correlation, 0.0 = no correlation)")
        
        # Create scatter plot
        plt.figure(figsize=(12, 8))
        
        # Plot winners vs non-winners
        non_winners = self.df[self.df['MVP_WINNER'] == False]
        plt.scatter(non_winners['TEAM_WIN_PCT'], non_winners['MVP_Points'], 
                   alpha=0.5, s=50, c='lightblue', label='MVP Candidates', edgecolors='black')
        plt.scatter(winners['TEAM_WIN_PCT'], winners['MVP_Points'], 
                   alpha=0.9, s=200, c='gold', label='MVP Winners', edgecolors='black', linewidths=2)
        
        plt.xlabel('Team Win Percentage', fontsize=14, fontweight='bold')
        plt.ylabel('MVP Voting Points', fontsize=14, fontweight='bold')
        plt.title('Team Success vs MVP Voting Points (2000-2025)', fontsize=16, fontweight='bold')
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add correlation text
        plt.text(0.02, 0.98, f'Correlation: {corr:.3f}', 
                transform=plt.gca().transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f'{self.plot_dir}/01_team_success_vs_mvp_votes.png', dpi=300, bbox_inches='tight')
        print(f"\nSaved: {self.plot_dir}/01_team_success_vs_mvp_votes.png")
        plt.close()
    
    def historical_trends(self):
        print("\n\n" + "=" * 70)
        print("HISTORICAL TRENDS IN MVP VOTING")
        print("=" * 70)
        
        winners = self.df[self.df['MVP_WINNER'] == True].copy()
        winners['Year'] = winners['Season'].str[:4].astype(int)
        
        # Split into eras
        early = winners[winners['Year'] < 2010]
        recent = winners[winners['Year'] >= 2010]
        
        print(f"\nEarly Era (2000-2009): {len(early)} MVPs")
        print(f"Modern Era (2010-2024): {len(recent)} MVPs")
        
        print(f"\n{'Stat':<15} | {'2000-2009 Avg':<15} | {'2010-2024 Avg':<15} | {'Change':<10}")
        print("-" * 70)
        
        stat_columns = ['PTS', 'REB', 'AST', 'FG3_PCT', 'TEAM_WIN_PCT', 'GAME_SCORE']
        
        for stat in stat_columns:
            if stat in winners.columns:
                early_avg = early[stat].mean()
                recent_avg = recent[stat].mean()
                change = recent_avg - early_avg
                print(f"{stat:<15} | {early_avg:>14.1f} | {recent_avg:>14.1f} | {change:>+9.1f}")
        
        print("\nKey Observations:")
        if recent['FG3_PCT'].mean() > early['FG3_PCT'].mean():
            print("  • 3-point shooting has become more important for MVP candidates")
        if recent['AST'].mean() > early['AST'].mean():
            print("  • Playmaking (assists) valued more in modern era")
        if recent['TEAM_WIN_PCT'].mean() > early['TEAM_WIN_PCT'].mean():
            print("  • Team success even more critical in recent years")
        
        # Create trend comparison plot
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        
        stats_to_plot = [
            ('PTS', 'Points Per Game'),
            ('AST', 'Assists Per Game'),
            ('REB', 'Rebounds Per Game'),
            ('FG3_PCT', '3-Point %'),
            ('TEAM_WIN_PCT', 'Team Win %'),
            ('GAME_SCORE', 'Game Score')
        ]
        
        for idx, (stat, title) in enumerate(stats_to_plot):
            row = idx // 3
            col = idx % 3
            ax = axes[row, col]
            
            data_to_plot = [early[stat].mean(), recent[stat].mean()]
            colors = ['#3498db', '#e74c3c']
            bars = ax.bar(['2000-2009', '2010-2024'], data_to_plot, 
                         color=colors, edgecolor='black', linewidth=2)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Historical Trends in MVP Winners: Early vs Modern Era', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.plot_dir}/02_historical_trends.png', dpi=300, bbox_inches='tight')
        print(f"\nSaved: {self.plot_dir}/02_historical_trends.png")
        plt.close()
    
    def past_winner_advantage(self):
        print("PAST MVP WINNER ADVANTAGE")
        
        past_winners = self.df[self.df['PAST_MVP_WINNER'] == True]
        first_timers = self.df[self.df['PAST_MVP_WINNER'] == False]
        
        past_mvp_rate = past_winners['MVP_WINNER'].mean()
        first_timer_rate = first_timers['MVP_WINNER'].mean()
        
        print(f"\nCandidates who were past MVP winners: {len(past_winners)}")
        print(f"Candidates who were first-time finalists: {len(first_timers)}")
        
        print(f"\nMVP Win Rate:")
        print(f"  • Past winners: {past_mvp_rate*100:.1f}% won MVP again")
        print(f"  • First-timers: {first_timer_rate*100:.1f}% won MVP")
        
        if past_mvp_rate > first_timer_rate:
            print(f"\n  → Past winners are {past_mvp_rate/first_timer_rate:.1f}x more likely to win MVP")
        
        # Multiple time winners
        multiple_winners = self.df[self.df['MVP_WINNER'] == True].groupby('Player').size()
        multiple_winners = multiple_winners[multiple_winners > 1].sort_values(ascending=False)
        
        if len(multiple_winners) > 0:
            print(f"\nMultiple-Time MVP Winners:")
            for player, count in multiple_winners.items():
                print(f"  • {player}: {count} MVPs")
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Win rate comparison
        win_rates = [past_mvp_rate * 100, first_timer_rate * 100]
        categories = ['Past MVP\nWinners', 'First-Time\nFinalists']
        colors = ['#f39c12', '#95a5a6']
        
        bars = axes[0].bar(categories, win_rates, color=colors, edgecolor='black', linewidth=2)
        axes[0].set_ylabel('MVP Win Rate (%)', fontsize=12, fontweight='bold')
        axes[0].set_title('MVP Win Rate by Previous Winner Status', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')
        
        # Add percentage labels
        for bar in bars:
            height = bar.get_height()
            axes[0].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Multiple winners bar chart
        if len(multiple_winners) > 0:
            top_multi = multiple_winners.head(10)
            axes[1].barh(range(len(top_multi)), top_multi.values, color='#2ecc71', edgecolor='black', linewidth=2)
            axes[1].set_yticks(range(len(top_multi)))
            axes[1].set_yticklabels(top_multi.index, fontsize=10)
            axes[1].set_xlabel('Number of MVP Awards', fontsize=12, fontweight='bold')
            axes[1].set_title('Multiple-Time MVP Winners', fontsize=14, fontweight='bold')
            axes[1].grid(True, alpha=0.3, axis='x')
            axes[1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(f'{self.plot_dir}/03_past_winner_advantage.png', dpi=300, bbox_inches='tight')
        print(f"\nSaved: {self.plot_dir}/03_past_winner_advantage.png")
        plt.close()
    
    def generate_summary_report(self):
        print("EXECUTIVE SUMMARY: 2025-26 MVP PREDICTION CRITERIA")
        
        winners = self.df[self.df['MVP_WINNER'] == True]
        
        print("\nBased on 25 years of MVP voting data (2000-2025), a player needs:\n")
        
        print("1. INDIVIDUAL PERFORMANCE:")
        print(f"   • Points per game: ≥ {winners['PTS'].quantile(0.25):.1f} (minimum threshold)")
        print(f"   • Elite scoring: ≥ {winners['PTS'].median():.1f} PPG (median MVP)")
        print(f"   • All-around impact: SIMPLE_PER ≥ {winners['SIMPLE_PER'].median():.1f}")
        print(f"   • Overall game score: ≥ {winners['GAME_SCORE'].median():.1f}")
        
        print("\n2. TEAM SUCCESS (CRITICAL):")
        print(f"   • Minimum team win%: {winners['TEAM_WIN_PCT'].min():.1f}% (historical floor)")
        print(f"   • Competitive threshold: ≥ {winners['TEAM_WIN_PCT'].quantile(0.25):.1f}%")
        print(f"   • Strong candidate: ≥ {winners['TEAM_WIN_PCT'].median():.1f}% (top 3 seed)")
        print(f"   • {len(winners[winners['TEAM_WIN_PCT'] >= 70])} of {len(winners)} MVPs ({len(winners[winners['TEAM_WIN_PCT'] >= 70])/len(winners)*100:.0f}%) had 70%+ team win rate")
        
        print("\n3. ADDITIONAL FACTORS:")
        past_winner_boost = winners['PAST_MVP_WINNER'].mean()
        print(f"   • Past MVP winners: {past_winner_boost*100:.0f}% of winners were previous MVPs")
        print("   • Narrative importance: Best player on best team preferred")
        print("   • Position flexibility: No position bias in voting")
        
        print("\n4. 2025-26 PREDICTION APPROACH:")
        print("   → Identify players averaging:")
        print(f"     - {winners['PTS'].median():.0f}+ PPG")
        print(f"     - {winners['REB'].median():.0f}+ RPG or {winners['AST'].median():.0f}+ APG")
        print(f"     - Team with {winners['TEAM_WIN_PCT'].median():.0f}%+ win rate")
        print("   → Consider narrative and historical precedent")
        print("   → Weight recent performance and team seeding")
        
        # Create threshold visualization
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Box plots for key stats
        stats_to_plot = [
            ('PTS', 'Points Per Game', axes[0, 0]),
            ('TEAM_WIN_PCT', 'Team Win %', axes[0, 1]),
            ('GAME_SCORE', 'Game Score', axes[1, 0]),
            ('SIMPLE_PER', 'Simple PER', axes[1, 1])
        ]
        
        for stat, title, ax in stats_to_plot:
            data = [
                self.df[self.df['MVP_WINNER'] == True][stat].dropna(),
                self.df[self.df['TOP_3'] == True][stat].dropna(),
                self.df[self.df['TOP_3'] == False][stat].dropna()
            ]
            
            bp = ax.boxplot(data, labels=['MVP\nWinners', 'Top 3\nFinishers', 'Other\nCandidates'],
                           patch_artist=True, showmeans=True)
            
            colors = ['#FFD700', '#C0C0C0', '#CD7F32']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')
                patch.set_linewidth(2)
            
            ax.set_ylabel(title, fontsize=11, fontweight='bold')
            ax.set_title(f'{title} Distribution', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('MVP Candidate Statistical Thresholds (2000-2025)', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.plot_dir}/04_mvp_thresholds.png', dpi=300, bbox_inches='tight')
        print(f"\nSaved: {self.plot_dir}/04_mvp_thresholds.png")
        plt.close()
        
    def run_full_analysis(self):
        self.mvp_winner_thresholds()
        self.top3_analysis()
        self.team_record_importance()
        self.historical_trends()
        self.past_winner_advantage()
        self.generate_summary_report()
        
        print("ANALYSIS COMPLETE")
        print("\nUse the thresholds above to identify 2025-26 MVP candidates.")
        print("Look for players who meet the statistical criteria AND play for top teams.")
        print(f"\nAll visualizations saved to: {self.plot_dir}/")
        print("\nGenerated plots:")
        print("  1. Team Success vs MVP Votes (scatter plot)")
        print("  2. Historical Trends: Early vs Modern Era (comparison)")
        print("  3. Past Winner Advantage (win rates & multiple winners)")
        print("  4. MVP Statistical Thresholds (box plots)")
        print("\nFor presentation: Focus on team success correlation and historical trends.\n")


def main():
    analyzer = MVPAnalyzer('mvp_complete_stats.csv')
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
