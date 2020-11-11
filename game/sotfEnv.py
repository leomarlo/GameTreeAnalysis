from gym import Env, spaces, error
import numpy as np
import pandas as pd
from copy import deepcopy

# from collections import Counter
# import string




# from gym import spaces
# from gym.spaces import Space
# from gym import logger

class Sotf(Env):

    metadata = {'render.modes': ['human', 'console']}

    def __init__(self,peb,arr,nr_players,field_size):
        self.peb = peb
        self.arr = arr
        self.nr_players = nr_players
        self.current_player = 1
        self.field_size = field_size
        self.peb_total = self.nr_players * self.peb

        alphabet = ' abcdefghijklmnopqrstuvwxyz'
        ALPHABET = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alpha_to_num = {letter: i for i, letter in enumerate(alphabet)}
        alpha_to_num.update({LETTER: i for i, LETTER in enumerate(ALPHABET)})
        self.alpha_to_num=alpha_to_num

        self.either_peb_or_arrow=True
        self.any_or_all_arrows="all"
        self.stage="placing"
        self.win_by = "survivors" # can also be "degree"

        self.scores = [0]*self.nr_players
        self.rewards = [0]*self.nr_players
        self.triggering_player = 0
        self.winner_takes_it_all = True
        # True: 1 point for highest score. zero points for everyone the same score. -1 for someone else has the hightest score
        # False: normalize all score to -1,1 range and assign

        # for rendering
        self.screen = None
        # self.board = None
        # self.last_board = deepcopy(self.board)


        # peb_state assigns a player number to each point on the field matrix
        self.peb_state = np.zeros([self.field_size, self.field_size],dtype=int)
        # arr_state assigns a player number to each link in the adjacency matrix
        self.arr_state = np.zeros([self.peb_total, self.peb_total],dtype=int)
        # toDo: maybe just field_size x self.arr dimensional

        self.state = {'pebbles':self.peb_state, 'arrows':self.arr_state}


        # pebbles
        # holds the in column number
        #    1   -  pebble id
        #    2   -  player id
        #    3:4 -  where (x,y)
        #    5  - degree
        #    6  - placed
        # self.placed_pebbles = []
        self.pebbles_df = pd.DataFrame({'id':list(range(self.peb_total)),
                                        'player': np.repeat(list(range(1,self.nr_players+1)),self.peb),
                                        'x': np.nan * np.ones(self.peb_total),
                                        'y': np.nan * np.ones(self.peb_total),
                                        'deg': np.zeros(self.peb_total),
                                        'placed': np.zeros(self.peb_total)},dtype=int)
        self.arrows_df = pd.DataFrame({'id': list(range(self.nr_players * self.arr)),
                                        'player': np.repeat(list(range(1, self.nr_players + 1)), self.arr),
                                        'source_id': np.nan * np.ones(self.nr_players * self.arr),
                                        'target_id': np.nan * np.ones(self.nr_players * self.arr),
                                        'placed': np.zeros(self.nr_players * self.arr)},dtype=int)
        # self.placed_pebbles= pd.DataFrame(columns = ['id','player','x','y','deg'],dtype=int)

        self.finish_when_any_or_all_arrows_are_gone='any'


    def assign_scores(self):
        if self.win_by=="survivors":
            scores=[sum((self.pebbles_df['player']==player) & (self.pebbles_df['placed']==1)) for player in range(1,self.nr_players+1)]
        elif self.win_by=="degree":
            self.scores=[sum(self.pebbles_df.loc[(self.pebbles_df['player'] == player) & (self.pebbles_df['placed'] == 1),'deg']) for player in
              range(1, self.nr_players + 1)]
        else:
            print("specifiy the winning condition.")
            self.scores=[sum((self.pebbles_df['player'] == player) & (self.pebbles_df['placed'] == 1)) for player in
             range(1, self.nr_players + 1)]

        return None

    def extinction_waves(self):
        final_flag = False
        # for i in range(10): #ToDo: Needs to change
        while not final_flag:
            final_flag = self.extinction_wave()
        return None

    def extinction_wave(self):
        final_flag = False
        if max(self.pebbles_df.deg) == 0:
            final_flag = True
        elif max(self.pebbles_df[self.pebbles_df.placed==1].deg)==min(self.pebbles_df[self.pebbles_df.placed==1].deg):
            final_flag = True
        else:
            weakest_df = self.pebbles_df[self.pebbles_df['deg'] == min(self.pebbles_df[self.pebbles_df.placed==1].deg)]

            for i, row in weakest_df.iterrows():
                if row["placed"]:

                    stubs = (self.arrows_df['source_id']==row["id"]) | (self.arrows_df['target_id']==row["id"])
                    self.arrows_df.loc[stubs,'placed']=0
                    self.arrows_df.loc[stubs, 'source_id'] = np.nan
                    self.arrows_df.loc[stubs, 'target_id'] = np.nan

                    self.arr_state[int(row["id"]),:] = 0
                    self.arr_state[:,int(row["id"])] = 0
                    self.state['arrows'] = self.arr_state

                    self.peb_state[int(row["x"]),int(row["y"])]=0
                    self.state['pebbles'] = self.peb_state

                    self.pebbles_df.loc[int(row["id"]), "x"] = np.nan
                    self.pebbles_df.loc[int(row["id"]), "y"] = np.nan
                    self.pebbles_df.loc[int(row["id"]), "placed"] = 0
                    self.pebbles_df.loc[int(row["id"]), "deg"] = 0
                else:
                    pass

        return final_flag


    def step(self,action):
        """
        a step is taken

        action is a dictionary:
            - type: 'pebble' or 'arrow'
            - where: 2-dimensional list

        action list of pebble pos and arrow pos
        act=[peb[0],peb[1],arr[0][0],arr[0][1],arr[1][0],arr[1][1]]
        act=[peb,arr]
        """
        done = False
        # FIXME: Only do these actions when we are in placing mode !!!

        if self.stage == "placing":

            some_pebble = action[0][1] != 0
            some_arrow = action[1][1] != 0
            if self.either_peb_or_arrow:
                pebble_action = some_pebble and not some_arrow
                arrow_action = some_arrow and not some_pebble
            else:
                pebble_action = some_pebble
                arrow_action = some_arrow

            if pebble_action:
                chess_pos=action[0]
                pos = [None, None]
                pos[1] = chess_pos[1] - 1
                pos[0] = self.alpha_to_num[chess_pos[0]] - 1

                # is the position within the bounds
                if pos[0]<self.field_size and pos[1]<self.field_size:
                    # we are within the bounds
                    # choose a pebble place it and update peb state and arr state
                    temp_df = self.pebbles_df[(self.pebbles_df['placed'] == 0) & (self.pebbles_df['player'] == self.current_player)]

                    if len(temp_df)==0 :
                        # no more pebbles for this player
                        print("no more pebbles")
                    else:
                        # still some pebbles for this player

                        # may the pebble be placed or not
                        if self.peb_state[pos[0], pos[1]]==0:
                            # update pebbles state
                            self.peb_state[pos[0], pos[1]] = self.current_player
                            self.state['pebbles'] = self.peb_state

                            # update pebbles dataframe
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'x'] = pos[0]
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'y'] = pos[1]
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'placed'] = 1


                        else:
                            # pebble may not be placed
                            print("there is already a pebble here")

                else:
                    print('outside of field bounds')

            elif arrow_action:
                # place an arrow
                chess_pos = action[1]

                source = [None]*2
                target = [None]*2

                source[1] = chess_pos[1] - 1
                source[0] = self.alpha_to_num[chess_pos[0]] - 1

                target[1] = chess_pos[3] - 1
                target[0] = self.alpha_to_num[chess_pos[2]] - 1

                # is this a possible move
                source_occupied = self.peb_state[source[0], source[1]] != 0
                target_occupied = self.peb_state[target[0], target[1]] != 0

                if source_occupied and target_occupied:

                    # does the player have enough arrows left?
                    temp_df = self.arrows_df[(self.arrows_df['placed'] == 0) & (self.arrows_df['player'] == self.current_player)]

                    if len(temp_df) == 0:
                        # no more arrows for this player
                        print("no more arrows left")
                    else:
                        # update the arrow state

                        temp_source = self.pebbles_df[
                            (self.pebbles_df['x'] == source[0]) & (self.pebbles_df['y'] == source[1])]
                        temp_target = self.pebbles_df[
                            (self.pebbles_df['x'] == target[0]) & (self.pebbles_df['y'] == target[1])]

                        # we check whether there is an arrow there already
                        if self.arr_state[temp_source.iloc[0, 0], temp_target.iloc[0, 0]] == 0:
                            self.arr_state[temp_source.iloc[0, 0], temp_target.iloc[0, 0]] = self.current_player
                            self.state['arrows'] = self.arr_state

                            # update self.arrows_df
                            self.arrows_df.at[temp_df.iloc[0, 0], 'source_id'] = temp_source.iloc[0, 0]
                            self.arrows_df.at[temp_df.iloc[0, 0], 'target_id'] = temp_target.iloc[0, 0]
                            self.arrows_df.at[temp_df.iloc[0, 0], 'placed'] = 1

                            # update self.pebbles_df (update degree) .. only target degree should increase
                            self.pebbles_df.at[temp_target.iloc[0, 0], 'deg'] = self.pebbles_df.loc[temp_target.iloc[0, 0], 'deg'] + 1
                        else:
                            print('you must not place more than one arrow between any pair of pebbles.')

                else:
                    if source_occupied:
                        print("choose an occupied target grid point")
                    elif target_occupied:
                        print("choose an occupied source grid point")
                    else:
                        print("choose different grid points")

            else:
                print('no action is chosen')


            # trigger extinction wave(s)??
            if self.last_move():
                self.stage = "extinction-triggered"
                print(self.stage)
                print('before extinction the scores are ')
                print(self.scores)
                self.extinction_waves()
                # set scores
                self.assign_scores()
                print('after extinction wave and after assigning scores the scores are ')
                print(self.scores)
                # set rewards
                self._assign_rewards()
                print('This translates into the following rewards ')
                print(self.rewards)
        else:
            # we are not placing anymore
            # or rather placing does not affect the board, just everyone gets her or his reward for the game
            pass

        # compute reward
        reward = self._get_reward()
        print('The reward for this round is')
        print(reward)

        previous_stage = self.stage

        # FIXME:
        if self.stage == "extinction-rewards":
            # when all rewards were given we finish this episode
            if self.current_player == (self.triggering_player)%self.nr_players +1:
                self.stage = "game over"
                done = True
            else:
                pass
        elif self.stage == "extinction-triggered":
            # enter into a round of reward allocations
            self.stage = "extinction-rewards"
            self.triggering_player = self.current_player

        elif self.stage == "placing":
            # nothing special
            pass
        else:
            # continue as if nothing happened
            print('a bit unusual. The stage {} has never been seen.'.format(str(self.stage)))

        info = {'scores': self.scores, 'reward': reward, 'stage': self.stage, 'previous stage': previous_stage, 'current_player': self.current_player}
        print(info)
        self.update_player()
        print('next player number is'+str(self.current_player))
        print('why does the return not work?')
        return self.state, reward, done, info


    def _get_reward(self):
        return self.rewards[self.current_player-1]

    def _assign_rewards(self):
        # is the game finished?
        if self.stage == "extinction-rewards":
            if all([s==max_score for s in self.scores]):
                # its a remie for everyone
                self.rewards= [0]*self.nr_players
            else:
                # not a remie for everyone
                if self.winner_takes_it_all:
                    # have you got the max and are the only one with the max?

                    scores_sorted = deepcopy(self.scores)
                    scores_sorted.sort(reverse = True)
                    max_score = scores_sorted[0]
                    if max_score==scores_sorted[1]:
                        # we have some sort of remie
                        self.rewards = [0 if sc==max_score else -1 for sc in self.scores]
                    else:
                        # winner and looser
                        self.rewards = [1 if sc==max_score else -1 for sc in self.scores]

                else:
                    # get reward between -1 and 1 depending on your score
                    max_score = max(self.scores)
                    min_score = min(self.scores)
                    self.rewards = [ -1 + 2*(sc-min_score)/(max_score-min_score) for sc in self.scores]
        return None


    def update_player(self):
        self.current_player= (self.current_player)%self.nr_players +1


    def last_move(self):
        arr_depletion = [all(self.arrows_df.loc[self.arrows_df.player == pl + 1, "placed"])
                         for pl in range(self.nr_players)]
        print(arr_depletion)
        if self.any_or_all_arrows=="any":
            return any(arr_depletion)
        elif self.any_or_all_arrows=="all":
            return all(arr_depletion)
        else:
            print(' Game Finished condition is not specified ')
            return(False)

    def reward(self):
        return None

    def reset(self):
        self.current_player = 1
        self.either_peb_or_arrow = True
        self.any_or_all_arrows = "all"
        self.stage = "placing"
        self.win_by = "survivors"  # can also be "degree"

        self.scores = [0] * self.nr_players
        self.rewards = [0] * self.nr_players
        self.triggering_player = 0
        self.winner_takes_it_all = True

        # rendering should be set back to zero as well. Todo:

        # peb_state assigns a player number to each point on the field matrix
        self.peb_state = np.zeros([self.field_size, self.field_size], dtype=int)
        # arr_state assigns a player number to each link in the adjacency matrix
        self.arr_state = np.zeros([self.peb_total, self.peb_total], dtype=int)
        self.state['pebbles'] = self.peb_state
        self.state['arrows'] = self.arr_state

        self.pebbles_df = pd.DataFrame({'id': list(range(self.peb_total)),
                                        'player': np.repeat(list(range(1, self.nr_players + 1)), self.peb),
                                        'x': np.nan * np.ones(self.peb_total),
                                        'y': np.nan * np.ones(self.peb_total),
                                        'deg': np.zeros(self.peb_total),
                                        'placed': np.zeros(self.peb_total)}, dtype=int)
        self.arrows_df = pd.DataFrame({'id': list(range(self.nr_players * self.arr)),
                                       'player': np.repeat(list(range(1, self.nr_players + 1)), self.arr),
                                       'source_id': np.nan * np.ones(self.nr_players * self.arr),
                                       'target_id': np.nan * np.ones(self.nr_players * self.arr),
                                       'placed': np.zeros(self.nr_players * self.arr)}, dtype=int)

        self.state = {'pebbles': self.peb_state, 'arrows': self.arr_state}

        self.finish_when_any_or_all_arrows_are_gone = 'any'

    def render(self, mode='human', close=False):
        if mode == 'console':
            print(self.state)
        elif mode == "human":
            print(self.state)
        #     try:
        #         import pygame
        #         from pygame import gfxdraw
        #     except ImportError as e:
        #         raise error.DependencyNotInstalled(
        #             "{}. (HINT: install pygame using `pip install pygame`".format(e))
        #     if close:
        #         pygame.quit()
        #     else:
        #         if self.screen is None:
        #             pygame.init()
        #             self.screen = pygame.display.set_mode(
        #                 (round(self.window_width), round(self.window_height)))
        #         clock = pygame.time.Clock()
        #
        #         # Draw old bubbles
        #         self.screen.fill((255, 255, 255))
        #         for row in range(self.array_height):
        #             for column in range(self.array_width):
        #                 if self.last_board[row][column].color is not None:
        #                     bubble = self.last_board[row][column]
        #                     pygame.gfxdraw.filled_circle(
        #                         self.screen, round(
        #                             bubble.center_x), round(
        #                             bubble.center_y), self.bubble_radius, bubble.color)
        #         pygame.display.update()
        #
        #         # Draw flying bubble
        #         last_x, last_y = None, None
        #         for position in self.last_positions:
        #             if last_x is not None and last_y is not None:
        #                 pygame.gfxdraw.filled_circle(
        #                     self.screen, round(
        #                         last_x), round(
        #                         last_y), self.bubble_radius, (255, 255, 255))
        #             last_x, last_y = position[0], position[1]
        #             pygame.gfxdraw.filled_circle(
        #                 self.screen, round(
        #                     position[0]), round(
        #                     position[1]), self.bubble_radius, self.last_color)
        #             pygame.display.update()
        #             clock.tick(self.metadata["video.frames_per_second"])
        # print(self.state)
