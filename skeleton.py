import os
import json
from datetime import datetime
import threading

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import tkinter.font as tkfont

# Optional: sound playback (placeholder). If `playsound` is installed, it will be used.
import importlib
playsound = None
try:
    if importlib.util.find_spec("playsound") is not None:
        mod = importlib.import_module("playsound")
        playsound = getattr(mod, "playsound", None)
except Exception:
    playsound = None

# Reworked scene data with branching 'next' indices for choices.
scene_data = [
    {
        "id": 0,
        "title": "Prologue: The Awakening",
        "text": "Lucas wakes again to the same gray morning. He’s restless, yearning for something more. A strange memory of an old tree lingers.",
        "choices": ["Explore the town", "Touch the tree again", "Quit"],
        # next indices: Explore -> 1, Touch tree -> 2, Quit -> None
        "next": [1, 2, None],
        "effects": [
            {"compassion": 0, "visibility": 0, "ambition": 0},
            {"compassion": 0, "visibility": 0, "ambition": 1},
            {}
        ],
        "soundtrack": "prologue_theme.mp3"
    },
    {
        "id": 1,
        "title": "Town Square",
        "text": "The town square bustles with life. A small kitten cries near the fountain; an artist struggles with a canvas; townsfolk whisper of a strange helper.",
        "choices": ["Help the kitten", "Talk to the artist", "Return home"],
        "next": [3, 4, 5],
        "effects": [
            {"compassion": 2},
            {"visibility": 1, "compassion": 1},
            {"ambition": 0}
        ],
        "soundtrack": "square_loop.mp3"
    },
    {
        "id": 2,
        "title": "The Old Tree",
        "text": "You stand beneath the gnarled branches. The bark hums faintly as you place your hand on it. The world tilts and becomes still.",
        "choices": ["Step closer", "Pull back", "Quit"],
        "next": [6, 5, None],
        "effects": [
            {"ambition": 2},
            {"ambition": 0},
            {}
        ],
        "soundtrack": "mystic_tree.mp3"
    },
    {
        "id": 3,
        "title": "Rescue the Kitten",
        "text": "You scoop the trembling kitten into your arms. It purrs and curls around your neck. The owner returns and thanks you with a warm smile.",
        "choices": ["Stay and chat", "Leave with a smile", "Return to square"],
        "next": [7, 7, 1],
        "effects": [
            {"compassion": 2, "visibility": 0},
            {"compassion": 1},
            {}
        ]
    },
    {
        "id": 4,
        "title": "The Artist",
        "text": "The artist's canvas is dull. You offer encouragement; they reveal a lost inspiration and a secret—an old legend about a skeleton who helps the town.",
        "choices": ["Encourage more", "Ask about legend", "Return to square"],
        "next": [7, 8, 1],
        "effects": [
            {"compassion": 1, "visibility": 1},
            {"visibility": 2},
            {}
        ]
    },
    {
        "id": 5,
        "title": "Home Root",
        "text": "You return home briefly. The house is warm; your family laughs. Still, the memory of the tree and the town's small needs tug at you.",
        "choices": ["Head back out", "Reflect quietly", "Quit"],
        "next": [1, 9, None],
        "effects": [
            {},
            {"compassion": 1},
            {}
        ]
    },
    {
        "id": 6,
        "title": "Transformation",
        "text": "The world slips into mist. You awaken to cold air against bone—you're a skeleton. Unseen by most, you feel both distant and free.",
        "choices": ["Use this to help", "Search for purpose", "Try to sleep it off"],
        "next": [7, 9, 5],
        "effects": [
            {"compassion": 1, "visibility": -1},
            {},
            {}
        ],
        "soundtrack": "transformation_swirl.mp3"
    },
    {
        "id": 7,
        "title": "Acts of Kindness",
        "text": "You move unseen, nudging lost items back to owners, fixing small harms, and leaving notes of comfort. Word spreads of a mysterious helper.",
        "choices": ["Keep helping", "Explore farther", "Reflect on impact"],
        "next": [10, 11, 12],
        "effects": [
            {"compassion": 2},
            {"compassion": 1, "visibility": 1},
            {"compassion": 1}
        ],
        "soundtrack": "kindness_loop.mp3"
    },
    {
        "id": 8,
        "title": "Legend of the Skeleton",
        "text": "The artist tells stories of a skeletal guardian who appears in times of need. You wonder if you can become that guardian — and whether you'll ever be seen again.",
        "choices": ["Embrace legend", "Stay hidden", "Return to square"],
        "next": [7, 7, 1],
        "effects": [
            {"visibility": 2},
            {"visibility": -1},
            {}
        ]
    },
    {
        "id": 9,
        "title": "Search Within",
        "text": "You spend time thinking about who you are now. Memory and empathy guide your decisions; small acts feel more meaningful than grand gestures.",
        "choices": ["Act on empathy", "Plan a big act", "Return home"],
        "next": [7, 13, 5],
        "effects": [
            {"compassion": 2},
            {"ambition": 2},
            {}
        ]
    },
    {
        "id": 10,
        "title": "Steady Growth",
        "text": "Your steady kindness nudges a bright change in town morale. People help one another more, and you feel something inside shift toward warmth.",
        "choices": ["Celebrate quietly", "Push further", "Quietly observe"],
        "next": [12, 13, 12],
        "effects": [
            {"compassion": 1},
            {"ambition": 1, "visibility": 1},
            {}
        ]
    },
    {
        "id": 11,
        "title": "New District",
        "text": "You explore a new neighborhood. There, a child is scared of the dark; a gardener's tools are missing. Each small help ripples outward.",
        "choices": ["Help the child", "Find the tools", "Return to square"],
        "next": [10, 10, 1],
        "effects": [
            {"compassion": 2},
            {"compassion": 1},
            {}
        ]
    },
    {
        "id": 12,
        "title": "Quiet Reflection",
        "text": "You sit beneath a streetlamp and watch the town breathe. Your actions have meaning. The light feels warmer each night.",
        "choices": ["Keep going", "Seek a final purpose", "Rest"],
        "next": [7, 14, 5],
        "effects": [
            {"compassion": 1},
            {"ambition": 1},
            {}
        ]
    },
    {
        "id": 13,
        "title": "The Big Gesture",
        "text": "You plan a public act: restoring the ruined mural in the square. The town gathers, and your unseen work inspires many to join.",
        "choices": ["Finish the mural", "Reveal yourself", "Let others finish"],
        "next": [15, 16, 15],
        "effects": [
            {"compassion": 2, "visibility": 1},
            {"visibility": 3, "revealed": 1},
            {"compassion": 1}
        ],
        "soundtrack": "mural_finale.mp3"
    },
    {
        "id": 14,
        "title": "Finding Purpose",
        "text": "You realize purpose isn't a single grand act—it's the sum of small, steady kindnesses. The choice is yours how public you want to be.",
        "choices": ["Live quietly helping", "Return to being seen", "Reflect and decide"],
        "next": [15, 15, 15],
        "effects": [
            {"compassion": 2},
            {"visibility": 2},
            {}
        ]
    },
    {
        "id": 15,
        "title": "Epilogue: Echoes",
        "text": "The town flourishes. Whether skeleton or boy, your choice to care reshaped lives. Legends start quietly, grown from countless small hands.",
        "choices": ["Restart", "Quit"],
        "next": [0, None],
        "effects": [{}, {}],
        "end": True,
    },
    {
        "id": 16,
        "title": "Aftermath: The Reveal",
        "text": "You step forward and reveal yourself. Gasps, then silence, then voices. Some are afraid, some are grateful. The town must decide what you mean to them.",
        "choices": ["Speak gently", "Leave quietly", "Let the crowd decide"],
        "next": [17, 15, 15],
        "effects": [
            {"compassion": 2, "visibility": 2},
            {"visibility": 1},
            {}
        ],
        "soundtrack": "reveal_theme.mp3"
    },
    {
        "id": 17,
        "title": "Dialogue with the Town",
        "text": "You explain why you helped: not for praise, but because people matter. An elder approaches and tells of the tree's promise—whoever cares for the town may inherit its blessing.",
        "choices": ["Accept blessing", "Refuse and stay hidden", "Ask about the tree"],
        "next": [18, 15, 19],
        "effects": [
            {"compassion": 1, "visibility": 2, "ambition": 1},
            {"visibility": -1},
            {}
        ]
    },
    {
        "id": 18,
        "title": "Keeper's Choice",
        "text": "The elder leads you to the old tree at dusk. Its roots glow faintly. The town's gratitude and your steady care awaken a new role: Keepership of the tree's memory.",
        "choices": ["Become the Tree's Keeper", "Share the role with others"],
        "next": [20, 15],
        "effects": [
            {"compassion": 3, "visibility": 1, "tree_blessing": 1},
            {"compassion": 2, "visibility": 2}
        ],
        "soundtrack": "tree_blessing.mp3"
    },
    {
        "id": 19,
        "title": "The Elder's Tale",
        "text": "The elder tells of generations who cared for the town. The tree remembers every kindness. He warns that famous acts can be fragile—care must be constant.",
        "choices": ["Promise constant care", "Walk away"],
        "next": [15, 15],
        "effects": [
            {"compassion": 2},
            {}
        ]
    },
    {
        "id": 20,
        "title": "Tree's Blessing",
        "text": "You accept the role. The tree blooms quietly. The town honors the role with small ceremonies; your lore becomes intertwined with the town's rhythms.",
        "choices": ["Live as Keeper", "Train successors"],
        "next": [15, 15],
        "effects": [
            {"compassion": 3, "visibility": 1},
            {"compassion": 2}
        ],
        "end": True,
    },
    {
        "id": 21,
        "title": "Forgotten Path",
        "text": "Sometimes even legends fade. You choose anonymity and the years pass gently. The town remembers, but the story becomes a whisper, held by a few.",
        "choices": ["Restart", "Quit"],
        "next": [0, None],
        "effects": [{}, {}],
        "end": True,
    },
    {
        "id": 22,
        "title": "Legendary Festival",
        "text": "Years after your deeds, the town celebrates a new festival. Murals, music, and small rituals honor care. Children dress as skeletons to remind everyone of kindness.",
        "choices": ["Join the festival", "Watch from afar"],
        "next": [15, 15],
        "effects": [
            {"compassion": 2, "visibility": 2},
            {}
        ],
        "end": True,
    },
]


class TextAdventureGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Lost Skeleton")
        self.master.configure(bg="black")
        # Start fullscreen by default
        try:
            self.master.attributes("-fullscreen", True)
            self.fullscreen = True
        except Exception:
            self.fullscreen = False

        # Bind Escape to toggle fullscreen
        self.master.bind("<Escape>", lambda e: self.toggle_fullscreen())
        # Bind resize to update responsive layout
        self.master.bind("<Configure>", lambda e: self.on_resize(e))

        self.chapter = 0
        self.font_size = 12

        # Music control
        self._music_thread = None
        self._music_stop_event = None

        # Gameplay tracking
        self.history = []  # list of {scene_id, title, choice}
        self.stats = {"compassion": 0, "visibility": 0, "ambition": 0}
        self.save_file = os.path.join(os.path.dirname(__file__), "endings.json")
        self.settings_file = os.path.join(os.path.dirname(__file__), "settings.json")

        # Load settings (font, sound, fullscreen preference)
        self.settings = {
            "font_family": "Georgia",
            "font_size": 14,
            "enable_sound": False,
            "start_fullscreen": True,
            "wrap_margin": 80,
        }
        self.load_settings()

        self.scene_text = tk.StringVar()
        self.choice_buttons = []

        self.create_widgets()
        self.show_main_menu()

    def create_widgets(self):
        # Use a clearer font for readability; fallback to default if missing
        self.default_font = tkfont.Font(family=self.settings.get("font_family", "Georgia"), size=self.settings.get("font_size", self.font_size))
        # Main content area: left (scene) and right (HUD)
        self.content_frame = tk.Frame(self.master, bg="black")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.left_frame = tk.Frame(self.content_frame, bg="black")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.content_frame, bg="black", width=280)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.scene_label = tk.Label(
            self.left_frame,
            textvariable=self.scene_text,
            wraplength=700,
            justify=tk.LEFT,
            fg="white",
            bg="black",
            font=self.default_font
        )
        self.scene_label.pack(fill=tk.BOTH, expand=True)

        # Buttons container to be responsive (on left)
        self.buttons_frame = tk.Frame(self.left_frame, bg="black")
        self.buttons_frame.pack(fill=tk.X, padx=12, pady=6)
        for i in range(3):
            button = tk.Button(
                self.buttons_frame,
                text="",
                command=lambda i=i: self.process_choice(i),
                fg="white",
                bg="black",
                bd=0
            )
            button.pack(side=tk.TOP, fill=tk.X, pady=4)
            self.choice_buttons.append(button)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.master,
            variable=self.progress_var,
            maximum=len(scene_data),
            length=500,
            mode='determinate',
            style="TProgressbar"
        )
        self.progress_bar.pack(padx=12, pady=6)

        bottom_frame = tk.Frame(self.master, bg="black")
        bottom_frame.pack(pady=6)

        restart_button = tk.Button(
            bottom_frame,
            text="Restart",
            command=self.restart_game,
            fg="white",
            bg="black",
            bd=0
        )
        restart_button.pack(side=tk.LEFT, padx=8)

        quit_button = tk.Button(
            bottom_frame,
            text="Quit",
            command=self.quit_game,
            fg="white",
            bg="black",
            bd=0
        )
        quit_button.pack(side=tk.LEFT, padx=8)

        # Settings button
        settings_button = tk.Button(bottom_frame, text="Settings", command=self.open_settings, fg="white", bg="black", bd=0)
        settings_button.pack(side=tk.LEFT, padx=8)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("TProgressbar", thickness=20, troughcolor="black", background="white")

        # --- HUD on the right ---
        hud_title = tk.Label(self.right_frame, text="HUD", fg="white", bg="black", font=("Arial", 14, "bold"))
        hud_title.pack(pady=(6, 2))

        # Stats labels: icon + numeric value rows
        self.hud_images = {}
        self.stat_labels = {}
        icon_map = {"compassion": "heart.png", "visibility": "eye.png", "ambition": "star.png"}
        for key in ["compassion", "visibility", "ambition"]:
            row = tk.Frame(self.right_frame, bg="black")
            row.pack(anchor=tk.W, padx=8, pady=2)
            img_path = os.path.join(os.path.dirname(__file__), "assets", "hud_icons", icon_map.get(key, ""))
            img = None
            try:
                if os.path.exists(img_path):
                    img = tk.PhotoImage(file=img_path)
            except Exception:
                img = None
            if img:
                # keep reference to avoid GC
                self.hud_images[key] = img
                icon_lbl = tk.Label(row, image=img, bg="black")
                icon_lbl.pack(side=tk.LEFT)
            else:
                icon_lbl = tk.Label(row, text=key[0].upper(), fg="white", bg="black")
                icon_lbl.pack(side=tk.LEFT)
            value_lbl = tk.Label(row, text=str(self.stats.get(key, 0)), fg="white", bg="black")
            value_lbl.pack(side=tk.LEFT, padx=(8, 0))
            self.stat_labels[key] = value_lbl

        tk.Label(self.right_frame, text="", bg="black").pack()

        # Choice history
        hist_label = tk.Label(self.right_frame, text="Choice History:", fg="white", bg="black")
        hist_label.pack(anchor=tk.W, padx=8)
        self.history_box = tk.Listbox(self.right_frame, width=40, height=12, bg="black", fg="white")
        self.history_box.pack(padx=8, pady=4, fill=tk.BOTH, expand=False)
        hist_scroll = tk.Scrollbar(self.right_frame, command=self.history_box.yview)
        self.history_box.config(yscrollcommand=hist_scroll.set)
        hist_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        clear_btn = tk.Button(self.right_frame, text="Clear History", command=self.clear_history, fg="white", bg="black", bd=0)
        clear_btn.pack(pady=6)

        # Widgets ready; don't auto-display scene until main menu calls start
        return

    # --- Main Menu ---
    def show_main_menu(self):
        for w in self.master.winfo_children():
            w.destroy()

        self.master.configure(bg="black")
        # Optional main menu background image (assets/mainmenu_bg.png|jpg)
        bg_img = None
        try:
            base = os.path.dirname(__file__)
            candidates = [os.path.join(base, 'assets', 'mainmenu_bg.png'),
                          os.path.join(base, 'assets', 'mainmenu_bg.jpg'),
                          os.path.join(base, 'images', 'mainmenu_bg.png'),
                          os.path.join(base, 'images', 'mainmenu_bg.jpg')]
            for p in candidates:
                if os.path.exists(p):
                    try:
                        bg_img = tk.PhotoImage(file=p)
                    except Exception:
                        try:
                            from PIL import Image, ImageTk
                            img = Image.open(p)
                            # scale to window size
                            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
                            img = img.resize((w, h), Image.LANCZOS)
                            bg_img = ImageTk.PhotoImage(img)
                        except Exception:
                            bg_img = None
                    break
        except Exception:
            bg_img = None
        if bg_img:
            # keep a reference to avoid GC
            self._mainmenu_bg_img = bg_img
            bg_label = tk.Label(self.master, image=bg_img)
            bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            try:
                # ensure background is behind other widgets
                bg_label.lower()
            except Exception:
                pass
        title_font = tkfont.Font(family="Georgia", size=24, weight="bold")
        # Create a centered menu container for title/buttons (placed above background)
        menu_container = tk.Frame(self.master, bg="", bd=0)
        menu_container.place(relx=0.5, rely=0.12, anchor='n')

        # (logo disabled) — title will be shown without a logo image

        title = tk.Label(menu_container, text="Lost Skeleton", fg="white", bg="black", font=title_font)
        title.pack(pady=8)

        sub = tk.Label(menu_container, text="A tale of small kindnesses and second chances.", fg="white", bg="black")
        sub.pack(pady=6)

        btn_frame = tk.Frame(menu_container, bg="black")
        btn_frame.pack(pady=12)

        new_btn = tk.Button(btn_frame, text="New Game", width=20, command=self.start_new_game)
        new_btn.pack(pady=4)

        load_btn = tk.Button(btn_frame, text="View Endings", width=20, command=self.show_saved_endings)
        load_btn.pack(pady=4)

        credits_btn = tk.Button(btn_frame, text="Credits", width=20, command=self.show_credits)
        credits_btn.pack(pady=4)

        quit_btn = tk.Button(btn_frame, text="Quit", width=20, command=self.master.destroy)
        quit_btn.pack(pady=4)

        # Small hint about fullscreen
        hint = tk.Label(self.master, text="Press Escape to toggle fullscreen.", fg="gray", bg="black")
        hint.place(relx=0.5, rely=0.95, anchor='s')

        # Play main menu music if available and enabled (loop)
        try:
            if self.settings.get("enable_sound"):
                self.start_music('mainmenu.mp3', loop=True)
        except Exception:
            pass

    def start_new_game(self):
        # reset tracking
        # stop menu music if playing
        try:
            self.stop_music()
        except Exception:
            pass
        self.history = []
        self.stats = {"compassion": 0, "visibility": 0, "ambition": 0}
        # rebuild widgets and start at chapter 0
        for w in self.master.winfo_children():
            w.destroy()
        self.choice_buttons = []
        self.create_widgets()
        self.chapter = 0
        self.display_scene()
        self.update_hud()

    def toggle_fullscreen(self):
        try:
            self.fullscreen = not self.fullscreen
            self.master.attributes("-fullscreen", self.fullscreen)
        except Exception:
            pass

    def on_resize(self, event):
        # Responsive wraplength and font scaling
        try:
            w = max(self.master.winfo_width() - self.settings.get("wrap_margin", 80), 200)
            self.scene_label.configure(wraplength=w)
            # scale font by height
            h = self.master.winfo_height()
            base = max(12, int(h / 40))
            size = max(10, min(32, self.settings.get("font_size", self.font_size) + (base - 18)))
            self.default_font.configure(size=size)
        except Exception:
            pass

    def show_saved_endings(self):
        # Show saved endings in a simple window
        wins = tk.Toplevel(self.master)
        wins.title("Saved Endings")
        wins.configure(bg="black")
        txt = tk.Text(wins, width=80, height=20, bg="black", fg="white")
        txt.pack(padx=10, pady=10)
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                txt.insert(tk.END, f"Time: {entry.get('time')}\nEnding: {entry.get('ending_title')}\nSummary: {entry.get('ending_desc')}\nChoices: {entry.get('choices')}\n---\n")
        else:
            txt.insert(tk.END, "No saved endings yet.")
        # Make read-only
        txt.configure(state=tk.DISABLED)
        # also refresh HUD if open
        try:
            self.update_hud()
        except Exception:
            pass

    def show_credits(self):
        messagebox.showinfo("Credits", "Lost Skeleton\nDesign: You\nImplementation: helper script")

    # --- Settings persistence ---
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.settings.update(saved)
                # apply fullscreen preference if requested
                if self.settings.get("start_fullscreen"):
                    try:
                        self.master.attributes("-fullscreen", True)
                        self.fullscreen = True
                    except Exception:
                        self.fullscreen = False
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def open_settings(self):
        win = tk.Toplevel(self.master)
        win.title("Settings")
        win.configure(bg="black")

        # Font family
        tk.Label(win, text="Font family:", fg="white", bg="black").pack(anchor=tk.W, padx=8, pady=4)
        fam_var = tk.StringVar(value=self.settings.get("font_family"))
        fam_entry = tk.Entry(win, textvariable=fam_var)
        fam_entry.pack(fill=tk.X, padx=8)

        # Font size
        tk.Label(win, text="Base font size:", fg="white", bg="black").pack(anchor=tk.W, padx=8, pady=4)
        size_var = tk.IntVar(value=self.settings.get("font_size"))
        size_scale = tk.Scale(win, from_=10, to=32, orient=tk.HORIZONTAL, variable=size_var)
        size_scale.pack(fill=tk.X, padx=8)

        # Fullscreen toggle
        fs_var = tk.BooleanVar(value=self.settings.get("start_fullscreen", True))
        fs_cb = tk.Checkbutton(win, text="Start fullscreen", variable=fs_var, fg="white", bg="black", selectcolor="black")
        fs_cb.pack(anchor=tk.W, padx=8, pady=4)

        # Enable sound
        sound_var = tk.BooleanVar(value=self.settings.get("enable_sound", False))
        sound_cb = tk.Checkbutton(win, text="Enable sound playback", variable=sound_var, fg="white", bg="black", selectcolor="black")
        sound_cb.pack(anchor=tk.W, padx=8, pady=4)

        # Wrap margin
        tk.Label(win, text="Wrap margin (px):", fg="white", bg="black").pack(anchor=tk.W, padx=8, pady=4)
        wrap_var = tk.IntVar(value=self.settings.get("wrap_margin", 80))
        wrap_scale = tk.Scale(win, from_=40, to=300, orient=tk.HORIZONTAL, variable=wrap_var)
        wrap_scale.pack(fill=tk.X, padx=8)

        def apply_and_close():
            self.settings["font_family"] = fam_var.get()
            self.settings["font_size"] = int(size_var.get())
            self.settings["start_fullscreen"] = bool(fs_var.get())
            self.settings["enable_sound"] = bool(sound_var.get())
            self.settings["wrap_margin"] = int(wrap_var.get())
            # apply immediately
            try:
                self.default_font.configure(family=self.settings["font_family"], size=self.settings["font_size"])
            except Exception:
                pass
            if self.settings.get("start_fullscreen"):
                try:
                    self.master.attributes("-fullscreen", True)
                    self.fullscreen = True
                except Exception:
                    pass
            else:
                try:
                    self.master.attributes("-fullscreen", False)
                    self.fullscreen = False
                except Exception:
                    pass
            self.save_settings()
            win.destroy()

        apply_btn = tk.Button(win, text="Apply", command=apply_and_close)
        apply_btn.pack(pady=8)

    def display_scene(self):
        if not (0 <= int(self.chapter) < len(scene_data)):
            self.scene_text.set("The story has ended.")
            for b in self.choice_buttons:
                b.configure(text="", state=tk.DISABLED)
            self.progress_var.set(len(scene_data))
            return

        current = scene_data[int(self.chapter)]
        title = current.get("title")
        body = current.get("text", "")
        if title:
            display = f"{title}\n\n{body}"
        else:
            display = body

        self.scene_text.set(display)
        self.progress_var.set(min(int(self.chapter) + 1, len(scene_data)))

        choices = current.get("choices", [])
        for i, btn in enumerate(self.choice_buttons):
            if i < len(choices):
                btn.configure(text=choices[i], state=tk.NORMAL)
            else:
                btn.configure(text="", state=tk.DISABLED)
        # Update HUD to reflect current stats/history
        try:
            self.update_hud()
        except Exception:
            pass

    def process_choice(self, choice_index):
        if not (0 <= int(self.chapter) < len(scene_data)):
            messagebox.showinfo("Game Over", "The game has ended. Thanks for playing.")
            return

        current = scene_data[int(self.chapter)]
        choices = current.get("choices", [])
        if not choices:
            messagebox.showinfo("No choices", "There are no choices here.")
            return

        if not (0 <= choice_index < len(choices)):
            messagebox.showinfo("Invalid Choice", "Please select a valid option.")
            return

        next_map = current.get("next", [])
        try:
            next_idx = next_map[choice_index]
        except Exception:
            next_idx = None
        # Record the choice
        entry = {"scene_id": current.get("id"), "title": current.get("title"), "choice": choices[choice_index]}
        self.history.append(entry)

        # Apply effects if defined
        effects = current.get("effects", [])
        try:
            eff = effects[choice_index]
        except Exception:
            eff = {}
        if isinstance(eff, dict):
            for k, v in eff.items():
                self.stats[k] = self.stats.get(k, 0) + v

        # Special values: None -> Quit/End
        if next_idx is None:
            # compute ending and save
            ending_title, ending_desc = self.compute_ending()
            self.save_playthrough(ending_title, ending_desc)
            messagebox.showinfo(ending_title, ending_desc)
            # If the choice was Quit, close
            if choices[choice_index].lower() == "quit":
                self.quit_game()
            return

        # Valid next index: go there
        if isinstance(next_idx, int) and 0 <= next_idx < len(scene_data):
            self.chapter = next_idx
            # If the next scene has a soundtrack, show placeholder (play if available)
            sc = scene_data[self.chapter].get("soundtrack")
            if sc:
                self.play_sound(sc)
            self.display_scene()
            # If the scene is an end scene, finalize and save
            if scene_data[self.chapter].get("end"):
                ending_title, ending_desc = self.compute_ending()
                self.save_playthrough(ending_title, ending_desc)
                messagebox.showinfo(ending_title, ending_desc)
            return

        # Update HUD after making the choice
        try:
            self.update_hud()
        except Exception:
            pass

        messagebox.showinfo("Error", "Next scene is not available.")

    def compute_ending(self):
        # Determine ending based on highest stat and thresholds
        stats = self.stats
        # Determine primary stat
        primary = max(stats, key=lambda k: stats.get(k, 0))
        compassion = stats.get("compassion", 0)
        visibility = stats.get("visibility", 0)
        ambition = stats.get("ambition", 0)

        # Special flag checks
        tree_bless = stats.get("tree_blessing", 0)
        revealed = stats.get("revealed", 0)

        # Priority-based endings with lore combinations
        if tree_bless >= 1 and compassion >= 3:
            title = "Tree Keeper"
            desc = "You accepted a quiet covenant with the old tree. As Keeper, you steward memories and small rituals that bind the town together. The tree's blessing blooms in secret gardens and whispered traditions."
        elif revealed >= 1 and compassion >= 4:
            title = "Saint of the Square"
            desc = "You revealed yourself and taught by gentle example. The town honored you not only for spectacle but for the steadiness of your care. Your portrait hangs by the fountain; children learn your stories in school."
        elif compassion >= 6:
            title = "Guardian of Hope"
            desc = "You became a gentle legend — the unseen guardian whose small acts stitched the town together. Statues and murals celebrate the kindness that started as whispers. Your lore spreads: children leave tiny offerings at the fountain in thanks."
        elif revealed >= 1 and visibility >= 5:
            title = "Revealed Hero"
            desc = "You chose to be seen. When you revealed yourself, people recognized the heart beneath the bones. You became a teacher of compassion, inspiring civic movements and new friendships. Your story is sung at festivals."
        elif ambition >= 5:
            title = "Catalyst of Change"
            desc = "Your bold acts transformed the town's public life — murals, gardens, and organized charities bloom. You struck sparks that others fanned into movements. The legend of a skeleton who led change becomes a chapter in the town's history."
        elif compassion >= 3 and visibility >= 3:
            title = "Community Founder"
            desc = "A balance of kindness and being seen allowed you to found community projects that last. Benches, murals, and small guilds carry your name — humble monuments to steady care."
        elif tree_bless >= 1:
            title = "Silent Custodian"
            desc = "You accepted the tree's secret and tended it from the shadows. Few knew the role's fullness; those who did passed down your name like a warm ember."
        elif compassion >= 1:
            title = "Quiet Caretaker"
            desc = "You never sought fame. You kept helping in small ways until one day the town simply hummed with kindness. Your influence is subtle but deep; the neighborhood holds your memory like a steady light."
        else:
            title = "Fleeting Legend"
            desc = "Some stories shine briefly. You sparked moments that warmed a few, and those small sparks were enough. Your memory settles into the town like evening light."

        # Append some lore based on the combination
        # Append contextual lore reflecting choices and flags
        fragments = []
        fragments.append("Over decades the story grew: some say the old tree stores memories of every kindness.")
        if tree_bless >= 1:
            fragments.append("As Keeper, you stitched rituals into the calendar; offerings and small ceremonies keep the roots bright.")
        if revealed >= 1:
            fragments.append("Your reveal reshaped what people expect from legends — that being visible can also be kind.")
        if ambition >= 5:
            fragments.append("Your bold plans inspired civic change; new institutions rose from your daring.")

        lore = "\n\nLore: " + " ".join(fragments)
        return title, desc + lore

    def save_playthrough(self, ending_title, ending_desc):
        record = {
            "time": datetime.now().isoformat(),
            "ending_title": ending_title,
            "ending_desc": ending_desc,
            "stats": self.stats,
            "choices": self.history,
        }
        data = []
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
        data.append(record)
        with open(self.save_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def play_sound(self, filename):
        # Placeholder: playsound if available; otherwise no-op
        if not playsound:
            return
        path = os.path.join(os.path.dirname(__file__), "soundtracks", filename)
        if not os.path.exists(path):
            return
        def _play():
            try:
                playsound(path)
            except Exception:
                pass
        t = threading.Thread(target=_play, daemon=True)
        t.start()

    def start_music(self, filename, loop=False):
        """Start background music; if loop=True, repeatedly play until stopped."""
        # Stop existing music
        try:
            self.stop_music()
        except Exception:
            pass
        if not self.settings.get("enable_sound"):
            return
        if not playsound:
            return
        path = os.path.join(os.path.dirname(__file__), "soundtracks", filename)
        if not os.path.exists(path):
            return

        stop_evt = threading.Event()
        self._music_stop_event = stop_evt

        def _loopplay():
            try:
                while not stop_evt.is_set():
                    try:
                        playsound(path)
                    except Exception:
                        # if playsound raises, break to avoid spam
                        break
                    if not loop:
                        break
            finally:
                # clear references
                self._music_stop_event = None
                self._music_thread = None

        t = threading.Thread(target=_loopplay, daemon=True)
        self._music_thread = t
        t.start()

    def stop_music(self):
        try:
            if self._music_stop_event:
                self._music_stop_event.set()
            self._music_thread = None
            self._music_stop_event = None
        except Exception:
            pass

    # --- HUD helpers ---
    def update_hud(self):
        # Update stat labels
        for k, lbl in self.stat_labels.items():
            try:
                lbl.configure(text=str(self.stats.get(k, 0)))
            except Exception:
                pass
        # Update history listbox
        self.history_box.delete(0, tk.END)
        for i, h in enumerate(self.history, start=1):
            title = h.get("title") or ""
            choice = h.get("choice") or ""
            self.history_box.insert(tk.END, f"{i}. {title} — {choice}")

    def clear_history(self):
        self.history = []
        try:
            self.history_box.delete(0, tk.END)
        except Exception:
            pass

    def update_game_state(self, user_choice):
        # Not used in new structure, kept for backwards compatibility
        pass

    def restart_game(self):
        # Reset history and stats as a fresh restart
        self.history = []
        self.stats = {"compassion": 0, "visibility": 0, "ambition": 0}
        self.chapter = 0
        self.display_scene()
        try:
            self.update_hud()
        except Exception:
            pass

    def quit_game(self):
        messagebox.showinfo("Thanks for playing", "Goodbye.")
        try:
            self.stop_music()
        except Exception:
            pass
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = TextAdventureGame(root)
    root.mainloop()

