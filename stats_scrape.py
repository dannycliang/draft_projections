from bs4 import BeautifulSoup
from requests import get
import csv


def add_basic_stats(stats, tds):
    for td in tds:
        td = str(td)
        starting_index = td.find(">") + 1
        ending_index = td.find("</td")
        if "pts_per_g" in td:
            stats["pts_per_g"].append(td[starting_index:ending_index])
        elif "trb_per_g" in td:
            stats["trb_per_g"].append(td[starting_index:ending_index])
        elif "ast_per_g" in td:
            stats["ast_per_g"].append(td[starting_index:ending_index])
        elif "stl_per_g" in td:
            stats["stl_per_g"].append(td[starting_index:ending_index])
        elif "blk_per_g" in td:
            stats["blk_per_g"].append(td[starting_index:ending_index])
        elif "tov_per_g" in td:
            stats["tov_per_g"].append(td[starting_index:ending_index])
        elif "fg3_pct" in td:
            stats["fg3_pct"].append(td[starting_index:ending_index])
        elif "ft_pct" in td:
            stats["ft_pct"].append(td[starting_index:ending_index])
        elif "mp" in td:
            stats["mp_per_g"].append(td[starting_index:ending_index])
        elif "pf" in td:
            stats["pf_per_g"].append(td[starting_index:ending_index])

def add_advanced_stats(advanced, resp):
    for advance in advanced:
        tag = 'data-stat=\"' + advance + '\" >'
        body_text = resp
        versions = [body_text]
        while tag in body_text:
            versions.append(body_text)
            current_marker = body_text.index(tag)
            body_text = body_text[current_marker + len(tag):]
        body_text = versions[max(len(versions) - 2, 0)]
        if tag in body_text:
            current_marker = body_text.index(tag)
            body_text = body_text[current_marker:]
            advanced[advance].append(body_text[len(tag):body_text.index("</td")])



def college_stat_scrape(name):
    """,
                     "rapm": [],
                     "bpm": [],
                     "winshare": [],
                     "vorp": []"""
    college_url_template = "https://www.sports-reference.com/cbb/players/"
    url = college_url_template + name[1].lower() + "-" + name[0].lower() + "-1.html"
    response = get(url).text
    stats = {"pts_per_g": [],
             "trb_per_g": [],
             "ast_per_g": [],
             "stl_per_g": [],
             "blk_per_g": [],
             "tov_per_g": [],
             "fg3_pct": [],
             "ft_pct": [],
             "mp_per_g": [],
             "pf_per_g": [],
             "ts_pct": [],
             "usg_pct": [],
             "ows": [],
             "dws": []}
    if "Page Not Found" not in response:
        html = BeautifulSoup(response, 'html.parser')
        tds = html.find_all('td', attrs={'data-stat': True})
        add_basic_stats(stats, tds)
        add_advanced_stats(stats, response)
        for stat in stats:
            if len(stats[stat]) > 0:
                stats[stat] = stats[stat][max(len(stats[stat]) - 1, 0)]
    return stats

def advanced_stats_scrape(players):
    def add_rpm(rows, players, year):
        indices = {"/year/2014": 2014, "/year/2015": 2015, "/year/2016": 2016, "/year/2017": 2017, "": 2018}
        for row in rows:
            player_name = row.a.text
            if player_name in players:
                stats = players[player_name]
                stats["rpm"][indices[year] - stats["draft_year"]] = row.find('td', class_="sortcell").text
    years = {"/year/2014": 11, "/year/2015": 12, "/year/2016": 11, "/year/2017": 12, "": 14}
    for year in years:
        for page in range(1, years[year] + 1):
            url_template = "http://www.espn.com/nba/statistics/rpm/_" + year + "/page/" + str(page) + "/sort/RPM"
            response = get(url_template).text
            html = BeautifulSoup(response, 'html.parser')
            oddrows = html.find_all('tr', class_= 'oddrow')
            evenrows = html.find_all('tr', class_= 'evenrow')
            add_rpm(oddrows, players, year)
            add_rpm(evenrows, players, year)


def scrape_stats(starting_year, ending_year):
    url_template = "https://www.basketball-reference.com/draft/NBA_"
    players = {}
    for value in range(starting_year, ending_year + 1):
        print(str(value) + " NBA DRAFT")
        url = url_template + str(value) + ".html"
        response = get(url).text
        html = BeautifulSoup(response, 'html.parser')
        characteristics = html.find_all('td', attrs={'data-stat' : True})
        for characteristic in characteristics:
            characteristic = str(characteristic)
            starting_index = characteristic.find("k=")
            if "data-append" in characteristic:
                ending_index = characteristic.find("data-append")
            else:
                ending_index = characteristic.find("data-stat=")
            if "player" in characteristic:
                name = characteristic[starting_index + 3:ending_index - 2].split(",")
                players[name[1] + " " + name[0]] = college_stat_scrape(name)
                players[name[1] + " " + name[0]]["rpm"] = ["N/A" for _ in range(2018 - value)]
                players[name[1] + " " + name[0]]["draft_year"] = value
    advanced_stats_scrape(players)
    with open('stats.csv', mode='w') as stats_file:
        stats_writer = csv.writer(stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for player in players:
            stats_writer.writerow([player] + list(players[player].values()))

scrape_stats(2003, 2013)

