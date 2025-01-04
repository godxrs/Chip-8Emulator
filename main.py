import pygame
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from chip8 import Chip8
import threading
import time


class EmulatorGUI:
    def __init__(self):
        # Initialize tkinter window
        self.root = tk.Tk()
        self.root.title("CHIP-8 Emulator")

        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.quit_emulator)

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((640, 320))
        pygame.display.set_caption("CHIP-8 Display")
        self.clock = pygame.time.Clock()

        # Initialize CHIP-8
        self.chip8 = Chip8()

        # Create menu
        self.create_menu()

        # Emulation control variables
        self.running = True
        self.paused = False
        self.rom_loaded = False

        # Create control buttons
        self.create_controls()

        # Start emulation thread
        self.emu_thread = threading.Thread(target=self.emulation_loop, daemon=True)
        self.emu_thread.start()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load ROM...", command=self.load_rom)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_emulator)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Controls", command=self.show_controls)
        help_menu.add_command(label="About", command=self.show_about)

    def create_controls(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="Pause/Resume", command=self.toggle_pause).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(self.root, text="No ROM loaded", fg="red")
        self.status_label.pack(pady=5)

    def load_rom(self):
        filename = filedialog.askopenfilename(
            filetypes=[
                ("CHIP-8 ROMs", "*.ch8"),
                ("All files", "*.*")
            ]
        )
        if filename:
            try:
                self.chip8 = Chip8()  # Reset emulator
                self.chip8.load_rom(filename)
                self.rom_loaded = True
                self.paused = False
                self.status_label.config(text=f"Running: {os.path.basename(filename)}", fg="green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ROM: {str(e)}")

    def draw_display(self):
        pixel_array = pygame.PixelArray(self.screen)
        for y in range(32):
            for x in range(64):
                color = (255, 255, 255) if self.chip8.display[y * 64 + x] == 1 else (0, 0, 0)
                pixel_array[x * 10:(x + 1) * 10, y * 10:(y + 1) * 10] = color
        del pixel_array

    def emulation_loop(self):
        while self.running:
            if self.rom_loaded and not self.paused:
                # Handle Pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_emulator()
                        return
                    # Handle other Pygame events using the existing input handler
                    self.chip8.handle_input()

                # Emulate multiple cycles per frame
                for _ in range(10):
                    self.chip8.emulate_cycle()

                # Update display if needed
                if self.chip8.draw_flag:
                    self.screen.fill((0, 0, 0))
                    self.draw_display()
                    pygame.display.flip()
                    self.chip8.draw_flag = False

                self.clock.tick(60)
            else:
                # Handle Pygame events even when paused to allow window closing
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit_emulator()
                        return
                time.sleep(0.016)  # Sleep to prevent high CPU usage when paused

    def toggle_pause(self):
        self.paused = not self.paused
        status_text = "Paused" if self.paused else "Running"
        self.status_label.config(text=status_text)

    def reset(self):
        if self.rom_loaded:
            self.chip8.pc = 0x200
            self.chip8.stack = []
            self.chip8.V = bytearray(16)
            self.chip8.I = 0
            self.chip8.delay_timer = 0
            self.chip8.sound_timer = 0
            self.chip8.display = [0] * (self.chip8.DISPLAY_WIDTH * self.chip8.DISPLAY_HEIGHT)
            self.chip8.draw_flag = True

    def show_controls(self):
        controls = """
        Keyboard Controls:

        1 2 3 4    →    1 2 3 C
        Q W E R    →    4 5 6 D
        A S D F    →    7 8 9 E
        Z X C V    →    A 0 B F
        """
        messagebox.showinfo("Controls", controls)

    def show_about(self):
        about_text = """
        CHIP-8 Emulator

        A simple CHIP-8 emulator with GUI interface.
        Use File > Load ROM to load and play CHIP-8 games.
        """
        messagebox.showinfo("About", about_text)

    def quit_emulator(self):
        self.running = False
        pygame.quit()
        self.root.quit()
        self.root.destroy()

    def run(self):
        try:
            while True:
                self.root.update()
                if not self.running:
                    break
        except tk.TclError:
            # Handle case when window is closed
            self.running = False
            pygame.quit()


def main():
    gui = EmulatorGUI()
    gui.run()


if __name__ == "__main__":
    main()