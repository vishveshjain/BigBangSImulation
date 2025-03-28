import tkinter as tk
import math
import random

# --- Data for Universe Epochs ---
# Times are approximate and illustrative
EPOCHS = [
    {
        "name": "Big Bang Singularity",
        "time_years": 0,
        "temp_k": "Infinite",
        "size_factor": 0,
        "description": "The universe begins as an infinitely hot and dense point.",
        "visual": "singularity"
    },
    {
        "name": "Inflation",
        "time_years": 1e-34 / (365*24*3600), # Approx conversion from seconds
        "temp_k": "~10^27 K",
        "size_factor": 1e-26, # Relative illustrative factor
        "description": "Rapid exponential expansion. Universe filled with quark-gluon plasma.",
        "visual": "inflation"
    },
    {
        "name": "Nucleosynthesis",
        "time_years": 3 / (60*24*365), # Approx 3 minutes
        "temp_k": "~10^9 K",
        "size_factor": 1e-15,
        "description": "Protons and neutrons fuse to form the first light nuclei (Hydrogen, Helium, Lithium). Universe is opaque plasma.",
        "visual": "plasma_soup"
    },
    {
        "name": "Recombination",
        "time_years": 377000,
        "temp_k": "~3000 K",
        "size_factor": 1/1100, # Redshift z=1100 approx
        "description": "Universe cools enough for electrons to combine with nuclei, forming neutral atoms. Light can travel freely (CMB is released). Universe becomes transparent.",
        "visual": "transparent_atoms"
    },
    {
        "name": "Dark Ages & First Stars",
        "time_years": 400_000_000, # 400 Million Years
        "temp_k": "~60 K",
        "size_factor": 1/20, # Approx z=20
        "description": "Gravity slowly pulls matter together. The first stars and galaxies begin to form, reionizing the universe.",
        "visual": "first_structures"
    },
    {
        "name": "Galaxy Formation Peak",
        "time_years": 3_000_000_000, # 3 Billion Years
        "temp_k": "~10 K",
        "size_factor": 1/3, # Approx z=2
        "description": "Peak era of star formation and galaxy assembly. Quasars are common.",
        "visual": "forming_galaxies"
    },
    {
        "name": "Present Day",
        "time_years": 13_800_000_000, # 13.8 Billion Years
        "temp_k": "2.7 K (CMB)",
        "size_factor": 1, # Reference point
        "description": "Universe dominated by dark energy, leading to accelerated expansion. Complex structures (clusters, superclusters) exist.",
        "visual": "modern_galaxies"
    },
    {
        "name": "Future - Continued Expansion",
        "time_years": 100_000_000_000, # 100 Billion Years
        "temp_k": "< 1 K",
        "size_factor": 10, # Illustrative
        "description": "Accelerated expansion continues. Galaxies move further apart. Star formation declines.",
        "visual": "distant_galaxies"
    },
        {
        "name": "Future - Heat Death?",
        "time_years": 1e14, # 100 Trillion Years +
        "temp_k": "-> 0 K",
        "size_factor": ">> 10", # Illustrative
        "description": "If expansion continues indefinitely: Star formation ceases, stars die, black holes evaporate (very long term). Universe approaches maximum entropy.",
        "visual": "empty_cold"
    },
]

# --- GUI Application ---

class BigBangSim:
    def __init__(self, master):
        self.master = master
        self.master.title("Conceptual Big Bang Simulation")
        self.master.geometry("800x600")

        self.current_epoch_index = 0

        # --- Top Frame for Info ---
        self.info_frame = tk.Frame(master, pady=10)
        self.info_frame.pack(side=tk.TOP, fill=tk.X)

        self.epoch_label = tk.Label(self.info_frame, text="Epoch:", font=("Arial", 12, "bold"))
        self.epoch_label.pack(side=tk.LEFT, padx=10)
        self.epoch_name_var = tk.StringVar()
        self.epoch_name_label = tk.Label(self.info_frame, textvariable=self.epoch_name_var, font=("Arial", 12))
        self.epoch_name_label.pack(side=tk.LEFT, padx=10)

        self.time_label = tk.Label(self.info_frame, text="Time:", font=("Arial", 12, "bold"))
        self.time_label.pack(side=tk.LEFT, padx=10)
        self.time_var = tk.StringVar()
        self.time_value_label = tk.Label(self.info_frame, textvariable=self.time_var, font=("Arial", 12))
        self.time_value_label.pack(side=tk.LEFT, padx=10)

        # --- Middle Frame for Canvas ---
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="black", width=600, height=400)
        self.canvas.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Configure>", self.on_resize) # Handle window resizing

        # --- Bottom Frame for Controls and Description ---
        self.control_frame = tk.Frame(master, pady=10)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.prev_button = tk.Button(self.control_frame, text="<< Previous Epoch", command=self.prev_epoch)
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(self.control_frame, text="Next Epoch >>", command=self.next_epoch)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        self.desc_label = tk.Label(self.control_frame, text="Description:", font=("Arial", 10, "bold"), justify=tk.LEFT)
        self.desc_label.pack(pady=(5,0)) # Add padding top

        self.desc_text = tk.Text(self.control_frame, height=6, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 10), padx=5, pady=5)
        self.desc_text.pack(fill=tk.X, padx=20, pady=(0, 10)) # Add padding bottom

        # Initialize display
        self.update_display()

    def format_time(self, years):
        if years == 0: return "0 (Singularity)"
        if years < 1e-6: return f"{years * 365 * 24 * 60 * 60:.1e} seconds"
        if years < 1: return f"{years * 365:.1f} days"
        if years < 1000: return f"{years:.0f} years"
        if years < 1e6: return f"{years / 1e3:.1f} thousand years"
        if years < 1e9: return f"{years / 1e6:.1f} million years"
        else: return f"{years / 1e9:.2f} billion years"

    def update_display(self):
        epoch = EPOCHS[self.current_epoch_index]

        # Update Info Labels
        self.epoch_name_var.set(epoch["name"])
        self.time_var.set(f"~ {self.format_time(epoch['time_years'])}")

        # Update Description Box
        self.desc_text.config(state=tk.NORMAL) # Enable editing
        self.desc_text.delete("1.0", tk.END) # Clear previous text
        info = (f"Approx. Temp: {epoch['temp_k']}\n"
                # f"Relative Size Factor: {epoch['size_factor']}\n" # Can be confusing
                f"Key Events: {epoch['description']}")
        if epoch["name"].startswith("Future"):
             info += "\n\n--- Prediction Note ---"
             info += "\nThis 'future' state is a simplified extrapolation based on current cosmological models (Lambda-CDM)."
             info += "\nThe actual long-term future is subject to ongoing research and potential unknown physics."
             if epoch["name"] == "Future - Heat Death?":
                 info += "\nThis scenario assumes continued dark energy dominance and proton stability (or very long decay time)."


        self.desc_text.insert(tk.END, info)
        self.desc_text.config(state=tk.DISABLED) # Disable editing

        # Update Buttons state
        self.prev_button.config(state=tk.NORMAL if self.current_epoch_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_epoch_index < len(EPOCHS) - 1 else tk.DISABLED)

        # Draw on Canvas
        self.draw_epoch(epoch)

    def draw_epoch(self, epoch):
        self.canvas.delete("all") # Clear canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        max_radius = min(width, height) / 2 * 0.9 # Max boundary for visuals

        visual_type = epoch["visual"]
        size_factor = epoch["size_factor"] # Use this conceptually

        # --- Drawing Logic ---
        if visual_type == "singularity":
            self.canvas.config(bg="black")
            self.canvas.create_oval(center_x - 1, center_y - 1, center_x + 1, center_y + 1, fill="white")
        elif visual_type == "inflation":
            self.canvas.config(bg="white") # Hot flash
            # Show expanding boundary conceptually
            radius = max_radius * 0.1 # Still small but expanded rapidly
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="red", width=2)
            # Add some random dots for energy field
            for _ in range(50):
                r = random.uniform(0, radius)
                a = random.uniform(0, 2 * math.pi)
                px, py = center_x + r * math.cos(a), center_y + r * math.sin(a)
                self.canvas.create_oval(px-1, py-1, px+1, py+1, fill="yellow", outline="")
        elif visual_type == "plasma_soup":
            self.canvas.config(bg="orange") # Hot, dense
            radius = max_radius * 0.3
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="yellow", width=1, dash=(4, 2))
            # Densely packed dots (protons, neutrons, electrons - indistinguishable)
            for _ in range(150):
                r = random.uniform(0, radius * 0.95)
                a = random.uniform(0, 2 * math.pi)
                px, py = center_x + r * math.cos(a), center_y + r * math.sin(a)
                self.canvas.create_oval(px-2, py-2, px+2, py+2, fill=random.choice(["red", "blue", "white"]), outline="") # p+, n0, e- colors (symbolic)
        elif visual_type == "transparent_atoms":
            self.canvas.config(bg="darkred") # Cooler, transparent
            radius = max_radius * 0.5
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="gray", width=1)
             # Less dense, neutral atoms (mostly H, He)
            for _ in range(80):
                r = random.uniform(0, radius * 0.95)
                a = random.uniform(0, 2 * math.pi)
                px, py = center_x + r * math.cos(a), center_y + r * math.sin(a)
                self.canvas.create_oval(px-1, py-1, px+1, py+1, fill="lightgray", outline="")
            # Hint of CMB: faint background pattern? Too complex for basic canvas.
        elif visual_type == "first_structures":
            self.canvas.config(bg="#200020") # Dark, cool purple hint
            radius = max_radius * 0.7
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="gray", width=1)
            # Dots starting to clump slightly
            num_clumps = 5
            clump_centers = [(random.uniform(0.1, 0.9) * width, random.uniform(0.1, 0.9) * height) for _ in range(num_clumps)]
            for _ in range(100):
                 # Bias towards clump centers
                cx, cy = random.choice(clump_centers)
                dist_factor = max_radius * 0.15 # How far points spread from clump center
                px = random.gauss(cx, dist_factor)
                py = random.gauss(cy, dist_factor)
                 # Ensure within bounds (simple clip)
                if math.dist((px, py), (center_x, center_y)) < radius * 0.95 :
                    self.canvas.create_oval(px-1, py-1, px+1, py+1, fill="lightblue", outline="") # First stars are blue/white
        elif visual_type == "forming_galaxies":
            self.canvas.config(bg="#100015") # Darker
            radius = max_radius * 0.85
            self.canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="darkgray", width=1)
             # More defined clumps (proto-galaxies), moving apart slightly
            num_galaxies = 15
            galaxy_points = []
            for i in range(num_galaxies):
                 r = random.uniform(radius * 0.1, radius * 0.90) # Place galaxies within boundary
                 a = random.uniform(0, 2 * math.pi)
                 gx, gy = center_x + r * math.cos(a), center_y + r * math.sin(a)
                 galaxy_points.append((gx, gy))
                 g_radius = random.uniform(3, 8) # Size of galaxy representation
                 self.canvas.create_oval(gx-g_radius, gy-g_radius, gx+g_radius, gy+g_radius, fill=random.choice(["yellow", "white", "lightblue"]), outline="")
        elif visual_type == "modern_galaxies":
            self.canvas.config(bg="black")
            radius = max_radius # Full observable universe representation
            # No explicit boundary needed, space is "infinite" conceptually
            # Galaxies are further apart
            num_galaxies = 10 # Fewer visible in a given patch due to expansion
            galaxy_points = []
            for i in range(num_galaxies):
                 # Ensure they are spread out more, less central clustering
                 r = random.uniform(radius * 0.3, radius * 0.95) # Start further out
                 a = random.uniform(0, 2 * math.pi)
                 gx, gy = center_x + r * math.cos(a), center_y + r * math.sin(a)
                 galaxy_points.append((gx, gy))
                 g_radius = random.uniform(4, 10)
                 self.canvas.create_oval(gx-g_radius, gy-g_radius, gx+g_radius, gy+g_radius, fill=random.choice(["white", "lightyellow", "orange"]), outline="gray") # More older stars
        elif visual_type == "distant_galaxies":
            self.canvas.config(bg="black")
            radius = max_radius # Still representing observable patch
            num_galaxies = 5 # Even fewer visible nearby
            galaxy_points = []
            for i in range(num_galaxies):
                 r = random.uniform(radius * 0.5, radius * 0.98) # Even further out on average
                 a = random.uniform(0, 2 * math.pi)
                 gx, gy = center_x + r * math.cos(a), center_y + r * math.sin(a)
                 galaxy_points.append((gx, gy))
                 g_radius = random.uniform(3, 8) # May appear smaller/dimmer
                 self.canvas.create_oval(gx-g_radius, gy-g_radius, gx+g_radius, gy+g_radius, fill=random.choice(["orange", "red"]), outline="darkgray") # Redder, older
        elif visual_type == "empty_cold":
             self.canvas.config(bg="black")
             # Maybe a few dim points representing dead stars or lone black holes (symbolic)
             for _ in range(3):
                px = random.uniform(0, width)
                py = random.uniform(0, height)
                self.canvas.create_oval(px-1, py-1, px+1, py+1, fill="#333333", outline="") # Very dim gray


    def next_epoch(self):
        if self.current_epoch_index < len(EPOCHS) - 1:
            self.current_epoch_index += 1
            self.update_display()

    def prev_epoch(self):
        if self.current_epoch_index > 0:
            self.current_epoch_index -= 1
            self.update_display()

    def on_resize(self, event):
        # Redraw canvas content when window is resized
        self.update_display()


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BigBangSim(root)
    root.mainloop()