import pandas as pd

def clean_nba_data(input_file='tools/nba_player_data.xlsx', output_file='tools/nba_player_data_cleaned.xlsx'):
    # Load the data
    data = pd.read_excel(input_file)
    
    # Drop unnecessary columns
    data.drop(columns=['RANK', 'EFF'], inplace=True)
    
    # Create season start year column
    data['season_start_year'] = data['Year'].str[:4].astype(int)
    
    # Replace season type values
    data['Season_type'].replace('Regular%20Season', 'Regular_season', inplace=True)
    
    # Save the cleaned data
    data.to_excel(output_file, index=False)
    print(f'Cleaned data saved to {output_file}')

if __name__ == "__main__":
    clean_nba_data()
