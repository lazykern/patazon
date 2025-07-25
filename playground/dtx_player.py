import os
import sys
import re
import time
import pygame


def base36_to_int(s):
    """Converts a base36 string (0-9, A-Z) to an integer."""
    try:
        return int(s, 36)
    except (ValueError, TypeError):
        return 0


class Dtx:
    """
    Parses a .dtx file, processes its metadata, and calculates the precise
    timing of all musical events, including notes and BPM changes.
    """

    # Channels that do not represent playable notes and should be ignored
    # when building the list of timed events. This includes visual and
    # system channels for things like bar lines and BGA control.
    NON_NOTE_CHANNELS = {
        # Visual Layers & Control
        "04", "07", "54", "5A", "C4", "C7",
        "55", "56", "57", "58", "59", "60",
        "D5", "D6", "D7", "D8", "D9", "DA", "DB", "DC", "DD", "DE", "DF",
        # System (Bar lines, visibility toggles, etc.)
        "50", "51", "C1", "C2",
        # Sound Effect (SE) channels - these are autoplay sounds, not playable notes.
        "61", "62", "63", "64", "65", "66", "67", "68", "69",
        "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
        "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
        "90", "91", "92",
    }

    def __init__(self, dtx_path):
        """
        Initializes the Dtx object with the path to the .dtx file.

        Args:
            dtx_path (str): The full path to the .dtx file.

        Raises:
            FileNotFoundError: If the .dtx file does not exist.
        """
        if not os.path.exists(dtx_path):
            raise FileNotFoundError(f"DTX file not found: {dtx_path}")
        self.dtx_path = dtx_path
        self.directory = os.path.dirname(dtx_path) or "."

        # Metadata with default values
        self.title = "Untitled"
        self.artist = "Unknown"
        self.bpm = 120.0

        # Resource definitions
        self.wav_files = {}  # Maps WAV ID (str) to its file path
        self.bpm_changes = {}  # Maps BPM ID (str) to a BPM value (float)
        self.bar_length_changes = {}  # Maps bar number to a length multiplier (float)
        self.wav_volumes = {}  # Maps WAV ID to volume (0-100) from #VOLUME
        self.bgm_wav_id = None
        self.bgm_start_time_ms = 0.0

        # The final calculated event list
        self.timed_notes = []  # List of (time_in_ms, wav_id_str)

    def _split_line(self, line):
        """
        Helper to robustly split a DTX command line into a key and value.
        Handles commands with and without values.
        """
        # Prioritize colon as it's a more definitive separator
        if ":" in line:
            key, value = line.split(":", 1)
            return key, value
        # Fallback to the first space for commands like '#BPM 120'
        elif " " in line:
            key, value = line.split(" ", 1)
            return key, value
        # Handle commands with no value, like '#END'
        return line, ""

    def parse(self):
        """
        Parses the DTX file in two main stages:
        1. First Pass: Gathers all definitions (metadata, WAVs, BPMs, bar lengths).
        2. Second Pass: Processes the timeline, calculating the precise time
           for each event based on the current BPM and bar lengths.
        """
        print(f"Parsing '{os.path.basename(self.dtx_path)}'...")

        raw_events = []

        # --- First Pass: Gather all definitions from the file ---
        # Try to read the file with multiple encodings and choose the one that
        # produces the most valid-looking DTX command lines (starting with '#').
        best_content = None
        best_encoding = None
        max_command_lines = 0

        # Common encodings for DTX files, with cp932 (Shift-JIS) often being correct.
        for encoding in ["cp932", "utf-16-le", "utf-8-sig", "utf-8"]:
            try:
                with open(self.dtx_path, "r", encoding=encoding) as f:
                    lines = f.readlines()

                # Heuristic: The correct encoding should yield many command lines.
                command_lines = sum(1 for line in lines if line.strip().startswith("#"))

                if command_lines > max_command_lines:
                    max_command_lines = command_lines
                    best_content = lines
                    best_encoding = encoding

            except (UnicodeDecodeError, UnicodeError):
                continue  # This encoding is incorrect, try the next one.
            except Exception as e:
                print(f"An unexpected error occurred while reading with {encoding}: {e}")

        if not best_content:
            print("Error: Could not read or decode the file with any supported encodings.")
            return

        content = best_content
        print(
            f"Successfully read file using encoding '{best_encoding}' ({max_command_lines} command lines found)."
        )

        for line in content:
            line = line.strip()
            if not line or not line.startswith("#"):
                continue

            raw_key, raw_value = self._split_line(line[1:])

            key = raw_key.strip().upper()
            value = raw_value.strip().split(";")[0].strip()  # Remove comments

            if key == "TITLE":
                self.title = value
            elif key == "ARTIST":
                self.artist = value
            elif key == "BPM" and value:
                try:
                    self.bpm = float(value)
                except ValueError:
                    print(f"Warning: Invalid BPM value '{value}'")
            elif key.startswith("WAV") and value:
                # Normalize path separators to handle DTX files from Windows
                normalized_value = value.replace("\\", "/")
                self.wav_files[key[3:]] = os.path.join(self.directory, normalized_value)
            elif key == "BGMWAV" and value:
                self.bgm_wav_id = value
            elif key.startswith("BPM") and len(key) > 3 and value:
                try:
                    self.bpm_changes[key[3:]] = float(value)
                except ValueError:
                    print(f"Warning: Invalid BPM change value '{value}'")
            elif key.startswith("VOLUME") and len(key) > 6 and value:
                wav_id = key[6:]
                try:
                    self.wav_volumes[wav_id] = int(value)
                except (ValueError, TypeError):
                    print(
                        f"Warning: Invalid VOLUME value '{value}' for WAV ID {wav_id}"
                    )
            # Check for note/event data lines (e.g., #00108: ...)
            elif len(key) == 5 and re.match(r"^\d{3}[0-9A-Z]{2}$", key):
                bar_num = int(key[0:3])
                channel = key[3:5]

                # Handle bar length changes, which are not standard chip events
                if channel == "02":
                    if value:
                        try:
                            # Bar length is a direct float value in the DTX file
                            self.bar_length_changes[bar_num] = float(value)
                        except (ValueError, TypeError):
                            print(
                                f"Warning: Invalid bar length value '{value}' for bar {bar_num}"
                            )
                    continue  # Do not process as a note event

                # Ignore other non-note channels (visual, system, etc.)
                if channel in self.NON_NOTE_CHANNELS:
                    continue

                if not value:
                    continue

                notes = [value[i : i + 2] for i in range(0, len(value), 2)]
                if not notes:
                    continue

                total_notes = len(notes)
                for i, note_val in enumerate(notes):
                    if note_val != "00":
                        raw_events.append(
                            {
                                "bar": bar_num,
                                "channel": channel,
                                "pos": i,
                                "total_pos": total_notes,
                                "val": note_val,
                            }
                        )

        # If BGMWAV is not specified, default to WAV01, a common convention
        if not self.bgm_wav_id and "01" in self.wav_files:
            self.bgm_wav_id = "01"

        print(
            f"Found {len(self.wav_files)} WAVs, {len(self.bar_length_changes)} bar length changes, and {len(raw_events)} raw events."
        )

        # --- Second Pass: Calculate event timings ---
        # Pre-calculate the starting beat of each bar to handle time signature changes
        max_bar = 0
        if raw_events:
            max_bar = max(e["bar"] for e in raw_events)

        bar_start_beats = {0: 0.0}
        for i in range(max_bar + 1):
            bar_length_multiplier = self.bar_length_changes.get(i, 1.0)
            beats_in_bar = 4.0 * bar_length_multiplier
            bar_start_beats[i + 1] = bar_start_beats[i] + beats_in_bar

        # Annotate each event with its precise global beat number
        for event in raw_events:
            bar_num = event["bar"]
            # Get the length of the specific bar the event is in
            bar_len_multiplier = self.bar_length_changes.get(bar_num, 1.0)
            beats_in_this_bar = 4.0 * bar_len_multiplier

            # Position within the bar (0.0 to 1.0) * beats in this bar
            event_beat_in_bar = (event["pos"] / event["total_pos"]) * beats_in_this_bar

            # Global beat is the sum of beats before this bar + beat pos in this bar
            event["global_beat"] = bar_start_beats[bar_num] + event_beat_in_bar

        # Sort events by their calculated global beat to process them chronologically
        raw_events.sort(key=lambda x: x["global_beat"])

        current_time_s = 0.0
        current_bpm = self.bpm
        last_event_beat = 0.0
        first_bgm_event_processed = False

        for event in raw_events:
            # Calculate time elapsed since the last event using the current BPM
            delta_beats = event["global_beat"] - last_event_beat
            delta_time_s = delta_beats * (60.0 / current_bpm)
            event_time_s = current_time_s + delta_time_s

            # Process the event based on its channel to see if it's a note or a BPM change
            channel, value = event["channel"], event["val"]

            if channel == "01":  # BGM event
                if not first_bgm_event_processed:
                    self.bgm_start_time_ms = event_time_s * 1000
                    first_bgm_event_processed = True
                # BGM events aren't notes, so we don't add them to the list.
            elif channel == "03":  # Direct BPM change (hexadecimal value)
                try:
                    current_bpm = float(int(value, 16))
                except (ValueError, TypeError):
                    print(f"Warning: Invalid direct BPM value '{value}'")
            elif channel == "08":  # BPM change from predefined list
                if value in self.bpm_changes:
                    current_bpm = self.bpm_changes[value]
            else:  # Any other channel is a note.
                self.timed_notes.append((event_time_s * 1000, channel, value))

            # Update state for the next iteration
            current_time_s = event_time_s
            last_event_beat = event["global_beat"]

        self.timed_notes.sort()
        print(f"Successfully parsed {len(self.timed_notes)} timed notes.")


class Player:
    """
    Uses Pygame to load and play the sounds from a parsed DTX object.
    Also handles the visual "note highway" representation of the song.
    """

    # --- Constants for Visualization ---
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    # New DTXMania-like layout constants
    NUM_LANES = 10
    LANE_WIDTH = 40
    NOTE_HIGHWAY_WIDTH = NUM_LANES * LANE_WIDTH
    NOTE_HIGHWAY_X_START = (SCREEN_WIDTH - NOTE_HIGHWAY_WIDTH) // 2

    JUDGMENT_LINE_Y = SCREEN_HEIGHT - 100
    NOTE_HIGHWAY_TOP_Y = 50
    SCROLL_TIME_MS = 1500  # Time in ms for a note to travel the highway
    PROGRESS_BAR_WIDTH = 20  # Vertical progress bar on the side
    JUMP_AMOUNT_S = 5.0  # Jump 5 seconds

    # Colors
    COLOR_BACKGROUND = (0, 0, 0)  # Black background like DTXMania
    COLOR_LANE_SEPARATOR = (50, 50, 50)
    COLOR_JUDGMENT_LINE = (255, 255, 255)
    COLOR_TEXT = (220, 220, 255)

    # --- Lane Configuration (DTXMania Style) ---
    # Defines the order and appearance of each drum lane from left to right.
    # The 'color' is used for the static lane indicators at the bottom.
    LANE_DEFINITIONS = [
        {"name": "L.Cym", "channels": ["1A"], "color": (255, 105, 180)},  # Hot Pink
        {"name": "H.H.", "channels": ["11", "18"], "color": (0, 180, 255)},  # Light Blue
        {"name": "Snare", "channels": ["12"], "color": (255, 0, 100)},  # Red/Pink
        {
            "name": "L.Foot",
            "channels": ["1B", "1C"],
            "color": (255, 255, 255),
        },  # White Indicator
        {"name": "H.Tom", "channels": ["14"], "color": (0, 220, 0)},  # Green
        {"name": "Kick", "channels": ["13"], "color": (255, 255, 255)},  # White Indicator
        {"name": "L.Tom", "channels": ["15"], "color": (255, 0, 0)},  # Red
        {"name": "F.Tom", "channels": ["17"], "color": (255, 165, 0)},  # Orange
        {"name": "R.Cym", "channels": ["16"], "color": (0, 180, 255)},  # Blue
        {"name": "Ride", "channels": ["19"], "color": (0, 180, 255)},  # Blue
    ]

    # Create a reverse map for quick channel-to-lane-index lookups.
    CHANNEL_TO_LANE_MAP = {
        channel_id: i
        for i, lane in enumerate(LANE_DEFINITIONS)
        for channel_id in lane["channels"]
    }

    # Define specific colors for certain note types within a lane (e.g., Open Hi-Hat).
    # This overrides the base note color.
    NOTE_TYPE_COLORS = {
        "18": (100, 220, 255),  # H.H. Open - Brighter cyan
        "1B": (255, 105, 180),  # H.H. Pedal - Hot Pink
        "13": (200, 0, 200),  # Main Kick - Purple
        "1C": (200, 0, 200),  # Left Kick - Purple
    }

    # --- Sound Mechanics Configuration ---
    # Polyphony: How many instances of a single sound can play at once.
    POLYPHONY_LIMIT = 4  # Similar to DTXMania's default

    # Choke Map: Defines which sounds stop which other sounds.
    # Key: The sound that triggers the choke (the "choker").
    # Value: A list of sounds that get stopped (the "choked").
    CHOKE_MAP = {
        "11": ["18"],  # Closed HH chokes Open HH
        "1B": ["18"],  # Pedal HH chokes Open HH
    }

    def __init__(self, dtx_data):
        self.dtx = dtx_data
        self.sounds = {}
        self.bgm_path = None  # Will store the path to the BGM file
        self.hit_animations = []  # Stores recent note hits for visual feedback

        # --- Audio State Management ---
        # For polyphony: Stores active channels for each instrument lane.
        # Structure: { channel_id: [ (channel_object, play_time_ms), ... ] }
        self.active_poly_sounds = {}

        # For choke logic: Stores the active channel for chokeable sounds.
        # Structure: { channel_id: channel_object }
        self.active_choke_sounds = {}
        # Pre-calculate which channels can BE choked for faster lookups.
        self.CHOKEABLE_CHANNELS = list(
            set(
                choked
                for choker, choked_list in self.CHOKE_MAP.items()
                for choked in choked_list
            )
        )

        self.time_offset_ms = 0  # Stores seek position for audio-driven clock
        self.bgm_volume = 0.7  # Default BGM volume, adjustable with Up/Down keys
        self.se_volume = (
            1.0  # Default Sound Effect volume, adjustable with PageUp/PageDown
        )
        # Fade envelope settings (ms)
        self.se_fade_in_ms = 10  # gentle attack for each drum hit
        self.se_fade_out_ms = 100  # quick release when choked
        self.bgm_fade_ms = 400  # fade-in/out time for BGM on start/seek

        # --- Fonts (initialized in play method) ---
        self.font = None
        self.small_font = None

        print("\nInitializing Pygame audio...")
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        # Allocate more channels for complex drum patterns
        pygame.mixer.set_num_channels(64)
        print("Pygame audio initialized.")

    def load_sounds(self):
        """Loads all audio files defined in the DTX data into memory."""
        print("Loading audio files...")
        loaded_count = 0
        for wav_id, path in self.dtx.wav_files.items():
            if not os.path.exists(path):
                print(f"Warning: Audio file not found for WAV ID {wav_id}: {path}")
                continue

            # Separate BGM from other sound effects
            if wav_id == self.dtx.bgm_wav_id:
                self.bgm_path = path
                continue  # Don't load BGM as a normal sound

            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[wav_id] = sound
                loaded_count += 1
            except pygame.error as e:
                print(f"Warning: Could not load '{os.path.basename(path)}'. Error: {e}")

        if self.bgm_path:
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(self.bgm_volume)
                print(f"BGM loaded. Volume set to {self.bgm_volume * 100:.0f}%.")
            except pygame.error as e:
                print(
                    f"Warning: Could not load BGM '{os.path.basename(self.bgm_path)}'. Error: {e}"
                )
                self.bgm_path = None

        print(
            f"{len(self.sounds)} sound effects loaded (out of {len(self.dtx.wav_files)} defined)."
        )

    def _draw_lane_indicators(self, screen):
        """Draws colored indicators for each lane below the judgment line."""
        indicator_y = self.JUDGMENT_LINE_Y + 5
        indicator_height = 15

        for i, lane_def in enumerate(self.LANE_DEFINITIONS):
            x_pos = self.NOTE_HIGHWAY_X_START + i * self.LANE_WIDTH
            color = lane_def["color"]

            indicator_rect = pygame.Rect(
                x_pos + 2, indicator_y, self.LANE_WIDTH - 4, indicator_height
            )
            pygame.draw.rect(screen, color, indicator_rect)

    def _draw_lanes_and_judgment_line(self, screen):
        """Draws the static parts of the note highway."""
        # Draw vertical lane separators for the new layout
        for i in range(self.NUM_LANES + 1):
            x = self.NOTE_HIGHWAY_X_START + i * self.LANE_WIDTH
            start_pos = (x, self.NOTE_HIGHWAY_TOP_Y)
            end_pos = (x, self.JUDGMENT_LINE_Y)
            pygame.draw.line(screen, self.COLOR_LANE_SEPARATOR, start_pos, end_pos, 1)

        # Draw judgment line across the new highway width
        start_x = self.NOTE_HIGHWAY_X_START
        end_x = self.NOTE_HIGHWAY_X_START + self.NOTE_HIGHWAY_WIDTH
        pygame.draw.line(
            screen,
            self.COLOR_JUDGMENT_LINE,
            (start_x, self.JUDGMENT_LINE_Y),
            (end_x, self.JUDGMENT_LINE_Y),
            3,
        )

    def _draw_notes(self, screen, current_time_ms, notes_to_play, note_index):
        """Draws all the notes currently visible on the highway."""
        highway_height = self.JUDGMENT_LINE_Y - self.NOTE_HIGHWAY_TOP_Y

        # Iterate from the next note to be played onwards
        for i in range(note_index, len(notes_to_play)):
            note_time, channel_id, _ = notes_to_play[i]

            time_until_hit = note_time - current_time_ms

            # Stop drawing notes that are too far in the future
            if time_until_hit > self.SCROLL_TIME_MS:
                break

            # Only draw notes that are currently on screen
            if time_until_hit >= 0:
                progress = 1.0 - (time_until_hit / self.SCROLL_TIME_MS)
                y_pos = self.NOTE_HIGHWAY_TOP_Y + (progress * highway_height)

                # Draw notes in their respective lanes using the new layout
                if channel_id in self.CHANNEL_TO_LANE_MAP:
                    lane_index = self.CHANNEL_TO_LANE_MAP[channel_id]
                    lane_def = self.LANE_DEFINITIONS[lane_index]

                    # Get color from the lane definition, allowing for overrides for special notes.
                    color = self.NOTE_TYPE_COLORS.get(channel_id, lane_def["color"])

                    x_pos = self.NOTE_HIGHWAY_X_START + lane_index * self.LANE_WIDTH
                    note_rect = pygame.Rect(
                        x_pos + 2, y_pos - 3, self.LANE_WIDTH - 4, 7
                    )

                    # --- Special Hi-Hat Visuals ---
                    if channel_id == "18":  # Open Hi-Hat
                        # Draw as a hollow rectangle to signify "open"
                        pygame.draw.rect(screen, color, note_rect, 2)
                    elif channel_id == "1B":  # Pedal Hi-Hat
                        # Draw as a smaller, thinner bar to distinguish it
                        pedal_rect = pygame.Rect(
                            x_pos + 2, y_pos - 1, self.LANE_WIDTH - 4, 3
                        )
                        pygame.draw.rect(screen, color, pedal_rect)
                    else:  # All other notes
                        pygame.draw.rect(screen, color, note_rect)

    def _draw_hit_animations(self, screen, current_time_ms):
        """Draws a visual indicator when a note is hit."""
        ANIMATION_DURATION_MS = 80
        # Iterate over a copy, as we might remove items
        for anim in self.hit_animations[:]:
            if current_time_ms - anim["time"] > ANIMATION_DURATION_MS:
                self.hit_animations.remove(anim)
                continue

            channel_id = anim["channel_id"]
            # Use the new lane mapping to draw hit flashes
            if channel_id in self.CHANNEL_TO_LANE_MAP:
                lane_index = self.CHANNEL_TO_LANE_MAP[channel_id]
                lane_def = self.LANE_DEFINITIONS[lane_index]

                # Brighten the note's actual color for the animation flash.
                # This ensures special notes (like open HH) have the right color flash.
                note_color = self.NOTE_TYPE_COLORS.get(channel_id, lane_def["color"])
                color = tuple(min(c + 80, 255) for c in note_color)

                x_pos = self.NOTE_HIGHWAY_X_START + lane_index * self.LANE_WIDTH
                rect = pygame.Rect(
                    x_pos, self.JUDGMENT_LINE_Y - 50, self.LANE_WIDTH, 50
                )
                pygame.draw.rect(screen, color, rect)

                # Add text for special hi-hats to make hits clearer
                hit_text = None
                if channel_id == "18":
                    hit_text = "OPEN"
                elif channel_id == "1B":
                    hit_text = "PEDAL"

                if hit_text and self.small_font:
                    surface = self.small_font.render(
                        hit_text, True, self.COLOR_BACKGROUND
                    )
                    text_rect = surface.get_rect(center=rect.center)
                    screen.blit(surface, text_rect)

    def play(self):
        """Starts the main playback loop."""
        if not self.sounds and not self.bgm_path:
            print("No sounds were loaded. Nothing to play.")
            return

        notes_to_play = self.dtx.timed_notes[:]
        note_index = 0
        # The time offset is used to sync the chart's timeline with the
        # audio playback timeline. It's initialized with the BGM's start time.
        self.time_offset_ms = self.dtx.bgm_start_time_ms

        screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(f"Playing: {self.dtx.title} - {self.dtx.artist}")
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)

        # Calculate total song duration for progress bar
        song_duration_ms = 0
        if notes_to_play:
            song_duration_ms = notes_to_play[-1][0] + 3000  # Add 3s padding

        clock = pygame.time.Clock()

        print("\n--- Starting Playback ---")
        print("Press ESC to quit. Use Left/Right arrows to seek.")
        print("Use Up/Down for BGM volume. Use PageUp/PageDown for SE volume.")

        # --- Clock Initialization ---
        # The master clock is driven by the BGM audio position for perfect sync.
        # If no BGM is available, it falls back to the system's high-res timer.
        clock_is_audio_driven = False
        if self.bgm_path:
            try:
                pygame.mixer.music.play(fade_ms=self.bgm_fade_ms)
                clock_is_audio_driven = True
                print("Playback clock is audio-driven (BGM position).")
            except pygame.error as e:
                print(
                    f"Warning: Could not play BGM. Falling back to system clock. Error: {e}"
                )

        if not clock_is_audio_driven:
            print("Playback clock is system-driven.")

        start_ticks = pygame.time.get_ticks()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

                # --- Volume and Seek functionality ---
                if event.type == pygame.KEYDOWN:
                    # BGM Volume control
                    if event.key == pygame.K_UP:
                        self.bgm_volume = min(1.0, self.bgm_volume + 0.1)
                        if self.bgm_path:
                            pygame.mixer.music.set_volume(self.bgm_volume)
                    elif event.key == pygame.K_DOWN:
                        self.bgm_volume = max(0.0, self.bgm_volume - 0.1)
                        if self.bgm_path:
                            pygame.mixer.music.set_volume(self.bgm_volume)
                    # SE Volume Control
                    elif event.key == pygame.K_PAGEUP:
                        self.se_volume = min(1.0, self.se_volume + 0.1)
                    elif event.key == pygame.K_PAGEDOWN:
                        self.se_volume = max(0.0, self.se_volume - 0.1)

                    # Get current time before calculating jump
                    if clock_is_audio_driven and pygame.mixer.music.get_busy():
                        current_time_ms = (
                            pygame.mixer.music.get_pos() + self.time_offset_ms
                        )
                    else:
                        current_time_ms = pygame.time.get_ticks() - start_ticks

                    new_time_ms = -1

                    if event.key == pygame.K_RIGHT:
                        new_time_ms = current_time_ms + (self.JUMP_AMOUNT_S * 1000)
                    elif event.key == pygame.K_LEFT:
                        new_time_ms = current_time_ms - (self.JUMP_AMOUNT_S * 1000)

                    if new_time_ms != -1:
                        # Clamp the new time within song bounds
                        new_time_ms = max(0, new_time_ms)
                        if song_duration_ms > 0:
                            new_time_ms = min(new_time_ms, song_duration_ms)

                        # Update the reference for the system clock fallback
                        start_ticks = pygame.time.get_ticks() - new_time_ms

                        # Resync the BGM by restarting it at the new position
                        if clock_is_audio_driven:
                            # gentle fade-out before repositioning
                            pygame.mixer.music.fadeout(self.bgm_fade_ms)
                            self.time_offset_ms = new_time_ms

                            # Calculate the correct starting position within the BGM file
                            # by subtracting the initial BGM offset from the target chart time.
                            music_start_pos_ms = new_time_ms - self.dtx.bgm_start_time_ms
                            music_start_pos_s = max(0, music_start_pos_ms / 1000.0)

                            pygame.mixer.music.play(
                                start=music_start_pos_s, fade_ms=self.bgm_fade_ms
                            )

                        # Find the new note index
                        note_index = 0
                        for i, note in enumerate(notes_to_play):
                            if note[0] >= new_time_ms:
                                note_index = i
                                break
                        else:  # Jumped past the last note
                            note_index = len(notes_to_play)

                        # Stop all currently playing sounds when seeking
                        pygame.mixer.stop()
                        self.active_poly_sounds.clear()
                        self.active_choke_sounds.clear()

                        # Clear old hit animations
                        self.hit_animations.clear()

            # --- Update Master Clock ---
            if clock_is_audio_driven and pygame.mixer.music.get_busy():
                current_time_ms = pygame.mixer.music.get_pos() + self.time_offset_ms
            else:
                # If BGM ends or wasn't there, rely on the system clock
                if clock_is_audio_driven:  # Just transitioned from audio to system
                    print("BGM finished. Switching to system clock.")
                    clock_is_audio_driven = False
                    # Resync system clock to the BGM's last known position
                    start_ticks = pygame.time.get_ticks() - song_duration_ms

                current_time_ms = pygame.time.get_ticks() - start_ticks

            # Trigger notes that are due
            while (
                note_index < len(notes_to_play)
                and notes_to_play[note_index][0] <= current_time_ms
            ):
                _, channel_id, wav_id = notes_to_play[note_index]
                if wav_id in self.sounds:
                    sound_to_play = self.sounds[wav_id]

                    # 1. --- Choke Logic ---
                    # If this note is a "choker", stop any corresponding "choked" sounds.
                    if channel_id in self.CHOKE_MAP:
                        for choked_channel_id in self.CHOKE_MAP[channel_id]:
                            if choked_channel_id in self.active_choke_sounds:
                                channel_to_stop = self.active_choke_sounds[
                                    choked_channel_id
                                ]
                                if channel_to_stop and channel_to_stop.get_busy():
                                    channel_to_stop.fadeout(self.se_fade_out_ms)
                                # Remove it from tracking since it's now choked
                                del self.active_choke_sounds[choked_channel_id]

                    # 2. --- Polyphony & Playback Logic ---
                    # This logic now operates per channel, not per sound file.
                    # Initialize a list for this channel if it's the first time we've seen it.
                    if channel_id not in self.active_poly_sounds:
                        self.active_poly_sounds[channel_id] = []

                    # Get the list of currently playing instances for this specific channel.
                    playing_instances = self.active_poly_sounds[channel_id]

                    # Clean up any sounds in the list that have finished playing naturally.
                    playing_instances = [
                        item for item in playing_instances if item[0].get_busy()
                    ]

                    # Voice stealing: If we're at the polyphony limit, stop the oldest sound.
                    if len(playing_instances) >= self.POLYPHONY_LIMIT:
                        # Sort by play time to find the oldest sound.
                        playing_instances.sort(key=lambda x: x[1])
                        # Get the channel of the oldest sound and remove it from our tracking list.
                        oldest_channel, _ = playing_instances.pop(0)
                        # Fade it out to free up a mixer channel.
                        oldest_channel.fadeout(self.se_fade_out_ms)

                    # Play the new sound with a gentle fade-in.
                    # The final volume combines the master SE volume and the per-WAV volume from the chart.
                    wav_vol_percent = self.dtx.wav_volumes.get(wav_id, 100)
                    note_vol_multiplier = wav_vol_percent / 100.0
                    final_volume = self.se_volume * note_vol_multiplier

                    # Set the volume on the Sound object itself right before playing.
                    # This ensures the fade-in targets the correct final volume.
                    sound_to_play.set_volume(final_volume)
                    new_channel = sound_to_play.play(fade_ms=self.se_fade_in_ms)

                    if new_channel:
                        # The volume is now set on the Sound, so this is no longer needed.
                        # new_channel.set_volume(final_volume)

                        # Add the new sound to our polyphony tracking list.
                        playing_instances.append((new_channel, current_time_ms))

                        # If this sound is one that can BE choked (e.g., an open hi-hat),
                        # track its channel so a future "choker" can stop it.
                        if channel_id in self.CHOKEABLE_CHANNELS:
                            self.active_choke_sounds[channel_id] = new_channel

                    # Update the master list of active sounds.
                    self.active_poly_sounds[channel_id] = playing_instances

                    # Add an animation for visual feedback
                    self.hit_animations.append(
                        {"channel_id": channel_id, "time": current_time_ms}
                    )
                note_index += 1

            # Check if playback is finished
            bgm_playing = pygame.mixer.music.get_busy()
            if note_index >= len(notes_to_play) and not bgm_playing:
                print("Playback finished.")
                time.sleep(2)
                running = False

            # --- Render status to the screen ---
            screen.fill(self.COLOR_BACKGROUND)

            # Draw the highway and notes
            self._draw_lanes_and_judgment_line(screen)
            self._draw_lane_indicators(screen)
            self._draw_notes(screen, current_time_ms, notes_to_play, note_index)
            self._draw_hit_animations(screen, current_time_ms)

            # --- Draw Progress Bar (DTXMania style on the right) ---
            if song_duration_ms > 0:
                progress_bar_x = (
                    self.NOTE_HIGHWAY_X_START + self.NOTE_HIGHWAY_WIDTH + 10
                )
                progress_bar_height = self.JUDGMENT_LINE_Y - self.NOTE_HIGHWAY_TOP_Y

                # Background of the progress bar
                bg_rect = pygame.Rect(
                    progress_bar_x,
                    self.NOTE_HIGHWAY_TOP_Y,
                    self.PROGRESS_BAR_WIDTH,
                    progress_bar_height,
                )
                pygame.draw.rect(screen, self.COLOR_LANE_SEPARATOR, bg_rect)

                # Filled part of the progress bar (grows upwards)
                progress = current_time_ms / song_duration_ms
                fill_height = progress * progress_bar_height
                fill_rect = pygame.Rect(
                    progress_bar_x,
                    self.JUDGMENT_LINE_Y - fill_height,
                    self.PROGRESS_BAR_WIDTH,
                    fill_height,
                )

                # Use a distinct color for the progress bar fill
                progress_color = (180, 180, 40)  # A gold-like color
                pygame.draw.rect(screen, progress_color, fill_rect)

            info_texts = [
                f"Time: {current_time_ms / 1000.0:.2f}s / {song_duration_ms / 1000.0:.2f}s",
                f"Notes Played: {note_index} / {len(notes_to_play)}",
                f"BPM: {self.dtx.bpm:.2f}",  # Note: This shows initial BPM only
                f"BGM Volume: {self.bgm_volume * 100:.0f}% (Up/Down)",
                f"SE Volume: {self.se_volume * 100:.0f}% (PgUp/PgDn)",
                "Seek: Left/Right Arrows | Quit: ESC",
            ]

            for i, text in enumerate(info_texts):
                surface = self.font.render(text, True, self.COLOR_TEXT)
                screen.blit(surface, (10, 10 + i * 30))

            pygame.display.flip()
            clock.tick(240)  # Use a high tick rate for accurate timing

        pygame.quit()
        print("Player has shut down.")


def main():
    """Main function to run the DTX player from the command line."""
    if len(sys.argv) < 2:
        print("Usage: python dtx_player.py <path_to_dtx_file>")
        sys.exit(1)

    dtx_file_path = sys.argv[1]

    try:
        dtx_data = Dtx(dtx_file_path)
        dtx_data.parse()

        player = Player(dtx_data)
        player.load_sounds()
        player.play()

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
