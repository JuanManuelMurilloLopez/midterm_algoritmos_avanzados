from domain.models.TeamGraph import TeamGraph
from algorithms.rhythm import rhythm_weight
from domain.services.form import recent_form
from domain.models.Team import Team


def build_team_graph(matches, teams, window=15):
    graph = TeamGraph()

    team_objects = {}

    for team_name in teams:
        form = recent_form(matches, team_name, n=window)
        team_objects[team_name] = Team(team_name, form)

    for match in matches:
        home = match["home"]
        away = match["away"]

        r_home = team_objects[home].rhythm
        r_away = team_objects[away].rhythm

        graph.add_edge(
            home,
            away,
            rhythm_weight(r_away),
            meta={"rhythm": r_away}
        )

        graph.add_edge(
            away,
            home,
            rhythm_weight(r_home),
            meta={"rhythm": r_home}
        )

    return graph



def build_prestige_graph(matches):

    graph = TeamGraph()
    
    for match in matches:
        home = match["home"]
        away = match["away"]
        
        hg, ag = match["ft"] 
        
        if hg > ag:
            graph.add_edge(from_team=away, to_team=home, weight=1.0, meta={"result": "L"})
        elif ag > hg:
            graph.add_edge(from_team=home, to_team=away, weight=1.0, meta={"result": "L"})
        else:
            graph.add_edge(from_team=home, to_team=away, weight=0.5, meta={"result": "D"})
            graph.add_edge(from_team=away, to_team=home, weight=0.5, meta={"result": "D"})
            
    return graph