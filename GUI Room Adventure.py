from tkinter import *
from casino_rooms import Room
from PIL import Image, ImageTk
import casino_of_sin
import threading
import winsound

#Added on by Claude when prompted
def _play(beeps):
    """Play a sequence of (frequency_hz, duration_ms) beeps in a background thread."""
    def _run():
        for freq, ms in beeps:
            winsound.Beep(freq, ms)
    threading.Thread(target=_run, daemon=True).start()


# ── sound presets ─────────────────────────────────────────────────────────────
SND_MOVE    = [(400,  60)]                                 # footstep click
SND_PLAY    = [(700,  80), (900,  60)]                     # game start
SND_HIT     = [(520,  70)]                                 # card draw
SND_STAND   = [(350, 120)]                                 # hold decision
SND_BET     = [(600,  80)]                                 # place a bet
SND_SHOP    = [(800,  60), (1000, 60)]                     # open shop
SND_BUY     = [(900,  60), (1100, 80)]                     # purchase
SND_USE     = [(600,  50), (800,  50), (1000, 60)]         # use consumable
SND_WIN     = [(523, 100), (659, 100), (784, 150)]         # C-E-G victory
SND_LOSE    = [(400, 100), (350, 100), (280, 200)]         # descending loss

# ── colour palette ────────────────────────────────────────────────────────────
BG_DARK    = "#1A1A2E"   # window / outer background
BG_MID     = "#16213E"   # info panel background
BG_PANEL   = "#0F3460"   # button / nav background
ACCENT     = "#E94560"   # border highlight / separators
GOLD       = "#FFD700"   # headings and money
TEXT_LIGHT = "#F0F0F0"   # primary text
TEXT_DIM   = "#A8A8C0"   # secondary / dim text
BTN_GREEN  = "#2D6A4F"   # Play button
BTN_RED    = "#C0392B"   # Red button
BTN_BLACK  = "#1a1a1a"   # Black button
BTN_USE    = "#4A235A"   # Use-item button (deep purple)

# ── typography ────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Georgia",  18, "bold")
FONT_BODY   = ("Arial",    11)
FONT_BTN    = ("Arial",    12, "bold")
FONT_NAV    = ("Arial",    16, "bold")
FONT_STAT   = ("Arial",    13, "bold")
FONT_RESULT = ("Arial",    10)
FONT_SMALL  = ("Arial",    10, "bold")

BTN_W = 14   # uniform width for all action buttons

# ── end-state image paths ─────────────────────────────────────────────────────
DEATH_IMAGE   = "Game Over.png"
VICTORY_IMAGE = "Victory.png"


# ── room setup ────────────────────────────────────────────────────────────────
def createRooms():
    rooms = []

    main      = Room("Main Floor - Cashier")
    roulette  = Room("Roulette Room")
    blackjack = Room("Blackjack Room")
    bar       = Room("Bar")
    cockfight = Room("Cockfight Pit")
    wheel     = Room("Wheel of Fortune Room")

    main.image      = "Main Room.png"
    roulette.image  = "Roulette Room.png"
    blackjack.image = "Black Jack Art.png"
    bar.image       = "Bar Art.png"
    cockfight.image = "Cock Fight.png"
    wheel.image     = "Spin The Wheel Art.png"

    main.game      = None
    roulette.game  = casino_of_sin.playRoulette
    blackjack.game = casino_of_sin.playBlackjack
    bar.game       = None
    cockfight.game = casino_of_sin.startCockfight
    wheel.game     = casino_of_sin.spinTheWheel

    bar.shop = casino_of_sin.goShop

    # --- MAIN FLOOR ---
    main.description = (
        "You stand on the casino's main floor. You owe $10,000 to an alien "
        "loan shark — if you don't pay up, Earth explodes. Good luck."
    )
    main.addExit("west", roulette)
    main.addExit("east", wheel)
    rooms.append(main)

    # --- ROULETTE ---
    roulette.description = "You're in the Roulette Room. Time to put it all on black."
    roulette.addExit("east", main)
    roulette.addExit("north", blackjack)
    roulette.addItem("wheel", "The roulette wheel spins hypnotically.")
    rooms.append(roulette)

    # --- BLACKJACK ---
    blackjack.description = "Welcome to the Blackjack Room. Ready to play some cards?"
    blackjack.addExit("south", roulette)
    blackjack.addExit("east",  bar)
    blackjack.addItem("table", "A blackjack table with scattered chips.")
    rooms.append(blackjack)

    # --- BAR ---
    bar.description = "You're at the bar. Buy drinks here for a gambling edge."
    bar.addExit("west", blackjack)
    bar.addExit("east", cockfight)
    rooms.append(bar)

    # --- COCKFIGHT ---
    cockfight.description = "You're in the Cockfight Pit. Bet on some feathered fury."
    cockfight.addExit("west", bar)
    cockfight.addExit("south", wheel)
    rooms.append(cockfight)

    # --- WHEEL OF FORTUNE ---
    wheel.description = "You're in the Wheel of Fortune Room. Test your luck."
    wheel.addExit("north", cockfight)
    wheel.addExit("west",  main)
    rooms.append(wheel)

    return rooms, main


# ── main application ──────────────────────────────────────────────────────────
class App(Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_DARK)
        self.pack(fill="both", expand=True)

        self.rooms, self.currentRoom = createRooms()

        # outer grid: main content row (weight 4) + nav bar row (weight 1)
        self.grid_rowconfigure(0, weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_main_panel()
        self._build_nav_panel()
        self.update_room_display()

    # ── panel builders ────────────────────────────────────────────────────────

    def _build_main_panel(self):
        """Two-column layout: room image (left) | info + actions (right)."""
        self.main_frame = Frame(self, bg=BG_DARK)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 8))
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=3)   # image column
        self.main_frame.grid_columnconfigure(1, weight=2)   # info column

        # ── left: image panel ─────────────────────────────────────────────────
        self.img_panel = Frame(self.main_frame, bg=BG_DARK,
                               highlightbackground=ACCENT, highlightthickness=2)
        self.img_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.img_panel.grid_rowconfigure(0, weight=1)
        self.img_panel.grid_rowconfigure(1, weight=0)
        self.img_panel.grid_columnconfigure(0, weight=1)

        self.image_label = Label(self.img_panel, bg=BG_DARK)
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.room_title = Label(
            self.img_panel, text="", font=FONT_TITLE,
            bg=BG_DARK, fg=GOLD, pady=8
        )
        self.room_title.grid(row=1, column=0)

        # ── right: info panel ─────────────────────────────────────────────────
        self.info_panel = Frame(self.main_frame, bg=BG_MID,
                                highlightbackground=ACCENT, highlightthickness=2)
        self.info_panel.grid(row=0, column=1, sticky="nsew")
        self.info_panel.grid_columnconfigure(0, weight=1)

        # Row 0 — Room description
        self.room_desc = Label(
            self.info_panel, text="", font=FONT_BODY,
            bg=BG_MID, fg=TEXT_LIGHT,
            wraplength=270, justify="left", anchor="nw",
            padx=14, pady=10
        )
        self.room_desc.grid(row=0, column=0, sticky="ew")

        self._separator(self.info_panel, row=1)

        # Row 2 — Money
        self.money_label = Label(
            self.info_panel,
            text=f"Money:  ${casino_of_sin.money}",
            font=FONT_STAT, bg=BG_MID, fg=GOLD,
            anchor="w", padx=14, pady=6
        )
        self.money_label.grid(row=2, column=0, sticky="ew")

        # Row 3 — Inventory text
        self.inventory_label = Label(
            self.info_panel,
            text=f"Inventory:  {casino_of_sin.inventory}",
            font=FONT_BODY, bg=BG_MID, fg=TEXT_DIM,
            anchor="w", padx=14, pady=4, wraplength=270
        )
        self.inventory_label.grid(row=3, column=0, sticky="ew")

        # Row 4 — Use-item buttons (dynamically populated)
        self.use_frame = Frame(self.info_panel, bg=BG_MID)
        self.use_frame.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 4))
        self.use_frame.grid_columnconfigure(0, weight=1)
        self.use_frame.grid_columnconfigure(1, weight=1)

        self._separator(self.info_panel, row=5)

        # Row 6 — Game result text
        self.result_label = Label(
            self.info_panel, text="", font=FONT_RESULT,
            bg=BG_MID, fg=TEXT_LIGHT,
            wraplength=270, justify="left", anchor="nw",
            padx=14, pady=8
        )
        self.result_label.grid(row=6, column=0, sticky="ew")

        self._separator(self.info_panel, row=7)

        # Row 8 — Action buttons container
        self.action_frame = Frame(self.info_panel, bg=BG_MID)
        self.action_frame.grid(row=8, column=0, sticky="ew", padx=14, pady=12)
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        self._build_action_buttons()

    def _separator(self, parent, row):
        Frame(parent, bg=ACCENT, height=1).grid(
            row=row, column=0, sticky="ew", padx=14
        )

    def _btn(self, parent, text, bg, fg, command, width=None):
        return Button(
            parent, text=text, font=FONT_BTN,
            width=width or BTN_W, bg=bg, fg=fg,
            activebackground=ACCENT, activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            padx=6, pady=8,
            command=command
        )

    def _build_action_buttons(self):
        af = self.action_frame

        self.play_button = self._btn(af, "▶  Play", BTN_GREEN, "white", self.play_game)

        self.hit_button   = self._btn(af, "Hit",   BG_PANEL, GOLD, lambda: self.hit_or_stand("hit"))
        self.stand_button = self._btn(af, "Stand", BG_PANEL, GOLD, lambda: self.hit_or_stand("stand"))

        self.red_button   = self._btn(af, "🔴  Red",   BTN_RED,   "white", lambda: self.red_or_black("red"))
        self.black_button = self._btn(af, "⬛  Black", BTN_BLACK, "white", lambda: self.red_or_black("black"))

        self.buy_button            = self._btn(af, "🛒  Shop",    BG_PANEL, GOLD,       self.shop)
        self.beer_button           = self._btn(af, "🍺  Beer",    BG_PANEL, TEXT_LIGHT, lambda: self.buy_item("Beer"))
        self.vodka_button          = self._btn(af, "🥃  Vodka",   BG_PANEL, TEXT_LIGHT, lambda: self.buy_item("Vodka"))
        self.powdered_sugar_button = self._btn(af, "🍬  Sugar",   BG_PANEL, TEXT_LIGHT, lambda: self.buy_item("Powdered Sugar"))

    def _build_nav_panel(self):
        """Bottom navigation bar with centred D-pad."""
        self.nav_frame = Frame(self, bg=BG_DARK,
                               highlightbackground=ACCENT, highlightthickness=2)
        self.nav_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=0)
        self.nav_frame.grid_columnconfigure(2, weight=1)
        self.nav_frame.grid_rowconfigure(0, weight=1)

        dpad = Frame(self.nav_frame, bg=BG_DARK)
        dpad.grid(row=0, column=1, pady=8)

        def nav_btn(text, cmd):
            return Button(
                dpad, text=text, font=FONT_NAV,
                width=5, height=1,
                bg=BG_PANEL, fg=TEXT_LIGHT,
                activebackground=ACCENT, activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                command=cmd
            )

        self.up_button    = nav_btn("▲ N", lambda: self.move("north"))
        self.left_button  = nav_btn("◀ W", lambda: self.move("west"))
        self.right_button = nav_btn("E ▶", lambda: self.move("east"))
        self.down_button  = nav_btn("▼ S", lambda: self.move("south"))

        self.up_button.grid   (row=0, column=1, padx=6, pady=4)
        self.left_button.grid (row=1, column=0, padx=6, pady=4)
        self.right_button.grid(row=1, column=2, padx=6, pady=4)
        self.down_button.grid (row=2, column=1, padx=6, pady=4)

    # ── inventory use-buttons ─────────────────────────────────────────────────

    def _refresh_use_buttons(self): #Vibe coded the buttons with Claude
        """Rebuild the Use-button row to match the current inventory."""
        for widget in self.use_frame.winfo_children():
            widget.destroy()

        items = casino_of_sin.inventory
        if not items:
            return

        icons = {
            "Beer":           "🍺",
            "Vodka":          "🥃",
            "Powdered Sugar": "🍬",
        }

        for col, item in enumerate(items):
            icon  = icons.get(item.name, "✨")
            label = f"{icon} Use {item.name}"
            btn = Button(
                self.use_frame,
                text=label,
                font=FONT_SMALL,
                bg=BTN_USE, fg=GOLD,
                activebackground=ACCENT, activeforeground="white",
                relief="flat", bd=0, cursor="hand2",
                padx=6, pady=6,
                command=lambda n=item.name: self.use_item(n)
            )
            btn.grid(
                row=col // 2, column=col % 2,
                sticky="ew",
                padx=(0, 4) if col % 2 == 0 else (4, 0),
                pady=3
            )

    # ── game logic ────────────────────────────────────────────────────────────

    def move(self, direction):
        if direction in self.currentRoom.exits:
            _play(SND_MOVE)
            i = self.currentRoom.exits.index(direction)
            self.currentRoom = self.currentRoom.exitLocations[i]
            self.update_room_display()

    def hit_or_stand(self, choice):
        _play(SND_HIT if choice == "hit" else SND_STAND)
        casino_of_sin.choice = choice
        msg = casino_of_sin.playBlackjack()
        self.result_label.config(text=msg if msg else "")
        self.money_label.config(text=f"Money:  ${casino_of_sin.money}")
        if not casino_of_sin.blackjackState["active"]:
            self._hide_all_actions()
            self.play_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=4)
        self._check_end_state()

    def red_or_black(self, answer):
        _play(SND_BET)
        casino_of_sin.answer = answer
        msg = casino_of_sin.playRoulette()
        self.result_label.config(text=msg if msg else "")
        self.money_label.config(text=f"Money:  ${casino_of_sin.money}")
        self._hide_all_actions()
        self.play_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=4)
        self._check_end_state()

    def buy_item(self, item_name):
        _play(SND_BUY)
        msg = casino_of_sin.buyItem(item_name)
        self.result_label.config(text=msg)
        self.money_label.config(text=f"Money:  ${casino_of_sin.money}")
        self.inventory_label.config(text=f"Inventory:  {casino_of_sin.inventory}")
        self._refresh_use_buttons()

    def use_item(self, item_name):
        _play(SND_USE)
        msg = casino_of_sin.useItem(item_name)
        self.result_label.config(text=msg)
        self.inventory_label.config(text=f"Inventory:  {casino_of_sin.inventory}")
        self._refresh_use_buttons()

    def play_game(self):
        _play(SND_PLAY)
        if self.currentRoom.name == "Blackjack Room":
            self._hide_all_actions()
            self.hit_button.grid  (row=0, column=0, sticky="ew", padx=(0, 4), pady=4)
            self.stand_button.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)
            msg = casino_of_sin.startBlackjack()
            self.result_label.config(text=msg if msg else "")
            self.money_label.config(text=f"Money:  ${casino_of_sin.money}")

        elif self.currentRoom.name == "Roulette Room":
            self._hide_all_actions()
            self.red_button.grid  (row=0, column=0, sticky="ew", padx=(0, 4), pady=4)
            self.black_button.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)

        elif self.currentRoom.game:
            msg = self.currentRoom.game()
            self.result_label.config(text=msg if msg else "")
            self.money_label.config(text=f"Money:  ${casino_of_sin.money}")
            self._check_end_state()

    def shop(self):
        _play(SND_SHOP)
        if self.currentRoom.name == "Bar":
            self._hide_all_actions()
            self.beer_button.grid          (row=0, column=0, sticky="ew", padx=(0, 4), pady=4)
            self.vodka_button.grid         (row=0, column=1, sticky="ew", padx=(4, 0), pady=4)
            self.powdered_sugar_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)

    def _hide_all_actions(self):
        for w in self.action_frame.winfo_children():
            w.grid_remove()

    # ── end-state (death / victory) ───────────────────────────────────────────

    def _disable_all_controls(self):
        """Disable every navigation and action button so the game is locked."""
        for btn in (self.up_button, self.left_button,
                    self.right_button, self.down_button):
            btn.config(state=DISABLED)
        for w in self.action_frame.winfo_children():
            w.config(state=DISABLED)

    def _trigger_end_state(self, state):
        """Display Game Over.png or Victory.png and lock all controls."""
        self._hide_all_actions()
        self._disable_all_controls()

        # Clear inventory use-buttons — nothing is usable any more
        for widget in self.use_frame.winfo_children():
            widget.destroy()

        _play(SND_LOSE if state == "death" else SND_WIN)

        if state == "death":
            image_path  = DEATH_IMAGE
            title_text  = "💀  GAME OVER"
            end_color   = BTN_RED
            desc_text   = (
                "You couldn't repay your debts. The alien loan shark has arrived. "
                "Earth has been destroyed. You failed humanity."
            )
            result_text = f"Final balance: ${casino_of_sin.money}"
        else:
            image_path  = VICTORY_IMAGE
            title_text  = "🎉  YOU WIN!"
            end_color   = GOLD
            desc_text   = (
                "You paid back every penny! The alien loan shark is satisfied. "
                "Earth is saved. You are a legend."
            )
            result_text = f"Final balance: ${casino_of_sin.money} — Humanity saved!"

        # Load and display the end-state image
        end_img = Image.open(image_path)
        end_img = end_img.resize((580, 380))
        tk_img  = ImageTk.PhotoImage(end_img)
        self.image_label.config(image=tk_img)
        self.image_label.image = tk_img

        self.room_title.config(text=title_text,    fg=end_color)
        self.room_desc.config( text=desc_text,     fg=end_color)
        self.result_label.config(text=result_text, fg=end_color)
        self.money_label.config(text=f"Money:  ${casino_of_sin.money}")

    def _check_end_state(self):
        """Check money and trigger the appropriate end screen if the game is over.

        Returns True if an end state was triggered, False otherwise.
        """
        if casino_of_sin.money <= 0:
            self._trigger_end_state("death")
            return True
        elif casino_of_sin.money >= 10000:
            self._trigger_end_state("victory")
            return True
        return False

    def update_room_display(self):
        self.result_label.config(text="")
        self.room_title.config(text=self.currentRoom.name, fg=GOLD)
        self.room_desc.config(text=self.currentRoom.description, fg=TEXT_LIGHT)
        self.money_label.config(text=f"Money:  ${casino_of_sin.money}")
        self.inventory_label.config(text=f"Inventory:  {casino_of_sin.inventory}")
        self._refresh_use_buttons()

        img = Image.open(self.currentRoom.image)
        img = img.resize((580, 380))
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img

        self._hide_all_actions()

        if self.currentRoom.game is not None:
            self.play_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=4)
        elif self.currentRoom.name == "Bar":
            self.buy_button.grid(row=0, column=0, columnspan=2, sticky="ew", pady=4)

        # Check for death / victory AFTER all normal display updates are done
        self._check_end_state()


# ── entry point ───────────────────────────────────────────────────────────────
window = Tk()
window.title("Casino of Sin")
window.geometry("1050x700")
window.configure(bg=BG_DARK)
window.resizable(True, True)

app = App(window)
window.mainloop()

