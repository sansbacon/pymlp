import re

from bs4 import BeautifulSoup
import requests


def get_players(el, fields=None):
    """Get the player attributes on the page"""
    fields = fields if fields else ['alt']
    base_player_url = 'https://www.majorleaguepickleball.net/player/{slug}/'
    players = []

    for img in el.find_all('img'):
        if 'Player' in img.attrs.get('alt',):
            player = {k: img.attrs[k] for k in fields}
            slug = '-'.join([s.lower() for s in player['alt'].split()[1:]])
            player['player_url'] = base_player_url.format(slug=slug)
            player['player_name'] = ' '.join(player['alt'].split()[1:])
            players.append({k: v for k, v in player.items() if k not in fields})        
    return players


def get_teams(soup):
    """Parses page into dict of team name: team URL
       Team name is in all caps. Is challenger and premier"""
    urls = {}
    for a in soup.find_all('a', class_=None):
        if re.search(r'net/team/', a.get('href', '')):
            urls[a.text] = a['href']
    return urls


def get_team_divs(soup):
    """Parses page into divs for teams. Is only for the selected league"""
    css_class = 'league__team'
    return [div for div in soup.find_all('div', class_=css_class)]


def parse_team_div(div, teamsd):
    """Parses team div into dict"""
    team = {'players': get_players(div)}
    
    # get team metadata
    ## team name
    team['team_name'] = div.find('a').text
    
    ## page and logo link
    team['team_url'] = teamsd.get(team['team_name'])
    logo_class = 'league__team-card__logo'
    for img in div.find_all('img', class_=logo_class):
        if team['team_name'] in img.attrs.get('alt', ''):
            team['logo_url'] = img.attrs['data-src']

    ## DUPR
    dupr_class = 'league__team-card__dupr'
    for child in div.findChildren(recursive=True):
        if dupr_class in child.attrs.get('class', ''):
            team['team_dupr'] = float(child.text)

    return team    


def run():
    BASE_URL = 'https://www.majorleaguepickleball.net/{league}-league/'
    r = requests.get(BASE_URL.format(league='challenger'))
    html = r.text.replace("""Player Carson "CJ" Klinger""", 'Player CJ Klinger')
    soup = BeautifulSoup(html, parser='lxml')
    teams = [parse_team_div(team, get_teams(soup)) for team in get_team_divs(soup)]
    print(teams)
    


if __name__ == '__main__':
    run()
    
