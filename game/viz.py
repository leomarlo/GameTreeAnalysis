#%%
import tkinter as tk
from sotf import Sotf


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

def gridsystem(window, N=5, padding=10, linewidth=4, nodewidth=6, canvas_x=100, canvas_y=200, canvas_width=600, canvas_height=350, canvas_color='white',grid_color='gray'):
    canvas = tk.Canvas(window, bg=canvas_color)
    canvas.place(x=canvas_x, y=canvas_y, width=canvas_width, height=canvas_height)
    padded_height = canvas_height - 2*padding
    padded_width = canvas_width - 2*padding
    delta_h = int(padded_height/(N-1))
    delta_w = int(padded_width/(N-1))

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
    # canvas.create_line(50,50,100,100,fill='white',arrow="last",arrowshape=(25,25,10),width=10)
# canvas.grid(column=0,row=1)

# class GUI():

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
GRID_LINEWIDTH = 4
GRID_NODEWIDTH = 6
INFOBOX_HEIGHT = 40
PLAYER_INFO_HEIGHT = 40
ARROWS = 8
ARROW_WIDTH = 5
PEBBLES = 5 
PEBBLE_WIDTH = 5
DEMO_PEBBLE_WIDTH = 10
PLAYER_1_COLOR = 'blue'
PLAYER_2_COLOR = 'orange'
CANVAS_COLOR = 'white'
GRID_COLOR = 'gray'

ARROW_CANVAS_HEIGHT = 120
PEBBLE_CANVAS_HEIGHT = 120

game = Sotf(peb=PEBBLES,
            arr=ARROWS,
            nr_players=2,
            field_size=GRID_POINTS)

arrs1 = ARROWS 
pebs1 = PEBBLES
arrs2 = ARROWS 
pebs2 = PEBBLES


#########################################################
##### MAIN CONSOLE ######################################
#########################################################

window = tk.Tk()

window.title("Welcome")
window.geometry('{w}x{h}'.format(w=WIDTH,h=HEIGHT))

canvas = gridsystem(window=window,
                    N=GRID_POINTS,
                    padding=CANVAS_PADDING,
                    linewidth=GRID_LINEWIDTH,
                    nodewidth=GRID_NODEWIDTH,
                    canvas_x=(HALF_PAD + COL_WIDTH + PAD),
                    canvas_y=(HALF_PAD + TITLE_HEIGHT + PAD + RULES_HEIGHT + PAD),
                    canvas_width=CANVAS_WIDTH,
                    canvas_height=CANVAS_HEIGHT,
                    canvas_color=CANVAS_COLOR,
                    grid_color=GRID_COLOR)

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

#########################################################
##### PLAYER 1 ##########################################
#########################################################

# Pebbles

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

rem_pebs1 = tk.Label(window, text='Remaining: {}'.format(str(pebs1)), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
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
                  width=COL_WIDTH,
                  height=BUTTON_HEIGHT)
place_pebs1.id = 'place-pebs1'
# Arrows

arrs1_cnvs = tk.Canvas(window, bg=CANVAS_COLOR)
arrs1_cnvs.place(x=(HALF_PAD),
                 y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                    BUTTON_HEIGHT + PAD),
                 width=COL_WIDTH,
                 height=ARROW_CANVAS_HEIGHT)
arrs1_cnvs.create_line(int(COL_WIDTH/2), ARROW_CANVAS_HEIGHT - CANVAS_PADDING, int(COL_WIDTH/2),CANVAS_PADDING,fill=PLAYER_1_COLOR,arrow="last",arrowshape=(2*ARROW_WIDTH,2*ARROW_WIDTH,ARROW_WIDTH),width=ARROW_WIDTH)

rem_arrs1 = tk.Label(window, text='Remaining: {}'.format(str(arrs1)), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
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
                  width=COL_WIDTH,
                  height=BUTTON_HEIGHT)
place_arrs1.id = 'place-arrs1'

#########################################################
##### PLAYER 2 ##########################################
#########################################################

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

rem_pebs2 = tk.Label(window, text='Remaining: {}'.format(str(pebs2)), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
rem_pebs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD),
                width=COL_WIDTH,
                height=PLAYER_INFO_HEIGHT)

place_pebs2 = tk.Button(window,
                     text="Place Pebble",
                     bg=PLAYER_2_COLOR,
                     fg="black")
place_pebs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                  y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD),
                  width=COL_WIDTH,
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

rem_arrs2 = tk.Label(window, text='Remaining: {}'.format(str(arrs2)), bg='white', fg='black') #padx=5, pady=20, side=tk.LEFT)
rem_arrs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                    BUTTON_HEIGHT + PAD + ARROW_CANVAS_HEIGHT + PAD),
                width=COL_WIDTH,
                height=PLAYER_INFO_HEIGHT)

place_arrs2 = tk.Button(window,
                     text="Place Arrow",
                     bg=PLAYER_2_COLOR,
                     fg="black")
place_arrs2.place(x=(HALF_PAD + COL_WIDTH + PAD + CANVAS_WIDTH + PAD),
                  y=(HALF_PAD + TITLE_HEIGHT + PAD + PEBBLE_CANVAS_HEIGHT + PAD + PLAYER_INFO_HEIGHT + PAD +
                    BUTTON_HEIGHT + PAD + 
                    ARROW_CANVAS_HEIGHT + PAD + 
                    PLAYER_INFO_HEIGHT + PAD),
                  width=COL_WIDTH,
                  height=BUTTON_HEIGHT)
place_arrs2.id = 'place-arrs2'

#########################################################
#####  EVENT HANDLING  ##################################
#########################################################

def select_pebble(event):
    # print(dir(event.widget))
    print(event.widget.id)
    widget_id = event.widget.id
    player = widget_id[-1]
    if widget_id=='place-pebs1':
        new_text = "Player {} selected a pebble".format(player)
        info["text"] = new_text
        print(new_text)
    if widget_id=='place-pebs2':
        new_text = "Player {} selected a pebble".format(player)
        info["text"] = new_text
        print(new_text)
    if widget_id=='place-arrs1':
        new_text = "Player {} selected an arrow".format(player)
        info["text"] = new_text
        print(new_text)
    if widget_id=='place-arrs2':
        new_text = "Player {} selected an arrow".format(player)
        info["text"] = new_text
        print(new_text)
    # print('hello')

place_pebs1.bind("<Button 1>", select_pebble, add='+')
place_pebs2.bind("<Button 1>", select_pebble, add='+')
place_arrs1.bind("<Button 1>", select_pebble, add='+')
place_arrs2.bind("<Button 1>", select_pebble, add='+')



#########################################################
##### START THE LOOP ####################################
#########################################################

window.mainloop()

# %%
