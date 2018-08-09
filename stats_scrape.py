from bs4 import BeautifulSoup
from requests import get
import csv


def add_basic_stats(stats, tds):
    """
    :param stats: dictionary of college stats
    :param tds: items with td tag on college page
    :return: None
    Retrieves basic college stats from sports reference page
    """
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
        length = 0
        for stat in stats:
            if len(stats[stat]) > 0:
                if stat == "pts_per_g":
                    length = len(stats[stat]) - 2
                stats[stat] = stats[stat][max(len(stats[stat]) - 1, 0)]
        stats["college_year"] = length
    return stats

def advanced_stats_scrape(players):
    def add_rpm(rows, players, year, rpms):
        indices = {"/year/2014": 2014, "/year/2015": 2015, "/year/2016": 2016, "/year/2017": 2017, "": 2018}
        for row in rows:
            player_name = row.a.text
            if player_name in players:
                stats = players[player_name]
                rpm = row.find('td', class_="sortcell").text
                stats["rpm"][indices[year] - stats["draft_year"] - 1] = rpm
                """rpm = round(float(rpm), 1)
                if rpm in rpms:
                    rpms[rpm].append(str(indices[year]) + " " + player_name)
                else:
                    rpms[rpm] = [str(indices[year]) + " " + player_name]"""
    rpms = {}
    years = {"/year/2014": 11, "/year/2015": 12, "/year/2016": 11, "/year/2017": 12, "": 14}
    for year in years:
        for page in range(1, years[year] + 1):
            url_template = "http://www.espn.com/nba/statistics/rpm/_" + year + "/page/" + str(page) + "/sort/RPM"
            response = get(url_template).text
            html = BeautifulSoup(response, 'html.parser')
            oddrows = html.find_all('tr', class_= 'oddrow')
            evenrows = html.find_all('tr', class_= 'evenrow')
            add_rpm(oddrows, players, year, rpms)
            add_rpm(evenrows, players, year, rpms)
    """with open('comparisons.csv', mode='w') as stats_file:
        comp_writer = csv.writer(stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        rpm_values = list(rpms.keys())
        rpm_values.sort()
        for value in rpm_values:
            to_write = [value, rpms[value]]
            comp_writer.writerow(to_write)"""


def all_stats_scrape(players):
    url_template = "https://www.basketball-reference.com/players/"
    urls = {}
    for char in "abcdefghijklmnopqrstuvwyz":
        url = url_template + char + "/"
        print(url)
        response = get(url).text
        html = BeautifulSoup(response, 'html.parser')
        rows = html.find_all('th', attrs={'data-append-csv': True})
        years = html.find_all('td', attrs={'data-stat': True})
        count = 0
        for row in rows:
            if int(years[count].text) > 1996:
                link = str(row.a)
                urls[link[link.index("players"):link.index("html") + 4]] = row.a.text
            count += 7
    page_scrape(urls, players)


def page_scrape(urls, players):
    advanced_stats = [{}, {}, {}, {}]
    file_names = ["bpm", "ws", "ws48", "vorp"]
    for url in urls:
        stats = {"pts_per_g": [],
                 "trb_per_g": [],
                 "ast_per_g": [],
                 "stl_per_g": [],
                 "blk_per_g": [],
                 "tov_per_g": [],
                 "fg3_pct": [],
                 "ft_pct": [],
                 "fg_pct": [],
                 "ts_pct": [],
                 "bpm": [],
                 "ws": [],
                 "ws/48": [],
                 "vorp": []}
        player_url = "https://www.basketball-reference.com/" + url
        response = get(player_url).text
        html = BeautifulSoup(response, 'html.parser')
        trs = html.find_all('tr', class_="full_table")
        for tr in trs:
            tr = str(tr)
            stats["fg_pct"].append(tr[tr.index("fg_pct") + 8:tr.index("fg3_per_g") - 35])
            stats["fg3_pct"].append(tr[tr.index("fg3_pct") + 9:tr.index("fg2_per_g") - 35])
            stats["ft_pct"].append(tr[tr.index("ft_pct") + 8:tr.index("orb_per_g") - 35])
            stats["pts_per_g"].append(tr[tr.index("pts_per_g") + 11:tr.index("</tr") - 5])
            stats["trb_per_g"].append(tr[tr.index("trb_per_g") + 11:tr.index("ast_per_g") - 35])
            stats["ast_per_g"].append(tr[tr.index("ast_per_g") + 11:tr.index("stl_per_g") - 35])
            stats["stl_per_g"].append(tr[tr.index("stl_per_g") + 11:tr.index("blk_per_g") - 35])
            stats["blk_per_g"].append(tr[tr.index("blk_per_g") + 11:tr.index("tov_per_g") - 35])
            stats["tov_per_g"].append(tr[tr.index("tov_per_g") + 11:tr.index("pf_per_g") - 35])
        add_comparisons(stats, response, urls[url], advanced_stats)
        combined = []
        for stat in stats:
            for item in stats[stat]:
                combined.append(item)
            combined.append("")
        combined = [float(item) if item != "" and "<" not in item else item for item in combined]
        if urls[url] in players:
            players[urls[url]]["all"] = combined
    """
    cleaned_advanced_stats = []
    for advanced_stat in advanced_stats:
        current = {}
        for stat in advanced_stat:
            if type(stat) is str:
                current[float(stat[stat.index(">") + 1:stat.index("</")])] = advanced_stat[stat]
            else:
                current[stat] = advanced_stat[stat]
        cleaned_advanced_stats.append(current)"""
    for count, advanced_stat in enumerate(advanced_stats):
        with open("comparisons/" + file_names[count] + "_comparisons.csv", mode='w') as stats_file:
            comp_writer = csv.writer(stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            values = list(advanced_stat.keys())
            # values.sort()
            for value in values:
                to_write = [value, advanced_stat[value]]
                comp_writer.writerow(to_write)


def add_comparisons(stats, response, name, advanced_stats):
    while len(stats["bpm"]) < len(stats["pts_per_g"]):
        ts = response[response.index(" \" data-stat=\"ts") + 23:response.index(" \" data-stat=\"fg3a_per_fga") - 21]
        ws = response[response.index(" \" data-stat=\"ws\"") + 19:response.index(" \" data-stat=\"ws_per_48") - 21]
        ws_forty = response[response.index(" \" data-stat=\"ws_per_48") + 26:response.index(" \" data-stat=\"bpm-dum") - 21]
        bpm = response[response.index(" \" data-stat=\"bpm\"") + 20:response.index(" \" data-stat=\"vorp") - 21]
        year = response[response.index("advanced.") + 9:response.index("advanced.") + 13]
        stats["ts_pct"].append(ts)
        stats["ws"].append(ws)
        stats["ws/48"].append(ws_forty)
        stats["bpm"].append(bpm)
        position = response.index(" \" data-stat=\"vorp") + 20
        response = response[position:]
        new_position = response.index("</tr>")
        vorp = response[1:new_position - 5]
        stats["vorp"].append(vorp)
        try:
            ws = round(float(ws), 1)
        except:
            print(ws)
            pass
        try:
            bpm = round(float(bpm), 1)
        except:
            print(bpm)
            pass
        try:
            ws_forty = round(float(ws_forty), 2)
        except:
            print(ws_forty)
            pass
        try:
            vorp = round(float(vorp), 1)
        except:
            print(vorp)
            pass
        add_comparison(ws, advanced_stats[0], year, name)
        add_comparison(bpm, advanced_stats[1], year, name)
        add_comparison(ws_forty, advanced_stats[2], year, name)
        add_comparison(vorp, advanced_stats[3], year, name)
        response = response[new_position:]



def add_comparison(stat, comparison, year, name):
    if stat in comparison:
        comparison[stat].append(str(year) + " " + name)
    else:
        comparison[stat] = [str(year) + " " + name]


# page_scrape({"players/s/smartma01.html": "Marcus Smart"}, "")


# all_stats_scrape("")


def scrape_stats(starting_year, ending_year):
    url_template = "https://www.basketball-reference.com/draft/NBA_"
    players = {}
    for value in range(starting_year, ending_year + 1):
        print(str(value) + " NBA DRAFT")
        draft_position = 1
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
                players[name[1] + " " + name[0]]["selection"] = draft_position
                players[name[1] + " " + name[0]]["rpm"] = ["N/A" for _ in range(21)]
                players[name[1] + " " + name[0]]["draft_year"] = value
                draft_position += 1
    advanced_stats_scrape(players)
    all_stats_scrape(players)
    with open('stats.csv', mode='w') as stats_file:
        stats_writer = csv.writer(stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for player in players:
            players[player].pop("draft_year")
            rpm = players[player].pop("rpm")
            combined = []
            if "all" in players[player]:
                combined = list(players[player].pop("all"))
            to_write = [player] + list(players[player].values()) + rpm + combined
            stats_writer.writerow(to_write)



scrape_stats(1996, 2018)
