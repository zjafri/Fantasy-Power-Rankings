#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 09:23:21 2018

@author: Zain
"""

#function to capitalize first letter of first and last name
def format_name(s):
    space = s.find(' ')+1
    return s[0].capitalize() + s[1:space].lower() + s[space:space+1].capitalize() + s[space+1:len(s)]

#define the Teams
class Teams():
    
    def __init__(self, name, owner, link, team_id,wins,losses,ties,wlp):
        self.name = name
        self.owner = format_name(owner)
        self.link = link
        self.team_id = int(team_id)
        self.wins = int(wins)
        self.losses = int(losses)
        self.ties = int(ties)
        self.wlp = float(wlp)

        
    def __repr__(self):
        return '%s - %s, %s-%s-%s %s team_id:%s' % (self.name, self.owner,self.wins,self.losses,self.ties,self.wlp,self.team_id) 
#        return '%s %d' % (self.name, self.team_id)
    
    def writeRanks(self, pw):
        pw.write("<td align=\"left\"> <a href=\""+self.link+"\">"+ self.name +"</a> </td>"+
				"<td align=\"left\">"+str(self.total_points_rank)+"</td>"+
				"<td align=\"left\">"+str(self.overall_record_rank)+"</td>"+
				"<td align=\"left\">"+str(self.waa_rank)+"</td>"+
				"<td align=\"left\">"+str(self.standings_rank)+"</td>"+
				"<td align=\"left\">"+str(self.power_ranking_points)+"</td>")
    
    def writeOverallRecord(self,pw):
        pw.write("<tr><td>"+self.name+"</td>"+
				"<td>"+str(self.overall_wins)+"-"+str(self.overall_losses)+"-"+str(self.overall_ties)+"</td>"+
				"<td>")
        pw.write('%.3f' % self.overall_wlp)
        pw.write("</td></tr>")
    
    def get_teamID(self):
        return self.team_id
    
    def set_standings_rank(self,var_rank):
        self.standings_rank = int(var_rank)
        
    def set_overall_record_rank(self,var_rank):
        self.overall_record_rank = int(var_rank)
        
    def set_waa_rank(self,var_rank):
        self.waa_rank = int(var_rank)
    
    def set_total_points_rank(self,var_rank):
        self.total_points_rank = int(var_rank)
        
    def set_power_ranking_rank(self,var_rank):
        self.power_ranking_rank = int(var_rank)
        
    def set_power_ranking_points(self,var_rank):
        self.power_ranking_points = int(var_rank)
        
    def set_overall_wins(self,wins):
        self.overall_wins = int(wins)
        
    def set_overall_losses(self,losses):
        self.overall_losses = int(losses)
        
    def set_overall_ties(self,ties):
        self.overall_ties = int(ties)
        
    def set_overall_wlp(self,o_wlp):
        self.overall_wlp = o_wlp