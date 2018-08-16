#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 19:21:35 2018

@author: Zain
"""

# import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('display.max_columns', 50)

#maual inputs
lg_id = '1422081' #Dynasty
#lg_id = '198641' #Indians

if lg_id == '1422081':
    league = 'Dynasty'
elif lg_id == '198641':
    league = 'Indians'
else:
    leauge = 'Random'

season = '2017'
manual_weeks = 5
bool_manual_weeks = False

#define a llst of teams
from teams import Teams
ffl_teams = []

#standings webpage
standings_page = 'http://games.espn.com/ffl/standings?leagueId=' + lg_id + '&seasonId=' + season
sp_request = requests.get(standings_page)
standings = BeautifulSoup(sp_request.text,'html.parser')

#gets team list 
st_body = standings.find(id='games-tabs1')
team_list = st_body.find_all('a')

#get lists from standings tables
st_body = standings.find_all(class_='tableBody',border='0')

for table in range(int(len(st_body)/2)):
    team_list = st_body[table].find_all('tr')[2:]
    
    for t in team_list:
        name = t.find('a').contents[0]
        link = t.find('a')['href']
        team_id = link[link.find('teamId=')+len('teamId='):link.find('seasonId')-1]
        title = t.find('a')['title']
        owner = title[title.find('(')+1:title.find(')')]
        wins = t.find_all('td')[1].contents[0]
        losses = t.find_all('td')[2].contents[0]
        ties = t.find_all('td')[3].contents[0]
        win_perc = t.find_all('td')[4].contents[0]
        ffl_teams.append(Teams(name,owner,link,team_id,wins,losses,ties,win_perc))
#        print(name)
        
    #end t for
#end table for    

#sort teams by team_id
ffl_teams = sorted(ffl_teams, key=lambda teams: teams.team_id)

t_id = []
t_name = []
t_actual_wlp = []
for t in ffl_teams:
#    print(t)
    t_id.append(t.team_id)
    t_name.append(t.name)
    t_actual_wlp.append(t.wlp)
#end t for  


#scoreboard webpage
scoreboard_page = 'http://games.espn.com/ffl/scoreboard?leagueId=' + lg_id + '&seasonId=' + season + '&matchupPeriodId=1'

# query the website and return the html to the variable ‘page’
page = requests.get(scoreboard_page)

# parse the html using beautiful soup and store in variable `soup`
scoreboard = BeautifulSoup(page.text, 'html.parser')

#determine the number of weeks in the regular season
body = scoreboard.find(class_='bodyCopy')
wk_list = body.find_all('a')
weeks = 0
for w in wk_list:
    weeks = max(weeks,int(w.contents[0]))
#end w for

if(bool_manual_weeks):
    weeks = manual_weeks
#print(weeks)
weeks = int(weeks)

scores = pd.DataFrame(
    {'Name': t_name,
     'team_id': t_id,
     't_actual_wlp':t_actual_wlp
    })
    
#parse each scoreboard page and save scores to array with teams as rows and weeks as columns
for w in range(1,weeks+1):
    #add week to scores dataframe to store socres
    week_name = 'W' + str(w)
    scores[week_name]=""
    
    #webpage url for scoreboard in week 1 through w
    sp = scoreboard_page[0:len(scoreboard_page)-1]+str(w)

    # query the website and return the html to the variable ‘page’
    page = requests.get(sp)

    # parse the html using beautiful soup and store in variable `soup`
    scoreboard = BeautifulSoup(page.text, 'html.parser')
    
    #get scores
    matchups = scoreboard.find_all(class_='ptsBased matchup')
    
    for m in matchups:
        #get data for both teams
        sb_data = m.find_all('td')
        
        #get team 1 id and score
        t1 = sb_data[0].find('a')['href']
        t1_tid = int(t1[t1.find('teamId=')+len('teamId='):t1.find('seasonId')-1])
        t1_score =float(sb_data[1].contents[0])
        if(t1_score==0):
            weeks = w
        
        #get team 2 id and score
        t2 = sb_data[2].find('a')['href']
        t2_tid = int(t2[t2.find('teamId=')+len('teamId='):t2.find('seasonId')-1])
        t2_score = float(sb_data[3].contents[0])
        
        #save weekly scores in weekname column with corresponding row based on team id
        scores.loc[scores.loc[:,"team_id"]==t1_tid,week_name]=t1_score
        scores.loc[scores.loc[:,"team_id"]==t2_tid,week_name]=t2_score
        
        #end m for   
#end w for

#extra code for testing without rerunning the scraping code
scores2 = scores.copy()
scores = scores2.copy()

#create columns to store wins, losses, and ties
scores['wins'] = 0
scores['losses'] = 0
scores['ties'] = 0
scores['wlp']=0.0
scores['total_points'] = 0
scores['waa']=0

#loop through weeks to calculate numbers of wins and ties
for w in range(1,weeks+1):
    week_name = 'W' + str(w)
    wins = "wins"+str(w)
    scores[wins]=scores[week_name].rank(ascending=1)-1 #rank scores ascending which is equal to number of wins
    
    ties = pd.DataFrame(scores[week_name].value_counts())-1 #count the number of ties for a given score
    ties.columns = ['ties_'+week_name]
    ties[week_name] = ties.index
    scores = scores.join(ties.set_index(week_name),on=week_name) #join ties on score for a given week
    scores['wins'] += (scores["wins"+str(w)] - 0.5*scores['ties_'+week_name]) #update running total of wins
    scores['ties'] += scores['ties_'+week_name] #update running total of losses
    scores['total_points']+=scores[week_name]
    
    #creating wins above average metric
    #if you scored in the top half of your league for a given week, you get a win, otherwise a loss
    #if multiple teams tie for the last spot (i.e. 5th in a 10 team league), they split the win.
    waa = pd.DataFrame(scores[wins]//((len(ffl_teams)-1)/2))
    waa['ones'] = 1
    scores['waa'] += (waa.apply(min,axis=1) + scores[wins]//(len(ffl_teams)/2))/2
    
#end w for
scores['losses']=(len(ffl_teams)-1)*weeks-scores['wins']-scores['ties'] #update number of total losses
scores['wlp'] = (scores['wins']+0.5*scores['ties'])/((len(ffl_teams)-1)*weeks)

scores['total_points_rank'] = scores['total_points'].rank(ascending=0,method='min')
scores['overall_record_rank'] = scores['wlp'].rank(ascending=0,method='min')
scores['waa_rank'] = scores['waa'].rank(ascending=0,method='min')
scores['standings_rank'] = scores['t_actual_wlp'].rank(ascending=0,method='min')
scores['power_ranking_points'] = scores['total_points_rank'] + scores['overall_record_rank'] + scores['waa_rank'] + scores['standings_rank']
scores['power_ranking_rank'] = scores['power_ranking_points'].rank(ascending=1,method='min')

#assign new values to each teams variables in Team Class
for t in ffl_teams:
    t.points = scores.loc[scores['team_id']==t.team_id,'W1':week_name]
    t.overall_wlp = scores.loc[scores['team_id']==t.team_id,'wlp']
    t.set_overall_wins(scores.loc[scores['team_id']==t.team_id,'wins'])
    t.set_overall_losses(scores.loc[scores['team_id']==t.team_id,'losses'])
    t.set_overall_ties(scores.loc[scores['team_id']==t.team_id,'ties'])
    t.waa = scores.loc[scores['team_id']==t.team_id,'waa']
    t.total_points = scores.loc[scores['team_id']==t.team_id,'total_points']
    t.set_total_points_rank(scores.loc[scores['team_id']==t.team_id,'total_points_rank'])
    t.set_overall_record_rank(scores.loc[scores['team_id']==t.team_id,'overall_record_rank'])
    t.set_waa_rank(scores.loc[scores['team_id']==t.team_id,'waa_rank'])
    t.set_standings_rank(scores.loc[scores['team_id']==t.team_id,'standings_rank'])
    t.set_power_ranking_points(scores.loc[scores['team_id']==t.team_id,'power_ranking_points'])
    t.set_power_ranking_rank(scores.loc[scores['team_id']==t.team_id,'power_ranking_rank'])    
    t.set_overall_wlp(scores.loc[scores['team_id']==t.team_id,'wlp'])
    
    
#html output
f = open("/Users/Zain/Documents/fantasy/Power Rankings/"+league+" Power Rankings " + season + ".txt", "w")

#html header for the main power rankings table
header = '''<h1 style=\"font-family:font;color:color;font-size:sizepx;background-color:color;text-align:left\">Week '''+ str(weeks) +''' Power Rankings</h1>
	<hr>
    <p>The rankings are based on <a href=\"http://games.espn.go.com/ffl/standings?leagueId=1422081&seasonId='''+season+'''\">standings</a>, <a href=\"#overallrecord\">overall record</a>, <a href=\"http://games.espn.go.com/ffl/standings?leagueId=1422081&seasonId="+year+"\"> points scored</a>, and wins above average (WAA).</p>
    <p>Wins Above Average is how often you score in the top half of the league. </p>
    <table border=\"1\", class=\"sortable\", id=\"myTable\",align=\"right\">
    <col width=\"50\">
    <col width=\"200\">
    <col width=\"50\">
    <col width=\"50\">
    <col width=\"50\">
    <col width=\"50\">
    <tr>
    <th align=\"left\",class=\"rank\">Rank</td>
    <th align=\"left\",class=\"team\">Team</td>
    <th align=\"left\",class=\"ps\">Points</td>
    <th align=\"left\",class=\"or\">Overall</td>
    <th align=\"left\",class=\"war\">WAA </td>
    <th align=\"left\",class=\"standings\">Standings </td>
    <th align=\"left\",class=\"standings\">Total </td>
    </tr>'''

f.write(header)

#sort teams in order of power rankings
ffl_teams = sorted(ffl_teams, key=lambda teams: teams.power_ranking_rank)

#write power rankings
for t in ffl_teams:
    f.write("<tr><td align=\"left\",class=\"rank\">"+str(t.power_ranking_rank)+"</td>")
    t.writeRanks(f)
    f.write("</tr>")
#end t for
f.write("</table>")

#html header for the overall record section
f.write('''<hr><h1 style=\"text-align:left;\"><a id=overallrecord>Overall Record</a></h1>
        <p style=\"text-align:left;\">Overall record is your record if you played every team every week. Below are the standing for overall record through Week '''+ str(weeks) +'''. </p>
        <table border=\"1\">
        <col width=\"200\">
        <col width=\"100\">
        <col width=\"100\">
        <tr>
        <th align=\"left\">Team</th>
        <th align=\"left\">Record</th>
        <th align=\"left\">Winning %</th>
        </tr>''')

#sort teams in order of overall record
ffl_teams = sorted(ffl_teams, key=lambda teams: teams.overall_record_rank)

#write overall record
for t in ffl_teams:
    t.writeOverallRecord(f)
#end t for

f.write("</table>")
f.flush()
f.close()
