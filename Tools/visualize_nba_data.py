import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

def visualize_nba_data(input_file='tools/nba_player_data_cleaned.xlsx'):
    # Load the cleaned data
    data = pd.read_excel(input_file)
    
    # Separate data by season type
    rs_df = data[data['Season_type'] == 'Regular_season']
    playoffs_df = data[data['Season_type'] == 'Playoffs']
    total_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 
                  'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']
    
    # Group and calculate per-minute statistics
    data_per_min = data.groupby(['PLAYER', 'PLAYER_ID', 'Year'])[total_cols].sum().reset_index()
    for col in data_per_min.columns[4:]:
        data_per_min[col] = data_per_min[col] / data_per_min['MIN']
    
    # Calculate additional metrics
    data_per_min['FG%'] = data_per_min['FGM'] / data_per_min['FGA']
    data_per_min['3PT%'] = data_per_min['FG3M'] / data_per_min['FG3A']
    data_per_min['FT%'] = data_per_min['FTM'] / data_per_min['FTA']
    data_per_min['FG3A%'] = data_per_min['FG3A'] / data_per_min['FGA']
    data_per_min['PTS/FGA'] = data_per_min['PTS'] / data_per_min['FGA']
    data_per_min['FG3M/FGM'] = data_per_min['FG3M'] / data_per_min['FGM']
    data_per_min['FTA/FGA%'] = data_per_min['FTA'] / data_per_min['FGA']
    data_per_min['TRU%'] = 0.5 * data_per_min['PTS'] / (data_per_min['FGA'] + 0.475 * data_per_min['FTA'])
    data_per_min['AST_TOV'] = data_per_min['AST'] / data_per_min['TOV']
    
    # Filter out players with fewer than 50 minutes
    data_per_min = data_per_min[data_per_min['MIN'] >= 50]
    
    # Drop the PLAYER_ID column
    data_per_min.drop(columns='PLAYER_ID', inplace=True)
    
    # Select only numeric columns for correlation
    numeric_cols = data_per_min.select_dtypes(include=['float64', 'int64'])
    
    # Plot the correlation matrix
    fig = px.imshow(numeric_cols.corr(), text_auto=True)
    fig.update_layout(title='Correlation Matrix of Player Statistics')
    fig.show()
    
    # Plot the histogram of Minutes per Game in Regular Season
    fig = px.histogram(x=rs_df['MIN'], nbins=30)
    fig.update_layout(
        xaxis_title='Minutes Played',
        yaxis_title='Count of Players',
        title='Distribution of Minutes Played in Regular Season'
    )
    fig.show()

    def hist_data(df=rs_df, min_MIN=0, min_GP=0):
        return df.loc[(df['MIN'] >= min_MIN) & (df['GP'] >= min_GP), 'MIN'] / \
               df.loc[(df['MIN'] >= min_MIN) & (df['GP'] >= min_GP), 'GP']
    
    # Create the figure for comparison between Regular Season and Playoffs
    fig = go.Figure()
    
    # Add the Regular Season histogram
    fig.add_trace(go.Histogram(
        x=hist_data(rs_df, 50, 5), 
        histnorm='percent', 
        name='Regular Season',
        xbins={'start': 0, 'end': 46, 'size': 1}
    ))
    
    # Add the Playoffs histogram
    fig.add_trace(go.Histogram(
        x=hist_data(playoffs_df, 5, 1), 
        histnorm='percent', 
        name='Playoffs',
        xbins={'start': 0, 'end': 46, 'size': 1}
    ))
    
    # Update the layout to overlay the histograms and set the opacity
    fig.update_layout(
        barmode='overlay',
        xaxis_title='Minutes per Game',
        yaxis_title='Percentage of Players',
        title='Comparison of Minutes per Game: Regular Season vs Playoffs'
    )
    fig.update_traces(opacity=0.5)
    
    # Show the figure
    fig.show()

    # Scatter Plot of Points vs. Assists
    fig = px.scatter(data, x='PTS', y='AST', color='Season_type', 
                     title='Points vs Assists', labels={'PTS': 'Points', 'AST': 'Assists'})
    fig.show()

    # Box Plot of Points by Season Type
    fig = px.box(data, x='Season_type', y='PTS', title='Distribution of Points by Season Type', 
                 labels={'PTS': 'Points', 'Season_type': 'Season Type'})
    fig.show()

    # Heatmap of Player Performance Metrics
    fig = px.imshow(numeric_cols.corr(), text_auto=True, title='Heatmap of Player Performance Metrics')
    fig.show()

    # Bar Chart of Top 10 Scorers
    top_10_scorers = data.nlargest(10, 'PTS')
    fig = px.bar(top_10_scorers, x='PLAYER', y='PTS', color='PTS', 
                 title='Top 10 Scorers', labels={'PTS': 'Points'})
    fig.show()

    # Line Chart of Points Over Seasons for a specific player
    player_name = 'LeBron James'  # Replace with the player's name of interest
    player_data = data[data['PLAYER'] == player_name]
    fig = px.line(player_data, x='season_start_year', y='PTS', title=f'Points Over Seasons for {player_name}',
                  labels={'season_start_year': 'Season Start Year', 'PTS': 'Points'})
    fig.show()

    # Radar Chart of Player Statistics
    players = ['LeBron James', 'Stephen Curry', 'Kevin Durant']  # Replace with the players of interest
    categories = ['PTS', 'REB', 'AST', 'STL', 'BLK']

    fig = go.Figure()

    for player in players:
        player_stats = data[data['PLAYER'] == player][categories].mean()
        fig.add_trace(go.Scatterpolar(
            r=player_stats,
            theta=categories,
            fill='toself',
            name=player
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        title='Radar Chart of Player Statistics'
    )

    fig.show()

    # Violin Plot of Minutes Played by Season Type
    fig = px.violin(data, x='Season_type', y='MIN', box=True, points='all', 
                    title='Minutes Played by Season Type', labels={'MIN': 'Minutes', 'Season_type': 'Season Type'})
    fig.show()

    # Pie Chart of Shot Distribution
    shot_distribution = data[['FGA', 'FG3A', 'FTA']].sum()
    fig = px.pie(values=shot_distribution, names=shot_distribution.index, 
                 title='Shot Distribution (Field Goals, Three-Pointers, Free Throws)')
    fig.show()

if __name__ == "__main__":
    visualize_nba_data()
