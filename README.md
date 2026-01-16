# Lost Skeleton

A small, branching text-adventure built with Python and Tkinter.

## Overview

You play as Lucas — a mysterious helper in a small town. Your choices change stats (Compassion, Visibility, Ambition) and lead to different endings. The game is designed to be run locally with optional soundtrack playback.

## Requirements

- Python 3.8+ (Tkinter must be available)
- Optional: `playsound` or `pygame` for audio playback

Install an audio library (optional):

```bash
pip install playsound
# or
pip install pygame
```

## Running

From the project root (same folder as `skeleton.py`):

```bash
python skeleton.py
```

- The game starts fullscreen by default (press `Escape` to toggle).
- Use the Main Menu to start a new game, view saved endings, or open Settings.

## Soundtracks

Place audio files in a `soundtracks/` folder alongside `skeleton.py` (project root).

Example structure:

```
Lost_Skeleton_alpha/
	skeleton.py
	README.md
	soundtracks/
		prologue_theme.mp3
		square_loop.mp3
		mystic_tree.mp3
		transformation_swirl.mp3
		kindness_loop.mp3
		mural_finale.mp3
		reveal_theme.mp3
		tree_blessing.mp3
```

If the filename in `scene_data` matches a file in `soundtracks/` and you enable sound in Settings, the game will attempt to play it.

## Settings

Open `Settings` in-game to adjust font, wrap margin, fullscreen start preference, and enable/disable sound. Settings are saved to `settings.json` in the same folder as `skeleton.py`.

## Save Files

- `endings.json` — appended playthroughs and computed endings (time, stats, choices).
- `settings.json` — user preferences saved by the game.

## Editing Scenes and Assets

Scenes are defined in `scene_data` inside `skeleton.py`. Each scene includes `id`, `title`, `text`, `choices`, `next`, optional `effects`, optional `soundtrack`, and optional `end` flag.

- `next` values map choices to scene `id` indices (use `None` to end the game).
- `effects` are dicts that change stats (e.g., `{"compassion": 2}`) or set flags like `"tree_blessing": 1`.

To add or rename sound files, update the `soundtrack` field in a scene and place the matching file in `soundtracks/`.

## Extending the Game

Ideas:
- Add more branching scenes and endings.
- Ship a set of sample audio tracks in `soundtracks/`.
- Add volume controls or richer audio handling via `pygame`.
- Polish UI colors, icons and animations.

## Visual Assets (Images & Sprites)

Place visual assets in an `assets/` or `images/` folder next to `skeleton.py`. Recommended structure:

```
Lost_Skeleton_alpha/
	assets/
		mainmenu_bg.png       # main menu background (PNG recommended)
		logo.png              # optional logo for title
		hud_icons/            # small icons for HUD (heart, eye, star)
		portraits/            # character portraits (PNG, 256x256 or similar)
		sprites/              # small sprites for decorations (festival, mural pieces)
```

Where to use visuals in the game:
- Main Menu background and logo (`assets/mainmenu_bg.png`, `assets/logo.png`).
- Scene backdrops: per-scene background images to set mood (e.g. `assets/backdrops/tree.png`).
- HUD icons: replace text labels with small images for `compassion`, `visibility`, `ambition`.
- Choice buttons: small icon markers or portrait thumbnails beside choices.
- Endings screens: larger images or mural textures for finale scenes.
- Decorative sprites: festival banners, mural fragments, or particle overlays to enhance important scenes.

Implementation notes:
- The game will attempt to load `assets/mainmenu_bg.png` (or JPG) automatically for the main menu if present.
- Use PNG for transparency and better quality; keep sizes reasonable (desktop-sized backgrounds can be scaled at runtime).
- For JPEG support and image resizing the game will use Pillow (`pip install pillow`) if available; otherwise use PNG with `tk.PhotoImage`.


## Troubleshooting

- If the GUI does not open, confirm Tkinter is installed with your Python distribution.
- If audio does not play, ensure `enable_sound` is checked in Settings and the referenced files exist.
