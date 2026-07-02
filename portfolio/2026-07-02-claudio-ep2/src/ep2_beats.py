"""Ep2 beat sheet — WORLD 1-2: the bug bites back. Shared by animate + audio."""

FPS = 30
TOTAL = 57.0

# layout
X_START = 0.0
X_MEET = 6.6          # where the stomp attempt happens
X_JUMP_FROM = 5.0
X_FREEZE = 6.0        # mid-air freeze x
Y_FREEZE = 1.5
X_BLOCK = 3.6         # background set dressing
Y_BLOCK = 3.4
X_PIPE = 13.0

# beats
TITLE_END = 5.0
RUN = (5.4, 8.6)              # x 0 -> 5.0
JUMP = 8.8                    # leap toward the bug
FREEZE = 9.3                  # physics suspended mid-air
PANEL_ON = 9.8                # ALLOW CLAUDIO TO STOMP THIS BUG?
TIMEOUT = 13.3                # REQUEST TIMED OUT (red)
FALL = 14.3                   # gravity resumes
SPLAT = 14.8                  # face-first
BUG_CHARGE = 15.6             # bug winds up
BUG_HIT = 16.2                # contact! knockback + cap flies
TICK1 = 17.3                  # first glitch tick (1-2 frames)
TICK2 = 18.2
GETUP = (18.6, 20.4)
CORR1 = (20.5, 30.0)          # corruption 0 -> 0.5
CLOUD_FALL = 23.0
CLONE1 = 24.5                 # t-pose clone appears
ERRORS_FROM = 25.5            # dialog toasts start
BUGS_MULTIPLY = 27.0
ARM_STRETCH = 28.4
CORR2 = (30.0, 38.6)          # corruption 0.5 -> 1.0
FLOAT_FROM = 31.5             # gravity fails for Claudio
MODE_FLICKER = 32.0           # renderer modes leak (rainbow/normals/depth)
HEAD_DETACH = 34.0
RECURSE_PANELS = 35.0         # ALLOW CLAUDIO TO EXIST?
GIANT_BUG = 36.5
BSOD = (38.6, 39.5)
VOID = (39.5, 44.5)
REMINDER_TXT = 41.0           # <system-reminder> in the void
REASSEMBLE = (44.5, 46.0)     # world snaps back WRONG
PANCAKE = 45.4                # Claudio flattens
BUG_WALK = (46.4, 48.2)       # bug approaches (wearing the cap)
BUG_CLIMB = 48.4
SIGN_ON = 48.9                # CLAUDIO FIXED ✓
GLITCH_FW = (49.6, 50.7)      # wrong fireworks
END_CARD = 51.6
TOTAL_END = TOTAL
