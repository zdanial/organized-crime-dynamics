import numpy as np

class Gangster(object):
  def __init__(self,id,level,territory,boss, gang) -> None:
    self.id = id
    self.level = level
    self.territory = territory 
    self.boss = boss
    self.soldiers = [] 
    self.a = gang.a 
    self.R = gang.base_R * np.power(gang.R_rate,self.level)
    self.wealth = 0
    self.tribute_income = 0
    self.territory_income = self.gain_at_node(1)
    self.gang = gang

  @property
  def income_rate(self):
    tot_income = self.tribute_income+self.territory_income
    return tot_income if self.level == 0 else tot_income*(1-self.a)

  @property
  def tribute_rate(self):
    return self.a * self.income_rate

  def __repr__(self):
    return f"Gangster {self.id}: L{self.level} T{self.territory:.2f} N{len(self.soldiers)} G{self.income_rate:.2f}"

  def fight_or_flight(self, prob_success):
    return True 
    # return prob_success*self.income_rate > MCDONALDS_INCOME + (1-prob_success)*self.wealth
  #   new_g = self.gain_at_node(len(self.soldiers), delta_T = 0)
  #   return self.wealth + new_g > ((1-prob_success)*NORMAL_LIFE - (1-2*prob_success)*self.wealth)/prob_success
     
     
  # def gain_at_boss(self,N):
  #   a,T,R = self.a,self.territory,self.R
  #   c = np.log(T)/R
  #   return np.log(T/N) + a*(N-1)*np.log(T/N) - (N-1)*c

  def add_territory(self,new_territory):
    self.territory += new_territory


  def gain_at_node(self, N, delta_T = 0):
    a,T,R = self.a, self.territory+delta_T, self.R
    c = np.log(T)/R
    return (np.log(T/N) + a*(N-1)*np.log(T/N) - (N-1)*c ) # we need to add salary from boss = + np.log(self.gang.members[self.boss].territory*(len(self.gang.members[self.boss].soldiers)+1))/self.gang.members[self.boss].R 

  def split(self):
    for n in range(2,50):
      temp_rate = self.gain_at_node(n)
      # print (n,self.territory_income,temp_rate)
      if temp_rate <= self.territory_income:
        break 
      self.territory_income = temp_rate

    self.territory =  self.territory / (n-1)
    # new_income = self.territory_income
    self.territory_income = self.gain_at_node(1)
    # self.tribute_income += new_income-self.territory_income
    return n-2




  
      