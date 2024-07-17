import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def prepare_data(data):
    # Filter out players with fewer than 200 minutes in the regular season
    data = data[~((data['Season_type'] == 'Regular_season') & (data['MIN'] < 200))]
    # Filter out players with fewer than 50 minutes in the playoffs
    data = data[~((data['Season_type'] == 'Playoffs') & (data['MIN'] < 50))]

    # Select relevant columns for prediction
    columns_to_keep = ['Year', 'PLAYER', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'MIN']
    data = data[columns_to_keep]
    
    # Combine regular season and playoff stats for each player by season
    data = data.groupby(['Year', 'PLAYER'], as_index=False).sum()

    # Feature Engineering: Create lag features for past performance
    total_cols = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'MIN']
    for col in total_cols:
        for i in range(1, 2):  # Lag features for the past 1 year
            data[f'{col}_lag_{i}'] = data.groupby('PLAYER')[col].shift(i)
    
    # Fill NaN values created by lag features with zeroes or a default value
    for col in total_cols:
        for i in range(1, 2):
            data[f'{col}_lag_{i}'].fillna(0, inplace=True)  # You can choose a more appropriate default value if needed
    
    return data

def train_model(data):
    # Define the target and features
    target = 'PTS'
    features = [col for col in data.columns if 'lag' in col]
    
    X = data[features]
    y = data[target]
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    return model, mse

def predict_next_season(data, model):
    # Use the most recent season's data to predict the next season
    most_recent_season = data['Year'].max()
    next_season_data = data[data['Year'] == most_recent_season].copy()
    
    # Create lag features for the most recent season
    total_cols = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'MIN']
    for col in total_cols:
        for i in range(1, 2):  # Lag features for the past 1 year
            next_season_data.loc[:, f'{col}_lag_{i}'] = next_season_data.groupby('PLAYER')[col].shift(i)
    
    # Fill NaN values created by lag features with zeroes or a default value
    for col in total_cols:
        for i in range(1, 2):
            next_season_data[f'{col}_lag_{i}'].fillna(0, inplace=True)  # You can choose a more appropriate default value if needed
    
    if len(next_season_data) == 0:
        raise ValueError("No valid rows in the next season's data after creating lag features.")
    
    # Define the features for prediction
    features = [col for col in next_season_data.columns if 'lag' in col]
    
    # Predict the next season's performance
    next_season_data['PTS_predicted'] = model.predict(next_season_data[features])
    
    return next_season_data

def rank_players(predicted_data):
    # Define the composite score as a weighted sum of key metrics
    predicted_data['composite_score'] = (predicted_data['PTS_predicted'] +
                                         predicted_data['REB'] * 0.7 +
                                         predicted_data['AST'] * 0.5 +
                                         predicted_data['STL'] * 0.3 +
                                         predicted_data['BLK'] * 0.3)
    
    # Rank the players based on the composite score
    top_players = predicted_data.sort_values(by='composite_score', ascending=False).head(10)
    
    return top_players

def main(input_file='tools/nba_player_data_cleaned.xlsx'):
    # Explanation of the data and process
    print("This program predicts the top 10 NBA players for the next season based on historical performance data.")
    print("Steps involved:")
    print("1. Filter out players with insufficient playing time.")
    print("2. Combine regular season and playoff stats for each player.")
    print("3. Create lag features for past performance.")
    print("4. Train a regression model to predict next season's performance.")
    print("5. Rank the players based on a composite score of predicted and actual performance metrics.\n")
    
    # Load the cleaned data
    data = pd.read_excel(input_file)
    
    # Prepare the data
    data = prepare_data(data)
    
    # Train the model
    model, mse = train_model(data)
    
    # Predict the next season's performance
    try:
        predicted_data = predict_next_season(data, model)
    
        # Rank the players
        top_players = rank_players(predicted_data)
    
        print("\nTop 10 predicted players for the next season based on composite scores:")
        print(top_players[['PLAYER', 'composite_score']])
    except ValueError as e:
        print(e)
        print("Not enough data to create lag features for prediction.")
    
    # Explanation of the composite score
    print("""
Composite Score Calculation:

The composite score is calculated as a weighted sum of several key performance metrics for each player. These metrics include points scored (PTS), rebounds (REB), assists (AST), steals (STL), and blocks (BLK). The weights for each metric are assigned based on their importance in evaluating a player's overall performance. The formula used for calculating the composite score is as follows:

composite_score = (PTS_predicted) +
                  (REB * 0.7) +
                  (AST * 0.5) +
                  (STL * 0.3) +
                  (BLK * 0.3)

- PTS_predicted: The predicted points scored by the player for the next season, as determined by the regression model.
- REB: The total rebounds by the player.
- AST: The total assists by the player.
- STL: The total steals by the player.
- BLK: The total blocks by the player.

Each of these components contributes to the composite score, with higher weights assigned to metrics that are generally considered more indicative of a player's impact on the game. This composite score is then used to rank the players, identifying the top performers for the upcoming season.
""")
    
if __name__ == "__main__":
    main()
