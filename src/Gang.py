import numpy as np
import networkx as nx
from Gangster import Gangster

def form_squad(gang,leader):
  if leader == None:
    return []
  squad = []
  queue = [sid for sid in gang.members[leader].soldiers]
  while queue:
    mid = queue.pop(0)
    squad.append(mid)
    queue+= gang.members[mid].soldiers
  return squad[::-1] 

class Gang(object):
  def __init__(self,territory,a,base_R,R_rate):
    self.id_counter = 0
    self.members = {}
    self.layers = [[]]
    self.a = a
    self.base_R = base_R
    self.R_rate = R_rate
    self.add_member(0,territory)


  @property
  def tot_wealth(self):
    tot_wealth = 0
    for id, member in self.members.items():
      tot_wealth += member.wealth
    return tot_wealth

  @property
  def tot_territory(self):
    tot_territory = 0
    for id, member in self.members.items():
      tot_territory += member.territory
    return tot_territory


  @property 
  def num_member(self):
    return len(self.members)

  def num_soldiers(self,id):
    member = self.members[id]
    num = 1 
    for sid in member.soldiers:
      num += self.num_soldiers(sid)
    return num

  def add_member(self,level,territory,boss = None):
    id = self.id_counter
    member = Gangster(id,level,territory,boss, self)
    self.members[id] = member 
    if len(self.layers) <= level:
      self.layers.append([])
    # print (level,len(self.layers))
    self.layers[level].append(id)
    self.id_counter+=1 
    return member 

  def remove_member(self,id):
    if id not in self.members:
      return 
    member = self.members[id]
    boss = self.members[member.boss]
    boss.tribute_income -= member.tribute_rate
    for sid in member.soldiers:
      self.remove_member(sid)
    self.members.pop(id)
  
  def grow(self):
    member_list = []
    for id, member in self.members.items():
      member_list.append(member)

    while member_list:
      member = member_list.pop(0)
      num_new_members = member.split()
      # print (num_new_members)
      for _ in range(num_new_members):
        new_member = self.add_member(member.level+1,member.territory, boss = member.id)
        member.soldiers.append(new_member.id)
        member_list.append(new_member)

  def collect_income(self):
    for id, member in self.members.items():
      member.wealth += member.income_rate

  def update_layers(self):
    updated_layers = []
    for layer in self.layers:
      new_layer = []
      for i, id in enumerate(layer):
        if id in self.members:
          new_layer.append(id)
      updated_layers.append(new_layer)
    self.layers = updated_layers

  def remove_dead_soldiers(self):
    for id_, m in self.members.items():
      updated_soldiers = []
      for sid in m.soldiers:
        if sid in self.members:
          updated_soldiers.append(sid)
      m.soldiers = updated_soldiers


  def calculate_tribute(self,boss):
    boss.tribute_income = 0
    for sid in boss.soldiers:
      soldier = self.members[sid]
      boss.tribute_income += self.calculate_tribute(soldier)
    return boss.tribute_rate

  def update(self):
    self.update_layers()
    self.remove_dead_soldiers()
    boss = self.members[0]
    self.calculate_tribute(boss)


  def observe(self,opponent):
    available_members = []
    for ids in opponent.layers[:-1]:
      available_members+=ids
    if not len(available_members):
      return None
    observed_id = np.random.choice(available_members)
    return observed_id
  
  def recruit(self,enemies):
    # num_enemies = len(enemies)
    # mid = random.choice(self.layers[-2])
    # while self.num_soldiers(mid) <= num_enemies:
    #   mid = self.members[mid].boss 
    #   if mid == None:
    #     return None 
    # return mid
    selected_layer = len(self.layers) - 2
    while selected_layer > 0:
      if not len(self.layers[selected_layer]):
        selected_layer -= 1
        continue
      leader = self.layers[selected_layer][ np.argmax([self.num_soldiers(m) for m in self.layers[selected_layer]]) ]
      if not self.num_soldiers(leader) > len(enemies):
        selected_layer -= 1
      else:
        return leader

  def attack(self,leader,squad,enemies,opponent_gang):
    ptr_squad,ptr_enemies = 0, 0 
    survival_rate = (len(squad)-len(enemies))/len(squad)
    while (ptr_squad < len(squad)) and (ptr_enemies < len(enemies)):
      member = self.members[squad[ptr_squad]]
      enemy_id = enemies[ptr_enemies]
      if member.fight_or_flight(survival_rate):
        if np.random.uniform(0, 1) < 0.5:
          opponent_member = opponent_gang.members[enemy_id]
          self.members[leader].add_territory(opponent_member.territory)
          opponent_gang.remove_member(enemy_id)
          ptr_enemies += 1
        else:
          boss = self.members[member.boss]
          boss.add_territory(member.territory)
          self.remove_member(squad[ptr_squad])
          ptr_squad += 1
      else:
        boss = self.members[member.boss]
        boss.add_territory(member.territory)
        self.remove_member(squad[ptr_squad])
        ptr_squad += 1

  def move(self,opponent):
    oppo_leader = self.observe(opponent)
    enemies = form_squad(opponent,oppo_leader)
    leader = self.recruit(enemies)
    squad = form_squad(self,leader)
    # print (oppo_leader,enemies,leader, squad)
    if len(squad) > 0: 
      self.attack(leader, squad, enemies,opponent)
    # return (oppo_leader,enemies,leader, squad)
    

  def draw(self):
    G = nx.Graph()
    for id_, m in self.members.items():
      for sid_ in m.soldiers:
        G.add_edge(id_, sid_)
    pos = nx.spring_layout(G, seed=0)
    nx.draw(G) 
    
  

