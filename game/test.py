#%%
import numpy as np
from random import choice
from sotf import *

peb = 4; arr = 6; nr_players = 3; field_size = 5;

game = Sotf(peb=peb,arr=arr, nr_players=nr_players,field_size=field_size,action_format='compressed')

game_over = False


#%%
## rollout 
nodes = []
edges = []
prevs = game.state_hash
while not game_over:
    opts = game.options()
    chos = choice([o for o in opts])
    acti = opts[chos]
    _, _, game_over, _ = game.step(action=acti)
    node = game.state_hash
    edge = (prevs,node)
    nodes.append(node)
    edges.append(edge)
    prevs = node
    


#%%

# p_acs = [{'pebble': ['A', 1], 'arrow': [[None, None], [None, None]]},
#  {'pebble': ['C', 2], 'arrow': [[None, None], [None, None]]},
#  {'pebble': ['D', 3], 'arrow': [[None, None], [None, None]]},
#  {'pebble': ['A', 4], 'arrow': [[None, None], [None, None]]}]

# a_acs = [{'pebble': [None, None], 'arrow': [['D', 3], ['A', 1]]},
# {'pebble': [None, None], 'arrow': [['A', 1], ['C', 2]]},
# {'pebble': [None, None], 'arrow': [['c', 2], ['D', 3]]}]

# for p in p_acs:
#     game.step(action=p);
# for a in a_acs:
#     game.step(action=a);

# print(game.options())
#%%
