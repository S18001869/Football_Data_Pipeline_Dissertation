
def generate_download_links(start_year=2018, end_year=2020):
    """Given a start year and an end year, generate a list of links for
    premier league data from football-data.co.uk"""

    # "https://www.football-data.co.uk/mmz4281/2021/E0.csv"
    # Create array containing all relevant URLs
    data_links = ["https://www.football-data.co.uk/mmz4281/2021/E0.csv",
                  "https://www.football-data.co.uk/mmz4281/1920/E0.csv",
                  "https://www.football-data.co.uk/mmz4281/1819/E0.csv"]

    output = list()

    num_loops = end_year - start_year
    season_start_year = str(start_year)[-2:]
    season_start_end = str(int(season_start_year)+1)

    # DO STUFF HERE
    for i in data_links:
        # In a loop
        start_year_string = str(season_start_year)
        end_year_string = str(int(season_start_year)+1)
        link = f"https://www.football-data.co.uk/mmz4281/{start_year_string}{end_year_string}/E0.csv"
        output.append(link)
    return output

