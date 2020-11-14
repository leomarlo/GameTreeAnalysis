import numpy as np
import pandas as pd
from copy import deepcopy


class Sotf():

    metadata = {'render.modes': ['human', 'console']}

    def __init__(self,peb,arr,nr_players,field_size,action_format='default'):
        self.peb = peb
        self.arr = arr
        self.nr_players = nr_players
        self.current_player = 1
        self.field_size = field_size
        self.peb_total = self.nr_players * self.peb

        self.action = None
        self.done = False

        self.either_peb_or_arrow=True
        self.any_or_all_arrows="all"
        self.stage="placing"
        self.win_by = "survivors" # can also be "degree"

        # encoding and decoding functions for pebble and arrow states respectively.
        self.enc_peb, self.dec_peb = encode_state(multipl=self.nr_players + 1,
                                        size=self.field_size)
        self.enc_arr, self.dec_arr = encode_state(multipl=self.nr_players + 1,
                                        size=self.peb_total)

        self.convert_action = turn_into_action(action_format=action_format)
        self.scores = [0]*self.nr_players
        self.rewards = [0]*self.nr_players
        self.triggering_player = 0
        self.winner_takes_it_all = True
        # True: 1 point for highest score. 0 points for everyone the same score. -1 for someone else has the hightest score
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

        # space of possibilities
        # self.space_of_poss = pd.Data

        self.finish_when_any_or_all_arrows_are_gone='any'


    def assign_scores(self):
        if self.win_by=="survivors":
            self.scores=[sum((self.pebbles_df['player']==player) & (self.pebbles_df['placed']==1)) for player in range(1,self.nr_players+1)]
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
        # self.done = False
        # FIXME: Only do these actions when we are in placing mode !!!

        if self.stage == "placing":

            converted_action = self.convert_action(ac=action)
            self.action = converted_action
            some_pebble = converted_action[0] >= 0
            some_arrow = converted_action[2] >= 0
            if self.either_peb_or_arrow:
                pebble_action = some_pebble and not some_arrow
                arrow_action = some_arrow and not some_pebble
            else:
                pebble_action = some_pebble
                arrow_action = some_arrow

            if pebble_action:
                # is the position within the bounds
                if converted_action[0]<self.field_size and converted_action[1]<self.field_size:
                    # we are within the bounds
                    # choose a pebble place it and update peb state and arr state
                    temp_df = self.pebbles_df[(self.pebbles_df['placed'] == 0) & (self.pebbles_df['player'] == self.current_player)]

                    if len(temp_df)==0 :
                        # no more pebbles for this player
                        print("no more pebbles")
                    else:
                        # still some pebbles for this player

                        # may the pebble be placed or not
                        if self.peb_state[converted_action[0], converted_action[1]]==0:
                            # update pebbles state
                            self.peb_state[converted_action[0], converted_action[1]] = self.current_player
                            self.state['pebbles'] = self.peb_state

                            # update pebbles dataframe
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'x'] = converted_action[0]
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'y'] = converted_action[1]
                            self.pebbles_df.at[temp_df.iloc[0, 0], 'placed'] = 1


                        else:
                            # pebble may not be placed
                            print("there is already a pebble here")

                else:
                    print('outside of field bounds')

            elif arrow_action:
                source = converted_action[2:4]
                target = converted_action[4:6]
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
                self.stage = "extinction-rewards"
                # set rewards
                self._assign_rewards()  
                print('This translates into the following rewards ')
                print(self.rewards)
                self.done = True

        else:
            # we are not placing anymore
            # or rather placing does not affect the board, just everyone gets her or his reward for the game
            pass

        self.update_player()
        reward = 0
        info = 'nothing'

        return self.state, reward, self.done, info


    def _get_reward(self):
        return self.rewards[self.current_player-1]

    def _assign_rewards(self):
        # is the game finished?
        if self.stage == "extinction-rewards":
            scores_sorted = deepcopy(self.scores)
            scores_sorted.sort(reverse = True)
            max_score = scores_sorted[0]
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

    def options(self):
        # pebble options are all the vacant spots, if you have pebbles left.

        # arrow options are all the pairs of pebbles that conform to arrow-laying, if there are arrows left.
        
        # everything should be in a decoded form.
        return None

    def encode_df(self):
        peb_str =  '.'.join(sorted([''.join(a) for a in self.pebbles_df.loc[self.pebbles_df.placed==1,['player','x','y','deg']].values.astype(int).astype('U')]))
        arr_str_list = []
        source_n_target = ["source_id", "target_id"]
        for i, row in self.arrows_df.loc[self.arrows_df.placed==1, ['player'] + source_n_target].iterrows():
            arr_str_i = ''.join([ pos for f in source_n_target for pos in self.pebbles_df.loc[self.pebbles_df.id==row[f],['x','y']].values[0].astype(int).astype('U')])
            arr_str_list.append(str(int(row['player'])) + arr_str_i)
        arr_str = '.'.join(sorted(arr_str_list))
        return peb_str, arr_str

    def decode_state(self, peb_str, arr_str):
        pebs = [self.peb]*self.nr_players
        dics = []
        for i,bb in enumerate(peb_str.split('.')):
            player = int(bb[0])
            dic = {'player': player, 'x':float(bb[1]), 'y': float(bb[2]), 'id':i, 'placed':1, 'deg':bb[3]}
            dics.append(dic)
            pebs[player-1]-=1
        layed_peb_df = pd.DataFrame(dics)
        rest = [{'player': i + 1, 'x':np.nan, 'y':np.nan, 'deg':0, 'placed':0} for i,peb in enumerate(pebs) for j in range(peb)]
        rest_df = pd.DataFrame(rest)
        rest_df['id'] = rest_df.index + i + 1
        peb_df = layed_peb_df.append(rest_df)
        # TODO; index still screwed up
        del dics
        # and now for the arrows
        arrs = [self.arr]*self.nr_player
        dics = []
        for i,aa in enumerate(arr_str.split('.')):
            player = int(aa[0])
            # TODO: SOMEHOW THESE ARE EMPTY.
            source_id = layed_peb_df[(layed_peb_df.x==float(aa[1])) & (layed_peb_df.y==float(aa[2]))].id.values[0]
            target_id = layed_peb_df[(layed_peb_df.x==float(aa[3])) & (layed_peb_df.y==float(aa[4]))].id.values[0]
            dic = {'id':i, 'player': player, 'source_id': source_id, 'target_id': target_id, 'placed':1}
            dics.append(dic)
            arrs[player-1]-=1
        layed_arr_df = pd.DataFrame(dics)
        rest = [{'player': i + 1, 'source_id':np.nan, 'target_id':np.nan, 'placed':0} for i,arr in enumerate(arrs) for j in range(arr)]
        rest_df = pd.DataFrame(rest)
        rest_df['id'] = rest_df.index + i + 1
        arr_df = layed_arr_df.append(rest_df)

        return peb_df, arr_df

    def reset(self):
        self.current_player = 1
        self.either_peb_or_arrow = True
        self.any_or_all_arrows = "all"
        self.stage = "placing"
        self.win_by = "survivors"  # can also be "degree"
        self.done = False
        self.action = None

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




def turn_into_action(action_format='default'):
    """create a conversion function that converts an action input during the game

    Parameters
    ----------
    action_format : dict or str, optional
        If a dictionary is passed, then there are the following options:
            "format" -> ("dictionary", "list_of_lists" or "single_list")
            "coordinates" -> ("chess", "number" or "python")
            "arrow_in_2d_array" -> (True or False)
            "None_or_minus_one" -> ("none" or "minus_one")
        Most of these are self-explanatory.
        The way it is handled in the code is:
            "format": "single_list"
            "coordinates": "python"
            "arrow_in_2d_array": False
            "None_or_minus_one": "none"
        The most intuitive and convenient for human input is:
            "format": "dictionary"
            "coordinates": "chess"
            "arrow_in_2d_array": True
            "None_or_minus_one": "minus_one"
        This is also the default assignment.
        If a string is passed, then it can be either 'default' or 'compressed'. The latter is the way that python handles it.

    Returns
    -------
    function
        a function that takes the action and turns it into a python handable action
    """

    # default

    default = {"format":"dictionary",
                "coordinates":"chess",
                "arrow_in_2d_array":True,
                "None_or_minus_one": "none"}

    compressed = {"format":"list",
                    "coordinates":"number",
                    "arrow_in_2d_array":False,
                    "None_or_minus_one": "minus_one"}

    if action_format=='default':
        action_dict = default
    elif action_format=='compressed':
        action_dict = compressed
    elif isinstance(action_format,dict):
        # print(action_format)
        action_dict = {k: (action_format[k] if k in action_format else v) 
                        for k, v in default.items()}
        # print(action_dict)
    else:
        action_dict = default  # like default

    alphabet = ' abcdefghijklmnopqrstuvwxyz'
    alpha_to_num = {letter: i for i, letter in enumerate(alphabet)}
    alpha_to_num.update({LETTER.upper(): i for i, LETTER in enumerate(alphabet)})

    # define the coordinate conversion
    if action_dict["coordinates"] == 'chess' and action_dict["None_or_minus_one"] == "none":
        def c_conv(xy):
            x = (alpha_to_num[xy[0]] if xy[0] in alpha_to_num else 0) 
            y = (xy[1] if xy[1] is not None else 0) 
            return [x - 1, y - 1]
    elif action_dict["coordinates"] == 'chess' and action_dict["None_or_minus_one"] == "minus_one":
        def c_conv(xy):
            x = (alpha_to_num[xy[0]] if xy[0] in alpha_to_num else 0) 
            y = (xy[1] if xy[1]>0 else 0) 
            return [x - 1, y - 1]
    elif action_dict["coordinates"] == 'number' and action_dict["None_or_minus_one"] == "none":
        def c_conv(xy):
            return [(-1 if z is None else z - 1) for z in xy]
    elif action_dict["coordinates"] == 'number' and action_dict["None_or_minus_one"] == "minus_one":
        def c_conv(xy):
            return [(-1 if z<=0 else z - 1) for z in xy]
    elif action_dict["coordinates"] == 'python' and action_dict["None_or_minus_one"] == "none":
        def c_conv(xy):
            return [(-1 if z is None else z) for z in xy]
    elif action_dict["coordinates"] == 'python' and action_dict["None_or_minus_one"] == "minus_one":
        def c_conv(xy):
            return [(-1 if z<=-1 else z) for z in xy]
    else:
        def c_conv(xy):
            return [(-1 if z<=-1 else z) for z in xy]

    # define the dict conversion
    if action_dict["format"] == 'dictionary' and action_dict["arrow_in_2d_array"]==False:
        def d_conv(ac):
            return ac["pebble"], ac["arrow"][0:2], ac["arrow"][2:4]
    elif action_dict["format"] == 'dictionary' and action_dict["arrow_in_2d_array"]==True:
        def d_conv(ac):
            return ac["pebble"], ac["arrow"][0], ac["arrow"][1]
    elif action_dict["format"] == 'single_list' and action_dict["arrow_in_2d_array"]==False:
        def d_conv(ac):
            return ac[0:2], ac[2:4], ac[4:6]
    elif action_dict["format"] == 'single_list' and action_dict["arrow_in_2d_array"]==True:
        def d_conv(ac):
            return ac[0:2], ac[3][0], ac[3][1]
    elif action_dict["format"] == 'list_of_lists' and action_dict["arrow_in_2d_array"]==False:
        def d_conv(ac):
            return ac[0], ac[1][0:2], ac[1][2:4]
    elif action_dict["format"] == 'list_of_lists' and action_dict["arrow_in_2d_array"]==True:
        def d_conv(ac):
            return ac[0], ac[1][0], ac[1][1]
    else:
        def d_conv(ac):
            return ac[0:2], ac[2:4], ac[4:6]


    if all([compressed[k] == v for k, v in action_dict.items()]):
        def fun(ac):
            return ac
    else:
        def fun(ac):
            peb, source, target = d_conv(ac)
            return c_conv(peb) + c_conv(source) + c_conv(target)
    
    return fun

def encode_df_fun(peb_df, arr_df):
    peb_str =  '.'.join(sorted([''.join(a) for a in peb_df.loc[peb_df.placed==1,['player','x','y','deg']].values.astype(int).astype('U')]))
    arr_str_list = []
    source_n_target = ["source_id", "target_id"]
    for i, row in arr_df.loc[arr_df.placed==1, ['player'] + source_n_target].iterrows():
        arr_str_i = ''.join([ pos for f in source_n_target for pos in peb_df.loc[peb_df.id==row[f],['x','y']].values[0].astype(int).astype('U')])
        arr_str_list.append(str(int(row['player'])) + arr_str_i)
    arr_str = '.'.join(sorted(arr_str_list))
    return peb_str, arr_str





def encode_state(multipl,size):

    # return sum([s * (multipl ** i) for i,s in enumerate(state.flatten())])
    def encode(state):
        string_encoded = ''.join(state.flatten().astype('U'))
        return int(string_encoded,multipl)

    def decode(number):
        string_decoded = str_base(number=number, base=multipl)
        if string_decoded=='0':
            padded_string = '0'*(size**2)
        else:
            padded_string = '0'*(size**2 - len(string_decoded)) + string_decoded
        return np.array(list(padded_string)).astype(int).reshape(size,size)
    
    return encode, decode


def digit_to_char(digit):
    if digit < 10:
        return str(digit)
    return chr(ord('a') + digit - 10)

def str_base(number,base):
    if number < 0:
        return '-' + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digit_to_char(m)
    return digit_to_char(m)
