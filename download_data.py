def generate_download_links(start_year=2018, end_year=2020):
    """Given a start year and an end year, generate a list of links for
    premier league data from football-data.co.uk"""

    # "https://www.football-data.co.uk/mmz4281/2021/E0.csv"

    output = list()

    # Find out how many links to generate
    num_loops = end_year - start_year

    for i in range(num_loops):
        # Generate the year_string variable
        season_start_year = str(start_year + i)[-2:]
        season_start_end = str(int(season_start_year) + 1).zfill(2)
        year_string = season_start_year + season_start_end
        link = f"https://www.football-data.co.uk/mmz4281/{year_string}/E0.csv"
        output.append(link)

    return output


def test_generate_download_links():
    expected_output = [
        'https://www.football-data.co.uk/mmz4281/1819/E0.csv',
        'https://www.football-data.co.uk/mmz4281/1920/E0.csv'
    ]
    assert generate_download_links(2018, 2020) == expected_output, "Test failed"
    print("Test passed")


def test_generate_download_links_one_digit_year():
    expected_output = [
        'https://www.football-data.co.uk/mmz4281/0102/E0.csv',
        'https://www.football-data.co.uk/mmz4281/0203/E0.csv'
    ]
    assert generate_download_links(2001, 2003) == expected_output, "Test failed"
    print("Test passed")


if __name__ == '__main__':
    test_generate_download_links()
    test_generate_download_links_one_digit_year()
    links = generate_download_links(2001, 2020)
    #for link in links:
        # get_football_data(link)


