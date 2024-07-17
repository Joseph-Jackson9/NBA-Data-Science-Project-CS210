import pandas as pd
import requests
import time
import numpy as np

# Setting display options for Pandas
pd.set_option('display.max_columns', None)

def scrape_nba_data():
    # Main URL for the page we will be scraping
    player_url = 'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season=2023-24&SeasonType=Regular%20Season&StatCategory=PTS'
    
    # Fetching the initial data to get headers
    r = requests.get(url=player_url).json()
    headers = r['resultSet']['headers']
    
    # Getting the header for the table set up
    df_cols = ['Year', 'Season_type'] + headers
    
    # Initializing the DataFrame
    df = pd.DataFrame(columns=df_cols)
    
    # Defining season types and years
    season_types = ['Regular%20Season', 'Playoffs']
    years = ['2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']
    
    begin_loop = time.time()
    
    # Looping through each year and season type to scrape data
    for y in years:
        for s in season_types:
            api_url = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season={y}&SeasonType={s}&StatCategory=PTS'
            r = requests.get(url=api_url).json()
            temp_df1 = pd.DataFrame(r['resultSet']['rowSet'], columns=headers)
            temp_df2 = pd.DataFrame({'Year': [y for _ in range(len(temp_df1))],
                                     'Season_type': [s for _ in range(len(temp_df1))]})
            temp_df3 = pd.concat([temp_df2, temp_df1], axis=1)
            df = pd.concat([df, temp_df3], axis=0)
            print(f'Finished scraping data for the {y} {s}')
            lag = np.random.uniform(low=4, high=30)
            print(f'... waiting {round(lag, 1)} seconds.')
            time.sleep(lag)
    
    print(f'Process completed. Total runtime: {round((time.time() - begin_loop) / 60, 2)} minutes.')
    
    # Saving the DataFrame to an Excel file
    df.to_excel('tools/nba_player_data.xlsx', index=False)

if __name__ == "__main__":
    scrape_nba_data()
