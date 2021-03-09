
def generate_download_links(start_year=2018, end_year=2020):
    """Given a start year and an end year, generate a list of links for
    premier league data from football-data.co.uk"""

    # "https://www.football-data.co.uk/mmz4281/2021/E0.csv"

    output = list()

    num_loops = end_year - start_year
    season_start_year = str(start_year)[-2:]
    season_start_end = str(int(season_start_year)+1)
    season_start_year + season_start_end

    # DO STUFF HERE
    for i in range(num_loops):
        # In a loop
        year_string = str(2018)
        link = f"https://www.football-data.co.uk/mmz4281/{year_string}/E0.csv"
        output.append(link)

    return output