"""Shared beat sheet — animation and audio both read these (seconds)."""

FPS = 30
TOTAL = 55.5

# world layout (x positions)
X_START = 0.0
X_BLOCK = 8.0
Y_BLOCK = 3.4
X_BUG_ENTER = 16.5
X_STOMP = 12.9
X_PIPE1 = 20.0
X_PIPE2 = 32.0
X_FLAG = 42.0
X_VICTORY = 39.9

# beats
TITLE_END = 6.0
RUN1 = (7.0, 12.4)          # x 0 -> 8
JUMP1 = 13.2                # jump at block
BONK = 13.55                # contact
PANEL_ON = 14.3
DING = 18.5                 # > YES
PANEL_OFF = 19.6
COIN_POP = 20.0
COIN_END = 21.0
HOP = 21.4                  # happy hop
BUG_ENTER = 22.5            # bug walks in from right
RUN2 = (24.6, 27.2)         # x 8 -> 11.4
JUMP2 = 27.4                # leap onto bug
STOMP = 28.15               # squish
SIGN_ON = 28.45
SIGN_OFF = 30.4
RUN3 = (30.6, 33.4)         # x -> pipe1 base (18.6)
PIPE_JUMP = 33.5            # hop up onto rim
PIPE_TOP = 34.2
PIPE_DOWN = (34.6, 35.8)    # descend into pipe
DARK = (35.7, 36.5)         # black beat
POP_OUT = (36.6, 37.5)      # rise from pipe2
RUN4 = (38.2, 41.6)         # x 33.2 -> 40.4
FLAG_JUMP = 41.8
FLAG_GRAB = 42.3
SLIDE = (42.3, 44.0)
TASK_TEXT = 45.0
FIREWORKS = (44.8, 46.1, 47.4)
IRIS = (49.4, 50.4)
END_CARD = 50.8
TOKENS_AT = COIN_POP + 0.45  # HUD counter increments
