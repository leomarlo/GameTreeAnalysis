#%%
from game.sotf import Sotf
from rl.MCTS import MCTS

peb = 4; arr = 6; nr_players = 3; field_size = 5;

#%%
game = Sotf(peb=peb,
            arr=arr,
            nr_players=nr_players,
            field_size=field_size,
            action_format='compressed')
#%%
MC = MCTS(game=game,
          exploration_epsilon=0.25,
          biasedness=1,
          optimizing_player=1)
# %%
