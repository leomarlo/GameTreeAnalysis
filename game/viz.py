import tkinter as tk
from sotf import Sotf


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def gridsystem(canvas, N=5, padding=10, linewidth=4, nodewidth=6, canvas_x=100, canvas_y=200, canvas_width=600, canvas_height=350, grid_color='gray'):
    canvas.place(x=canvas_x, y=canvas_y, width=canvas_width, height=canvas_height)
    padded_height = canvas_height - 2*padding
    padded_width = canvas_width - 2*padding
    delta_h = padded_height/(N-1)
    delta_w = padded_width/(N-1)

    for i in range(N+1):
        x = padding + i * delta_w
        y = padding + i * delta_h
        canvas.create_line(x,padding, x, padding + padded_height, fill=grid_color)
        canvas.create_line(padding, y, padding + padded_width, y, fill=grid_color)
        for j in range(N+1):
            xi = x 
            yi = padding + j * delta_h
            canvas.create_circle(x=xi, y=yi, r=nodewidth/2, fill=grid_color)
    return canvas
#     # canvas.create_line(50,50,100,100,fill='white',arrow="last",arrowshape=(25,25,10),width=10)
# # canvas.grid(column=0,row=1)

class GUI():

    PLAYERS = 2
    WIDTH = 600
    HEIGHT = 600
    HALF_PAD = 20
    PAD = HALF_PAD 
    COL_WIDTH = 110
    GRID_POINTS = 4
    RULES_HEIGHT = 60
    TITLE_HEIGHT = 40
    BUTTON_HEIGHT = 40
    BUTTON_WIDTH = 140
    CANVAS_WIDTH = 300
    CANVAS_HEIGHT = 300
    CANVAS_PADDING = 10
    CANVAS_PADDED_HEIGHT = CANVAS_HEIGHT - 2*CANVAS_PADDING
    CANVAS_PADDED_WIDTH = CANVAS_WIDTH - 2*CANVAS_PADDING
    CANVAS_DY = CANVAS_PADDED_HEIGHT / (GRID_POINTS - 1)
    CANVAS_DX = CANVAS_PADDED_WIDTH / (GRID_POINTS - 1)
    GRID_LINEWIDTH = 4
    GRID_NODEWIDTH = 6
    INFOBOX_HEIGHT = 40
    PLAYER_INFO_HEIGHT = 40
    SMALL_GAP = 2
    TINY_BUTTON = 16 
    
    ARROWS = 8
    ARROW_WIDTH = 5
    DEMO_ARROW_WIDTH = 8
    PEBBLES = 5 
    PEBBLE_WIDTH = 5
    DEMO_PEBBLE_WIDTH = 10
    PLAYER_1_COLOR = 'blue'
    PLAYER_2_COLOR = 'orange'
    CANVAS_COLOR = 'white'
    GRID_COLOR = 'gray'
    CANCEL_BUTTON_COLOR = 'gray'

    ARROW_CANVAS_HEIGHT = 120
    PEBBLE_CANVAS_HEIGHT = 120

    def __init__(self):
        self.game = Sotf(peb=self.PEBBLES,
                         arr=self.ARROWS,
                         nr_players=self.PLAYERS,
                         field_size=self.GRID_POINTS,
                         action_format='compressed')

        self.window = self.initialize_window()
        self.canvas = tk.Canvas(self.window, bg=self.CANVAS_COLOR)
        self.canvas = self.initialize_main_canvas(canvas=self.canvas)
        # initialize main panel
        (self.title,
         self.info,
         self.ply1_btn,
         self.ply2_btn) = self.initialize_main_panel(window=self.window)
        # initialize player 1
        (self.ply1_title,
         self.pebs1_cnvs,
         self.rem_pebs1,
         self.place_pebs1,
         self.cancel_place_pebs1,
         self.arrs1_cnvs,
         self.rem_arrs1,
         self.place_arrs1,
         self.cancel_place_arrs1) = self.Initialize_Player_1(window=self.window)
        # initialize player 2
        (self.ply2_title,
         self.pebs2_cnvs,
         self.rem_pebs2,
         self.cancel_place_pebs2,
         self.place_pebs2,
         self.arrs2_cnvs,
         self.rem_arrs2,
         self.cancel_place_arrs2,
         self.place_arrs2) = self.Initialize_Player_2(window=self.window)
        
        # store the current element
        self.current_element = None 
        self.action = [-1,-1,-1,-1,-1,-1]
        self.status = 'nothing'
        self.previous_pos = {"x":None, "y":None, "xi":None, "yi":None}

        # register callbacks
        self.display_event_info_callback()
        self.canvas_callback()
        self.cancel_peb_or_arr()
        self.next_player()

        # start the program
        self.window.mainloop()


    #########################################################
    ##### PROPERTIES ######################################
    #########################################################

    @property
    def current_player(self):    
        return self.game.current_player


    @property
    def pebbles(self):
        ret_dict = {}
        states = ['not placed', 'placed']
        pdf = self.game.pebbles_df
        for pl in range(1,self.game.nr_players + 1):
            placed_or_not = {}
            for boolean, state in enumerate(states):
                placed_or_not[state] = len(pdf[(pdf.placed==boolean) & (pdf.player==pl)])
            ret_dict[pl] = placed_or_not
        return ret_dict 
    

    @property
    def arrows(self):
        ret_dict = {}
        states = ['not placed', 'placed']
        adf = self.game.arrows_df     
        for pl in range(1,self.game.nr_players + 1):
            placed_or_not = {}
            for boolean, state in enumerate(states):
                placed_or_not[state] = len(adf[(adf.placed==boolean) & (adf.player==pl)])
            ret_dict[pl] = placed_or_not
        return ret_dict 

    #########################################################
    ##### MAIN CONSOLE ######################################
    #########################################################

    def initialize_window(self):
        window = tk.Tk()
        window.title("Welcome")
        window.geometry('{w}x{h}'.format(w=self.WIDTH,
                                         h=self.HEIGHT))
        return window


    def initialize_main_canvas(self, canvas):
        return gridsystem(canvas=canvas,
                            N=self.GRID_POINTS,
                            padding=self.CANVAS_PADDING,
                            linewidth=self.GRID_LINEWIDTH,
                            nodewidth=self.GRID_NODEWIDTH,
                            canvas_x=(self.HALF_PAD + self.COL_WIDTH + self.PAD),
                            canvas_y=(self.HALF_PAD + self.TITLE_HEIGHT + self.PAD + self.RULES_HEIGHT + self.PAD),
                            canvas_width=self.CANVAS_WIDTH,
                            canvas_height=self.CANVAS_HEIGHT,
                            grid_color=self.GRID_COLOR)

    def reset_canvas(self, canvas):
        self.canvas.delete('all')
        self.initialize_main_canvas(canvas=canvas)


    def initialize_main_panel(self, window):
        HALF_PAD = self.HALF_PAD
        PAD = self.PAD
        TITLE_HEIGHT = self.TITLE_HEIGHT
        CANVAS_WIDTH = self.CANVAS_WIDTH
        CANVAS_HEIGHT = self.CANVAS_HEIGHT
        INFOBOX_HEIGHT = self.INFOBOX_HEIGHT
        RULES_HEIGHT = self.RULES_HEIGHT
        COL_WIDTH = self.COL_WIDTH 
        PLAYER_1_COLOR = self.PLAYER_1_COLOR
        PLAYER_2_COLOR = self.PLAYER_2_COLOR
        BUTTON_HEIGHT = self.BUTTON_HEIGHT
        BUTTON_WIDTH = self.BUTTON_WIDTH

        title = tk.Label(window, bg='white', fg='black', text='Survival Of The Fittest') #padx=5, pady=20, side=tk.LEFT)
        title.place(x=(HALF_PAD + COL_WIDTH + PAD),
                    y=HALF_PAD,
                    width=CANVAS_WIDTH,
                    height=TITLE_HEIGHT)

        rules = tk.Label(window, text='Rules', bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
        rules.place(x=(HALF_PAD + COL_WIDTH + PAD),
                    y=(HALF_PAD + TITLE_HEIGHT + PAD),
                    width=CANVAS_WIDTH,
                    height=RULES_HEIGHT)

        info = tk.Button(window, bg='white', fg='black', text='Start the Game') #padx=5, pady=20, side=tk.LEFT)
        info.place(x=(HALF_PAD + COL_WIDTH + PAD),
                y=(HALF_PAD + TITLE_HEIGHT + PAD + RULES_HEIGHT + PAD + CANVAS_HEIGHT + PAD),
                width=CANVAS_WIDTH,
                height=INFOBOX_HEIGHT)
        info.id = 'info'

        ply1_btn = tk.Button(window,
                    text="Player 1 Finished",
                    bg=PLAYER_1_COLOR,
                    fg="black")       
        ply1_btn.place(x=(HALF_PAD + COL_WIDTH + PAD),
                y=(HALF_PAD + TITLE_HEIGHT + PAD + RULES_HEIGHT + PAD + CANVAS_HEIGHT + PAD + INFOBOX_HEIGHT + PAD),
                width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        ply1_btn.id = 'ply1-btn'

        ply2_btn = tk.Button(window, 
                    text="Player 2 Finished",
                    bg=PLAYER_2_COLOR,
                    fg="black")
        ply2_btn.place(x=(HALF_PAD + COL_WIDTH + PAD + BUTTON_WIDTH + PAD),
                y=(HALF_PAD + TITLE_HEIGHT + PAD + RULES_HEIGHT + PAD + CANVAS_HEIGHT + PAD + INFOBOX_HEIGHT + PAD),
                width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        ply2_btn.id = 'ply2-btn'

        return title, info, ply1_btn, ply2_btn

    #########################################################
    ##### PLAYER 1 ##########################################
    #########################################################

    # Pebbles
    def Initialize_Player_1(self, window):

        HALF_PAD = self.HALF_PAD
        PAD = self.PAD
        TITLE_HEIGHT = self.TITLE_HEIGHT
        COL_WIDTH = self.COL_WIDTH 
        PLAYER_1_COLOR = self.PLAYER_1_COLOR
        BUTTON_HEIGHT = self.BUTTON_HEIGHT
        ARROW_WIDTH = self.ARROW_WIDTH
        CANVAS_COLOR = self.CANVAS_COLOR
        PEBBLE_CANVAS_HEIGHT = self.PEBBLE_CANVAS_HEIGHT
        ARROW_CANVAS_HEIGHT = self.ARROW_CANVAS_HEIGHT
        CANVAS_PADDING = self.CANVAS_PADDING
        PLAYER_INFO_HEIGHT = self.PLAYER_INFO_HEIGHT
        DEMO_PEBBLE_WIDTH = self.DEMO_PEBBLE_WIDTH
        SMALL_GAP = self.SMALL_GAP
        TINY_BUTTON = self.TINY_BUTTON
        CANCEL_BUTTON_COLOR = self.CANCEL_BUTTON_COLOR

        ply1_title = tk.Label(window, text='Player 1', fg='black') #padx=5, pady=20, side=tk.LEFT)
        ply1_title.place(x=(HALF_PAD),
                        y=(HALF_PAD),
                        width=COL_WIDTH,
                        height=TITLE_HEIGHT)

        pebs1_cnvs = tk.Canvas(window, bg=CANVAS_COLOR)
        pebs1_cnvs.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PEBBLE_CANVAS_HEIGHT)
        pebs1_cnvs.create_circle(int(COL_WIDTH/2), int(PEBBLE_CANVAS_HEIGHT/2), r=DEMO_PEBBLE_WIDTH/2, fill=PLAYER_1_COLOR)

        rem_pebs1 = tk.Label(window, text='Remaining: {}'.format(str(self.pebbles[1]['not placed'])), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
        rem_pebs1.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PLAYER_INFO_HEIGHT)

        place_pebs1 = tk.Button(window,
                            text="Place Pebble",
                            bg=PLAYER_1_COLOR,
                            fg="black")
        place_pebs1.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD),
                        width=(COL_WIDTH - SMALL_GAP - TINY_BUTTON),
                        height=BUTTON_HEIGHT)
        place_pebs1.id = 'place-pebs1'

        cancel_place_pebs1 = tk.Button(window,
                            text="x",
                            bg=CANCEL_BUTTON_COLOR,
                            fg="black")
        cancel_place_pebs1.place(x=(HALF_PAD + COL_WIDTH - TINY_BUTTON),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD),
                        width=TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        cancel_place_pebs1.id = 'cancel-place-pebs1'

        # Arrows

        arrs1_cnvs = tk.Canvas(window, bg=CANVAS_COLOR)
        arrs1_cnvs.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=ARROW_CANVAS_HEIGHT)
        arrs1_cnvs.create_line(int(COL_WIDTH/2), ARROW_CANVAS_HEIGHT - CANVAS_PADDING, int(COL_WIDTH/2),CANVAS_PADDING,fill=PLAYER_1_COLOR,arrow="last",arrowshape=(2*ARROW_WIDTH,2*ARROW_WIDTH,ARROW_WIDTH),width=ARROW_WIDTH)

        rem_arrs1 = tk.Label(window, text='Remaining: {}'.format(str(self.arrows[1]['not placed'])), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
        rem_arrs1.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + ARROW_CANVAS_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PLAYER_INFO_HEIGHT)

        place_arrs1 = tk.Button(window,
                            text="Place Arrow",
                            bg=PLAYER_1_COLOR,
                            fg="black")
        place_arrs1.place(x=(HALF_PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + 
                            ARROW_CANVAS_HEIGHT + PAD + 
                            PLAYER_INFO_HEIGHT + PAD),
                        width=COL_WIDTH - TINY_BUTTON - SMALL_GAP,
                        height=BUTTON_HEIGHT)
        place_arrs1.id = 'place-arrs1'


        cancel_place_arrs1 = tk.Button(window,
                            text="x",
                            bg=CANCEL_BUTTON_COLOR,
                            fg="black")
        cancel_place_arrs1.place(x=(HALF_PAD + COL_WIDTH - TINY_BUTTON),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + 
                            ARROW_CANVAS_HEIGHT + PAD + 
                            PLAYER_INFO_HEIGHT + PAD),
                        width=TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        cancel_place_arrs1.id = 'cancel-place-arrs1'

        return ply1_title, pebs1_cnvs, rem_pebs1, place_pebs1, cancel_place_pebs1, arrs1_cnvs, rem_arrs1, place_arrs1, cancel_place_arrs1

    #########################################################
    ##### PLAYER 2 ##########################################
    #########################################################


    def Initialize_Player_2(self, window):

        HALF_PAD = self.HALF_PAD
        PAD = self.PAD
        TITLE_HEIGHT = self.TITLE_HEIGHT
        COL_WIDTH = self.COL_WIDTH 
        PLAYER_2_COLOR = self.PLAYER_2_COLOR
        BUTTON_HEIGHT = self.BUTTON_HEIGHT
        ARROW_WIDTH = self.ARROW_WIDTH
        CANVAS_COLOR = self.CANVAS_COLOR
        CANVAS_WIDTH = self.CANVAS_WIDTH
        PEBBLE_CANVAS_HEIGHT = self.PEBBLE_CANVAS_HEIGHT
        ARROW_CANVAS_HEIGHT = self.ARROW_CANVAS_HEIGHT
        CANVAS_PADDING = self.CANVAS_PADDING
        PLAYER_INFO_HEIGHT = self.PLAYER_INFO_HEIGHT
        DEMO_PEBBLE_WIDTH = self.DEMO_PEBBLE_WIDTH
        SMALL_GAP = self.SMALL_GAP
        TINY_BUTTON = self.TINY_BUTTON
        CANCEL_BUTTON_COLOR = self.CANCEL_BUTTON_COLOR

        ply2_title = tk.Label(window, text='Player 2', fg='black') #padx=5, pady=20, side=tk.LEFT)
        ply2_title.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD),
                        width=COL_WIDTH,
                        height=TITLE_HEIGHT)

        pebs2_cnvs = tk.Canvas(window, bg=CANVAS_COLOR)
        pebs2_cnvs.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PEBBLE_CANVAS_HEIGHT)
        pebs2_cnvs.create_circle(int(COL_WIDTH/2), int(PEBBLE_CANVAS_HEIGHT/2), r=DEMO_PEBBLE_WIDTH/2, fill=PLAYER_2_COLOR)

        rem_pebs2 = tk.Label(window, text='Remaining: {}'.format(str(self.pebbles[2]['not placed'])), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
        rem_pebs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PLAYER_INFO_HEIGHT)

        cancel_place_pebs2 = tk.Button(window,
                            text="x",
                            bg=CANCEL_BUTTON_COLOR,
                            fg="black")
        cancel_place_pebs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD),
                        width=TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        cancel_place_pebs2.id = 'cancel-place-pebs2'


        place_pebs2 = tk.Button(window,
                            text="Place Pebble",
                            bg=PLAYER_2_COLOR,
                            fg="black")
        place_pebs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD + TINY_BUTTON + SMALL_GAP),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD),
                        width=COL_WIDTH - SMALL_GAP - TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        place_pebs2.id = 'place-pebs2'


        # Arrows

        arrs2_cnvs = tk.Canvas(window, bg=CANVAS_COLOR)
        arrs2_cnvs.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=ARROW_CANVAS_HEIGHT)
        arrs2_cnvs.create_line(int(COL_WIDTH/2), ARROW_CANVAS_HEIGHT - CANVAS_PADDING, int(COL_WIDTH/2),CANVAS_PADDING,fill=PLAYER_2_COLOR,arrow="last",arrowshape=(2*ARROW_WIDTH,2*ARROW_WIDTH,ARROW_WIDTH),width=ARROW_WIDTH)

        rem_arrs2 = tk.Label(window, text='Remaining: {}'.format(str(self.arrows[2]['not placed'])), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
        rem_arrs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + ARROW_CANVAS_HEIGHT + PAD),
                        width=COL_WIDTH,
                        height=PLAYER_INFO_HEIGHT)

        cancel_place_arrs2 = tk.Button(window,
                            text="x",
                            bg=CANCEL_BUTTON_COLOR,
                            fg="black")
        cancel_place_arrs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + 
                            ARROW_CANVAS_HEIGHT + PAD + 
                            PLAYER_INFO_HEIGHT + PAD),
                        width=TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        cancel_place_arrs2.id = 'cancel-place-arrs2'


        place_arrs2 = tk.Button(window,
                            text="Place Arrow",
                            bg=PLAYER_2_COLOR,
                            fg="black")
        place_arrs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD + SMALL_GAP + TINY_BUTTON),
                        y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                            BUTTON_HEIGHT + PAD + 
                            ARROW_CANVAS_HEIGHT + PAD + 
                            PLAYER_INFO_HEIGHT + PAD),
                        width=COL_WIDTH - SMALL_GAP - TINY_BUTTON,
                        height=BUTTON_HEIGHT)
        place_arrs2.id = 'place-arrs2'

        return ply2_title, pebs2_cnvs, rem_pebs2, cancel_place_pebs2, place_pebs2, arrs2_cnvs, rem_arrs2, cancel_place_arrs2, place_arrs2



    #########################################################
    ##### REGISTER CALLBACKS ################################
    #########################################################

    def next_player(self):
        self.ply1_btn.bind("<Button-1>", self.Player_1_finished, add='+')
        self.ply2_btn.bind("<Button-1>", self.Player_2_finished, add='+')

    def canvas_callback(self):
        self.canvas.bind("<Button-1>", self.canvas_click_event, add='+')

    def cancel_peb_or_arr(self):
        self.cancel_place_pebs1.bind("<Button 1>", self.remove_element, add='+')
        self.cancel_place_pebs2.bind("<Button 1>", self.remove_element, add='+')
        self.cancel_place_arrs1.bind("<Button 1>", self.remove_element, add='+')
        self.cancel_place_arrs2.bind("<Button 1>", self.remove_element, add='+')


    def display_event_info_callback(self):

        self.place_pebs1.bind("<Button 1>", self.display_event_id, add='+')
        self.place_pebs1.bind("<Button 1>", lambda e: self.set_status('place_pebble',player=1), add='+')
        self.place_pebs2.bind("<Button 1>", self.display_event_id, add='+')
        self.place_pebs2.bind("<Button 1>", lambda e: self.set_status('place_pebble',player=2), add='+')
        self.place_arrs1.bind("<Button 1>", self.display_event_id, add='+')
        self.place_arrs1.bind("<Button 1>", lambda e: self.set_status('select_arrow',player=1), add='+')
        self.place_arrs2.bind("<Button 1>", self.display_event_id, add='+')
        self.place_arrs2.bind("<Button 1>", lambda e: self.set_status('select_arrow',player=2), add='+')

    #########################################################
    #####  EVENT HANDLING  ##################################
    #########################################################

    def remove_element(self, event):
        print('remove', self.status)
        if self.current_element:
            self.canvas.delete(self.current_element)
            self.current_element = None
            self.action = [-1,-1,-1,-1,-1,-1]
            self.status = 'nothing'

    def set_status(self, status, player, exception=True):

        print(self.status)
        if player!=self.current_player:
            return None
        if exception and self.status=='finished':
            return None
        self.status = status
        
    
    def imprint_state_to_canvas(self):
        colors = [self.PLAYER_1_COLOR, self.PLAYER_2_COLOR]
        adf = self.game.arrows_df
        pdf = self.game.pebbles_df
        self.reset_canvas(canvas=self.canvas)
        for ri, peb in pdf[pdf.placed==1].iterrows():
            x = self.CANVAS_PADDING + peb["x"]*self.CANVAS_DX
            y = self.CANVAS_PADDING + peb["y"]*self.CANVAS_DY
            self.canvas.create_circle(x=x, y=y, r=self.PEBBLE_WIDTH, fill=colors[int(peb["player"]) - 1])
        for ai, arr in adf[adf.placed==1].iterrows():
            source = pdf[pdf.id==arr["source_id"]]
            target = pdf[pdf.id==arr["target_id"]]
            sx = self.CANVAS_PADDING + source.x.values[0]*self.CANVAS_DX
            sy = self.CANVAS_PADDING + source.y.values[0]*self.CANVAS_DY
            tx = self.CANVAS_PADDING + target.x.values[0]*self.CANVAS_DX
            ty = self.CANVAS_PADDING + target.y.values[0]*self.CANVAS_DY
            self.canvas.create_line(sx, sy, tx, ty, fill=colors[int(arr["player"])-1],arrow="last", arrowshape=(2*self.ARROW_WIDTH,2*self.ARROW_WIDTH,self.ARROW_WIDTH),width=self.ARROW_WIDTH)

    def reset_for_turn(self):
        self.action = [-1,-1,-1,-1,-1,-1]
        self.previous_pos = {p:None for p in self.previous_pos}
        self.current_element = None
        self.status = 'nothing'


    def Player_1_finished(self, event):
        if self.current_player!=1:
            print('it\'s not your turn')
            return None
        state, reward, done, nac = self.game.step(action=self.action)
        self.reset_for_turn()
        self.imprint_state_to_canvas()
        self.rem_pebs1["text"] = 'Remaining: {}'.format(str(self.pebbles[1]['not placed']))
        self.rem_pebs2["text"] = 'Remaining: {}'.format(str(self.pebbles[2]['not placed']))
        self.rem_arrs1["text"] = 'Remaining: {}'.format(str(self.arrows[1]['not placed']))
        self.rem_arrs2["text"] = 'Remaining: {}'.format(str(self.arrows[2]['not placed']))
        if done:
            print('done')


    def Player_2_finished(self, event):
        if self.current_player!=2:
            print('it\'s not your turn')
            return None
        state, reward, done, nac = self.game.step(action=self.action)
        self.reset_for_turn()
        self.imprint_state_to_canvas()
        if done:
            print('done')


    def canvas_click_event(self, event):
        xi = int((event.x - self.CANVAS_PADDING + self.CANVAS_DX / 2) / self.CANVAS_DX)
        yi = int((event.y - self.CANVAS_PADDING + self.CANVAS_DY / 2) / self.CANVAS_DY)
        x = self.CANVAS_PADDING + xi*self.CANVAS_DX
        y = self.CANVAS_PADDING + yi*self.CANVAS_DY
        colors = [self.PLAYER_1_COLOR, self.PLAYER_2_COLOR]
        # print(event.x, event.y)
        if self.status == 'place_pebble':
            self.current_element = self.canvas.create_circle(x=x, y=y, r=self.DEMO_PEBBLE_WIDTH, fill=colors[self.current_player - 1])
            self.action = [xi,yi,-1,-1,-1,-1]
            self.status = 'finished'
        elif self.status == 'remove_last_pebble':
            print(self.current_element)
            if self.current_element:
                self.canvas.delete(self.current_element)
                self.current_element = None
                self.action = [-1,-1,-1,-1,-1,-1]
                self.status = 'nothing'
        elif self.status == 'place_arrow':
            pdf = self.game.pebbles_df
            if len(pdf[(pdf.placed) & ((pdf.x==float(xi)) & (pdf.y==float(yi)))])>0:
                self.current_element = self.canvas.create_line(self.previous_pos["x"], self.previous_pos["y"], x, y, fill=colors[self.current_player - 1],arrow="last",arrowshape=(2*self.DEMO_ARROW_WIDTH,2*self.DEMO_ARROW_WIDTH,self.DEMO_ARROW_WIDTH),width=self.DEMO_ARROW_WIDTH)
                self.action = [-1,-1,self.previous_pos["xi"],self.previous_pos["yi"],xi,yi]
                self.status = 'finished'
        elif self.status == 'select_arrow':
            pdf = self.game.pebbles_df
            if len(pdf[(pdf.placed) & ((pdf.x==float(xi)) & (pdf.y==float(yi)))])>0:
                self.previous_pos = {"x":x, "y":y, "xi": xi, "yi": yi}
                self.status = 'place_arrow'
        else: 
            # dont do anything
            pass
            
        # print "clicked at", event.x, event.y

    def display_event_id(self, event):
        # print(dir(event.widget))
        print(event.widget.id)
        widget_id = event.widget.id
        player = widget_id[-1]
        if widget_id=='place-pebs1':
            new_text = "Player {} selected a pebble".format(player)
            self.info["text"] = new_text
        if widget_id=='place-pebs2':
            new_text = "Player {} selected a pebble".format(player)
            self.info["text"] = new_text
        if widget_id=='place-arrs1':
            new_text = "Player {} selected an arrow".format(player)
            self.info["text"] = new_text
        if widget_id=='place-arrs2':
            new_text = "Player {} selected an arrow".format(player)
            self.info["text"] = new_text
        # print('hello')



    #########################################################
    ##### START THE LOOP ####################################
    #########################################################

    # window.mainloop()

# %%


game_GUI = GUI()