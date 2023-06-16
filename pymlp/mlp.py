import re

from bs4 import BeautifulSoup
import requests


def get_players(soup):
    """Get the player attributes on the page"""
    return [img.attrs for 
            img in soup.find_all('img')
            if 'Player' in img.attrs.get('alt', '')]     


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
    team = {}
    
    # get DUPR
    dupr_class = 'league__team-card__dupr'
    for child in div.findChildren(recursive=True):
        if dupr_class in child.attrs.get('class', ''):
            team['team_dupr'] = float(child.text)

    return team
    

def run():
    BASE_URL = 'https://www.majorleaguepickleball.net/{league}-league/'
    r = requests.get(BASE_URL.format(league='challenger'))
    html = r.text.replace("""Player Carson "CJ" Klinger""", 'Player CJ Klinger')
    soup = BeautifulSoup(html)
    teams = [parse_team_div(team) for team in get_team_divs(soup)]
    


if __name__ == '__main__':
    run()
    
