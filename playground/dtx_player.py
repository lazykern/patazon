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
        self.directory = os.path.dirname(dtx_path) or '.'
        
        # Metadata with default values
        self.title = "Untitled"
        self.artist = "Unknown"
        self.bpm = 120.0
        
        # Resource definitions
        self.wav_files = {}  # Maps WAV ID (str) to its file path
        self.bpm_changes = {} # Maps BPM ID (str) to a BPM value (float)
        self.bar_length_changes = {} # Maps bar number to a length multiplier (float)
        self.wav_volumes = {} # Maps WAV ID to volume (0-100) from #WAVVOL
        self.bgm_wav_id = None
        
        # The final calculated event list
        self.timed_notes = [] # List of (time_in_ms, wav_id_str)

    def _split_line(self, line):
        """
        Helper to robustly split a DTX command line into a key and value.
        Handles commands with and without values.
        """
        # Prioritize colon as it's a more definitive separator
        if ':' in line:
            key, value = line.split(':', 1)
            return key, value
        # Fallback to the first space for commands like '#BPM 120'
        elif ' ' in line:
            key, value = line.split(' ', 1)
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
        content = []
        # Try multiple encodings, with Shift-JIS (cp932) being common for DTX files.
        for encoding in ['utf-16-le', 'cp932', 'utf-8-sig', 'utf-8']:
            try:
                with open(self.dtx_path, 'r', encoding=encoding) as f:
                    content = f.readlines()
                print(f"Successfully read file with encoding: {encoding}")
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                print(f"Error reading file with {encoding}: {e}")

        if not content:
            print(f"Error: Could not read file with any of the attempted encodings.")
            return

        for line in content:
            line = line.strip()
            if not line or not line.startswith('#'):
                continue

            raw_key, raw_value = self._split_line(line[1:])
            
            key = raw_key.strip().upper()
            value = raw_value.strip().split(';')[0].strip() # Remove comments

            if key == 'TITLE': self.title = value
            elif key == 'ARTIST': self.artist = value
            elif key == 'BPM' and value:
                try: self.bpm = float(value)
                except ValueError: print(f"Warning: Invalid BPM value '{value}'")
            elif key.startswith('WAV') and value:
                self.wav_files[key[3:]] = os.path.join(self.directory, value)
            elif key == 'BGMWAV' and value:
                self.bgm_wav_id = value
            elif key.startswith('BPM') and len(key) > 3 and value:
                try: self.bpm_changes[key[3:]] = float(value)
                except ValueError: print(f"Warning: Invalid BPM change value '{value}'")
            elif key.startswith('WAVVOL') and len(key) > 6 and value:
                wav_id = key[6:]
                try:
                    self.wav_volumes[wav_id] = int(value)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid WAVVOL value '{value}' for WAV ID {wav_id}")
            # Check for note/event data lines (e.g., #00108: ...)
            elif len(key) == 5 and re.match(r'^\d{3}[0-9A-Z]{2}$', key):
                bar_num = int(key[0:3])
                channel = key[3:5]

                # Handle bar length changes, which are not standard chip events
                if channel == '02':
                    if value:
                        try:
                            # Bar length is a direct float value in the DTX file
                            self.bar_length_changes[bar_num] = float(value)
                        except (ValueError, TypeError):
                            print(f"Warning: Invalid bar length value '{value}' for bar {bar_num}")
                    continue # Do not process as a note event
                
                if not value:
                    continue

                notes = [value[i:i+2] for i in range(0, len(value), 2)]
                if not notes: continue
                
                total_notes = len(notes)
                for i, note_val in enumerate(notes):
                    if note_val != '00':
                        raw_events.append({
                            'bar': bar_num, 'channel': channel, 'pos': i,
                            'total_pos': total_notes, 'val': note_val
                        })
        
        # If BGMWAV is not specified, default to WAV01, a common convention
        if not self.bgm_wav_id and '01' in self.wav_files:
             self.bgm_wav_id = '01'

        print(f"Found {len(self.wav_files)} WAVs, {len(self.bar_length_changes)} bar length changes, and {len(raw_events)} raw events.")

        # --- Second Pass: Calculate event timings ---
        # Pre-calculate the starting beat of each bar to handle time signature changes
        max_bar = 0
        if raw_events:
            max_bar = max(e['bar'] for e in raw_events)
        
        bar_start_beats = {0: 0.0}
        for i in range(max_bar + 1):
            bar_length_multiplier = self.bar_length_changes.get(i, 1.0)
            beats_in_bar = 4.0 * bar_length_multiplier
            bar_start_beats[i + 1] = bar_start_beats[i] + beats_in_bar

        # Annotate each event with its precise global beat number
        for event in raw_events:
            bar_num = event['bar']
            # Get the length of the specific bar the event is in
            bar_len_multiplier = self.bar_length_changes.get(bar_num, 1.0)
            beats_in_this_bar = 4.0 * bar_len_multiplier
            
            # Position within the bar (0.0 to 1.0) * beats in this bar
            event_beat_in_bar = (event['pos'] / event['total_pos']) * beats_in_this_bar
            
            # Global beat is the sum of beats before this bar + beat pos in this bar
            event['global_beat'] = bar_start_beats[bar_num] + event_beat_in_bar

        # Sort events by their calculated global beat to process them chronologically
        raw_events.sort(key=lambda x: x['global_beat'])
        
        current_time_s = 0.0
        current_bpm = self.bpm
        last_event_beat = 0.0

        for event in raw_events:
            # Calculate time elapsed since the last event using the current BPM
            delta_beats = event['global_beat'] - last_event_beat
            delta_time_s = delta_beats * (60.0 / current_bpm)
            event_time_s = current_time_s + delta_time_s

            # Process the event based on its channel to see if it's a note or a BPM change
            channel, value = event['channel'], event['val']
            
            if channel == '03': # Direct BPM change (hexadecimal value)
                try:
                    current_bpm = float(int(value, 16))
                except (ValueError, TypeError):
                    print(f"Warning: Invalid direct BPM value '{value}'")
            elif channel == '08': # BPM change from predefined list
                if value in self.bpm_changes:
                    current_bpm = self.bpm_changes[value]
            elif channel != '01': # Any other channel is a note (channel 01 is BGM)
                self.timed_notes.append((event_time_s * 1000, channel, value))

            # Update state for the next iteration
            current_time_s = event_time_s
            last_event_beat = event['global_beat']
        
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
    LANE_WIDTH = 60
    JUDGMENT_LINE_Y = SCREEN_HEIGHT - 100
    NOTE_HIGHWAY_TOP_Y = 50
    SCROLL_TIME_MS = 1500 # Time in ms for a note to travel the highway
    PROGRESS_BAR_HEIGHT = 10
    JUMP_AMOUNT_S = 5.0 # Jump 5 seconds

    # Colors
    COLOR_BACKGROUND = (20, 20, 40)
    COLOR_LANE_SEPARATOR = (50, 50, 80)
    COLOR_JUDGMENT_LINE = (255, 255, 255)
    COLOR_TEXT = (220, 220, 255)
    
    # --- Lane Configuration ---
    # Maps DTX channel ID to (x_center, color, name)
    LANES_CONFIG = {
        '16': (SCREEN_WIDTH * 0.2, (220, 220, 0), "L.Cym"),  # Left Cymbal
        '11': (SCREEN_WIDTH * 0.3, (0, 200, 200), "H.H."),  # Hi-Hat Closed
        '18': (SCREEN_WIDTH * 0.3, (0, 255, 255), "H.H. Open"),
        '1B': (SCREEN_WIDTH * 0.3, (0, 150, 150), "H.H. Pedal"),
        '12': (SCREEN_WIDTH * 0.4, (255, 80, 80), "Snare"),
        '14': (SCREEN_WIDTH * 0.5, (80, 255, 80), "H.Tom"),
        '17': (SCREEN_WIDTH * 0.6, (80, 80, 255), "F.Tom"),
        '19': (SCREEN_WIDTH * 0.7, (220, 0, 220), "Ride"),
        '1A': (SCREEN_WIDTH * 0.8, (220, 220, 0), "R.Cym"), # Right Cymbal
    }
    KICK_CHANNEL = '13'
    KICK_COLOR = (255, 128, 0)
    
    # --- Sound Mechanics Configuration ---
    # Polyphony: How many instances of a single sound can play at once.
    POLYPHONY_LIMIT = 4 # Similar to DTXMania's default

    # Choke Map: Defines which sounds stop which other sounds.
    # Key: The sound that triggers the choke (the "choker").
    # Value: A list of sounds that get stopped (the "choked").
    CHOKE_MAP = {
        '11': ['18'],  # Closed HH chokes Open HH
        '1B': ['18'],  # Pedal HH chokes Open HH
    }
    
    def __init__(self, dtx_data):
        self.dtx = dtx_data
        self.sounds = {}
        self.bgm_path = None # Will store the path to the BGM file
        self.hit_animations = [] # Stores recent note hits for visual feedback
        
        # --- Audio State Management ---
        # For polyphony: Stores active channels for each sound file (wav_id).
        # Structure: { wav_id: [ (channel_object, play_time_ms), ... ] }
        self.active_poly_sounds = {}
        
        # For choke logic: Stores the active channel for chokeable sounds.
        # Structure: { channel_id: channel_object }
        self.active_choke_sounds = {}
        # Pre-calculate which channels can BE choked for faster lookups.
        self.CHOKEABLE_CHANNELS = list(set(
            choked for choker, choked_list in self.CHOKE_MAP.items() 
            for choked in choked_list
        ))

        self.time_offset_ms = 0 # Stores seek position for audio-driven clock
        self.bgm_volume = 0.7 # Default BGM volume, adjustable with Up/Down keys
        self.se_volume = 1.0 # Default Sound Effect volume, adjustable with PageUp/PageDown
        # Fade envelope settings (ms)
        self.se_fade_in_ms = 10   # gentle attack for each drum hit
        self.se_fade_out_ms = 100  # quick release when choked
        self.bgm_fade_ms = 400    # fade-in/out time for BGM on start/seek
        
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
                continue # Don't load BGM as a normal sound

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
                print(f"Warning: Could not load BGM '{os.path.basename(self.bgm_path)}'. Error: {e}")
                self.bgm_path = None
        
        print(f"{len(self.sounds)} sound effects loaded (out of {len(self.dtx.wav_files)} defined).")

    def _draw_lanes_and_judgment_line(self, screen):
        """Draws the static parts of the note highway."""
        # Draw lane separators
        for config in self.LANES_CONFIG.values():
            x_center = config[0]
            start_pos = (x_center - self.LANE_WIDTH // 2, self.NOTE_HIGHWAY_TOP_Y)
            end_pos = (x_center - self.LANE_WIDTH // 2, self.JUDGMENT_LINE_Y)
            pygame.draw.line(screen, self.COLOR_LANE_SEPARATOR, start_pos, end_pos, 1)
        
        # Draw judgment line
        pygame.draw.line(screen, self.COLOR_JUDGMENT_LINE, (0, self.JUDGMENT_LINE_Y), (self.SCREEN_WIDTH, self.JUDGMENT_LINE_Y), 3)

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

                # Handle kick drum notes (horizontal bar)
                if channel_id == self.KICK_CHANNEL:
                    note_rect = pygame.Rect(0, y_pos - 2, self.SCREEN_WIDTH, 5)
                    pygame.draw.rect(screen, self.KICK_COLOR, note_rect)
                # Handle regular lane notes
                elif channel_id in self.LANES_CONFIG:
                    config = self.LANES_CONFIG[channel_id]
                    x_center = config[0]
                    color = config[1]
                    note_rect = pygame.Rect(x_center - self.LANE_WIDTH // 2, y_pos - 4, self.LANE_WIDTH, 8)

                    # --- Special Hi-Hat Visuals ---
                    if channel_id == '18': # Open Hi-Hat
                        # Draw as a hollow rectangle to signify "open"
                        pygame.draw.rect(screen, color, note_rect, 2)
                    elif channel_id == '1B': # Pedal Hi-Hat
                        # Draw as a smaller, thinner bar to distinguish it
                        pedal_rect = pygame.Rect(x_center - self.LANE_WIDTH // 2, y_pos - 1, self.LANE_WIDTH, 3)
                        pygame.draw.rect(screen, color, pedal_rect)
                    else: # All other notes (including closed HH)
                        pygame.draw.rect(screen, color, note_rect)

    def _draw_hit_animations(self, screen, current_time_ms):
        """Draws a visual indicator when a note is hit."""
        ANIMATION_DURATION_MS = 80
        # Iterate over a copy, as we might remove items
        for anim in self.hit_animations[:]:
            if current_time_ms - anim['time'] > ANIMATION_DURATION_MS:
                self.hit_animations.remove(anim)
                continue
            
            channel_id = anim['channel_id']
            if channel_id == self.KICK_CHANNEL:
                pygame.draw.line(screen, self.KICK_COLOR, (0, self.JUDGMENT_LINE_Y - 5), (self.SCREEN_WIDTH, self.JUDGMENT_LINE_Y - 5), 10)
            elif channel_id in self.LANES_CONFIG:
                config = self.LANES_CONFIG[channel_id]
                x_center = config[0]
                color = tuple(min(c + 80, 255) for c in config[1]) # Brighter color
                rect = pygame.Rect(x_center - self.LANE_WIDTH // 2, self.JUDGMENT_LINE_Y - 50, self.LANE_WIDTH, 50)
                pygame.draw.rect(screen, color, rect)

                # Add text for special hi-hats to make hits clearer
                hit_text = None
                if channel_id == '18':
                    hit_text = "OPEN"
                elif channel_id == '1B':
                    hit_text = "PEDAL"

                if hit_text and self.small_font:
                    surface = self.small_font.render(hit_text, True, self.COLOR_BACKGROUND)
                    text_rect = surface.get_rect(center=rect.center)
                    screen.blit(surface, text_rect)

    def play(self):
        """Starts the main playback loop."""
        if not self.sounds and not self.bgm_path:
            print("No sounds were loaded. Nothing to play.")
            return

        notes_to_play = self.dtx.timed_notes[:]
        note_index = 0
        self.time_offset_ms = 0 # Reset offset at the start of every playback
        
        screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(f"Playing: {self.dtx.title} - {self.dtx.artist}")
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Calculate total song duration for progress bar
        song_duration_ms = 0
        if notes_to_play:
            song_duration_ms = notes_to_play[-1][0] + 3000 # Add 3s padding

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
                print(f"Warning: Could not play BGM. Falling back to system clock. Error: {e}")
        
        if not clock_is_audio_driven:
             print("Playback clock is system-driven.")

        start_ticks = pygame.time.get_ticks()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
                        current_time_ms = pygame.mixer.music.get_pos() + self.time_offset_ms
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
                            pygame.mixer.music.play(start=new_time_ms / 1000.0, fade_ms=self.bgm_fade_ms)
                        
                        # Find the new note index
                        note_index = 0
                        for i, note in enumerate(notes_to_play):
                            if note[0] >= new_time_ms:
                                note_index = i
                                break
                        else: # Jumped past the last note
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
                if clock_is_audio_driven: # Just transitioned from audio to system
                    print("BGM finished. Switching to system clock.")
                    clock_is_audio_driven = False
                    # Resync system clock to the BGM's last known position
                    start_ticks = pygame.time.get_ticks() - song_duration_ms

                current_time_ms = pygame.time.get_ticks() - start_ticks

            # Trigger notes that are due
            while note_index < len(notes_to_play) and notes_to_play[note_index][0] <= current_time_ms:
                _, channel_id, wav_id = notes_to_play[note_index]
                if wav_id in self.sounds:
                    sound_to_play = self.sounds[wav_id]
                    
                    # 1. --- Choke Logic ---
                    # If this note is a "choker", stop any corresponding "choked" sounds.
                    if channel_id in self.CHOKE_MAP:
                        for choked_channel_id in self.CHOKE_MAP[channel_id]:
                            if choked_channel_id in self.active_choke_sounds:
                                channel_to_stop = self.active_choke_sounds[choked_channel_id]
                                if channel_to_stop and channel_to_stop.get_busy():
                                    channel_to_stop.fadeout(self.se_fade_out_ms)
                                # Remove it from tracking since it's now choked
                                del self.active_choke_sounds[choked_channel_id]

                    # 2. --- Polyphony & Playback Logic ---
                    # Initialize a list for this sound if it's the first time we've seen it.
                    if wav_id not in self.active_poly_sounds:
                        self.active_poly_sounds[wav_id] = []
                    
                    # Get the list of currently playing instances for this specific sound.
                    playing_instances = self.active_poly_sounds[wav_id]
                    
                    # Clean up any sounds in the list that have finished playing naturally.
                    playing_instances = [ (ch, t) for (ch, t) in playing_instances if ch.get_busy() ]

                    # Voice stealing: If we're at the polyphony limit, stop the oldest sound.
                    if len(playing_instances) >= self.POLYPHONY_LIMIT:
                        # Sort by play time to find the oldest sound.
                        playing_instances.sort(key=lambda x: x[1])
                        # Get the channel of the oldest sound and remove it from our tracking list.
                        oldest_channel, _ = playing_instances.pop(0)
                        # Fade it out to free up a mixer channel.
                        print(f"Fading out {oldest_channel} for {wav_id}")
                        oldest_channel.fadeout(self.se_fade_out_ms)

                    # Play the new sound with a gentle fade-in.
                    wav_vol_percent = self.dtx.wav_volumes.get(wav_id, 100)
                    final_volume = self.se_volume * (wav_vol_percent / 100.0)
                    new_channel = sound_to_play.play(fade_ms=self.se_fade_in_ms)
                    
                    if new_channel:
                        new_channel.set_volume(final_volume)
                        # Add the new sound to our polyphony tracking list.
                        playing_instances.append( (new_channel, current_time_ms) )
                        
                        # If this sound is one that can BE choked (e.g., an open hi-hat),
                        # track its channel so a future "choker" can stop it.
                        if channel_id in self.CHOKEABLE_CHANNELS:
                            self.active_choke_sounds[channel_id] = new_channel

                    # Update the master list of active sounds.
                    self.active_poly_sounds[wav_id] = playing_instances
                        
                    # Add an animation for visual feedback
                    self.hit_animations.append({'channel_id': channel_id, 'time': current_time_ms})
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
            self._draw_notes(screen, current_time_ms, notes_to_play, note_index)
            self._draw_hit_animations(screen, current_time_ms)
            
            # --- Draw Progress Bar ---
            if song_duration_ms > 0:
                progress = current_time_ms / song_duration_ms
                bar_width = progress * self.SCREEN_WIDTH
                progress_rect = pygame.Rect(0, self.SCREEN_HEIGHT - self.PROGRESS_BAR_HEIGHT, bar_width, self.PROGRESS_BAR_HEIGHT)
                pygame.draw.rect(screen, self.KICK_COLOR, progress_rect)
            
            info_texts = [
                f"Time: {current_time_ms / 1000.0:.2f}s / {song_duration_ms / 1000.0:.2f}s",
                f"Notes Played: {note_index} / {len(notes_to_play)}",
                f"BPM: {self.dtx.bpm:.2f}", # Note: This shows initial BPM only
                f"BGM Volume: {self.bgm_volume * 100:.0f}% (Up/Down)",
                f"SE Volume: {self.se_volume * 100:.0f}% (PgUp/PgDn)",
                "Seek: Left/Right Arrows | Quit: ESC"
            ]
            
            for i, text in enumerate(info_texts):
                surface = self.font.render(text, True, self.COLOR_TEXT)
                screen.blit(surface, (10, 10 + i * 30))

            pygame.display.flip()
            clock.tick(240) # Use a high tick rate for accurate timing

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

if __name__ == '__main__':
    main()
