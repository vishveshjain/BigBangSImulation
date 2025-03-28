import tkinter as tk
import math
import numpy as np
import random
import os # To check for image files
from PIL import Image, ImageTk # Requires 'pip install Pillow'

# --- Cosmological Parameters (Illustrative) ---
H0 = 70
Omega_M0 = 0.3
Omega_R0 = 9e-5
Omega_L0 = 1.0 - Omega_M0 - Omega_R0
H0_per_yr = H0 / (3.086e19 / 1000) * (3.154e7)
sec_in_year = 365.25 * 24 * 3600

# --- Image Loading ---
IMAGE_CACHE = {} # Store loaded PhotoImage objects

def load_image(path, size):
    """Loads an image, resizes it, and creates a PhotoImage."""
    cache_key = (path, size)
    if cache_key in IMAGE_CACHE:
        return IMAGE_CACHE[cache_key]

    if not os.path.exists(path):
        print(f"Warning: Image file not found - {path}")
        return None

    try:
        img = Image.open(path)
        img.thumbnail((size, size), Image.Resampling.LANCZOS) # Resize smoothly
        photo_img = ImageTk.PhotoImage(img)
        IMAGE_CACHE[cache_key] = photo_img # Cache it
        return photo_img
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None

# --- GUI ---
class InteractiveBigBangSim:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive Conceptual Big Bang Simulation")
        self.master.geometry("900x800") # Larger window

        # --- Simulation State ---
        self.current_scale = 1.0
        self.galaxy_comoving_positions = [] # Store base positions
        self.image_references = [] # IMPORTANT: Keep PhotoImage refs

        # --- Load Images (adjust paths and sizes) ---
        self.img_galaxy = load_image("galaxy.png", 50) # Default size 50px
        self.img_star = load_image("star.png", 15)     # Default size 15px
        self.img_nebula = load_image("nebula.png", 80) # Default size 80px

        # --- Top Frame for Slider and Time ---
        self.top_frame = tk.Frame(master, pady=5)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        log_t_min_sec = -43
        log_t_max_sec = 20

        self.time_slider = tk.Scale(
            self.top_frame,
            from_=log_t_min_sec * 10,
            to=log_t_max_sec * 10,
            orient=tk.HORIZONTAL,
            label="Log10(Time in Seconds)",
            command=self.update_simulation_from_slider,
            length=700,
            showvalue=True
        )
        self.time_slider.pack(side=tk.LEFT, padx=10)

        self.time_label_var = tk.StringVar()
        self.time_label = tk.Label(self.top_frame, textvariable=self.time_label_var, font=("Arial", 12))
        self.time_label.pack(side=tk.LEFT, padx=10)

        # --- Canvas Frame ---
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="black", width=800, height=600)
        self.canvas.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # --- Description Text ---
        self.desc_text = tk.Text(master, height=6, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 10), padx=5, pady=5)
        self.desc_text.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        self.desc_label = tk.Label(master, text="Details:", font=("Arial", 10, "bold"), justify=tk.LEFT)
        # Position desc_label above desc_text (pack order matters)
        self.desc_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0,0), before=self.desc_text)

        # --- Bindings for Pan and Zoom ---
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        # Mouse wheel binding (platform dependent)
        self.canvas.bind("<MouseWheel>", self.do_zoom) # Windows
        self.canvas.bind("<Button-4>", self.do_zoom)   # Linux (zoom in)
        self.canvas.bind("<Button-5>", self.do_zoom)   # Linux (zoom out)
        # Binding for clicking on objects (use a tag)
        self.canvas.tag_bind("cosmic_object", "<ButtonPress-3>", self.identify_object) # Right-click to identify

        # --- Initialize ---
        present_day_log_sec = math.log10(13.8e9 * sec_in_year)
        self.time_slider.set(present_day_log_sec * 10)
        self.update_simulation(present_day_log_sec)


    # --- Pan and Zoom Methods ---
    def start_pan(self, event):
        # Check if click is on an object; if so, don't start pan (allow identify)
        # A bit tricky, maybe check tags of item under cursor later if needed.
        # For now, pan always starts on Button-1 press.
        self.canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def do_zoom(self, event):
        scale_factor = 1.0
        # Determine zoom direction
        if event.num == 5 or event.delta < 0: # Linux zoom out or Windows scroll down
            scale_factor = 0.9
        elif event.num == 4 or event.delta > 0: # Linux zoom in or Windows scroll up
            scale_factor = 1.1
        else:
            return # Unknown event

        # Limit zoom
        new_scale = self.current_scale * scale_factor
        if new_scale < 0.01 or new_scale > 100: # Min/Max zoom levels
             print(f"Zoom limit reached: {new_scale:.2f}")
             return
        self.current_scale = new_scale

        # Get canvas coordinates of the mouse pointer
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Scale the canvas around the mouse pointer
        self.canvas.scale("all", x, y, scale_factor, scale_factor)
        # Update scale display maybe?
        # print(f"Current Scale: {self.current_scale:.2f}")


    # --- Object Interaction ---
    def identify_object(self, event):
        # Find item closest to the click (within a small tolerance)
        item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), halo=5)
        if not item: return

        tags = self.canvas.gettags(item[0]) # Get tags of the found item
        info = f"Clicked item {item[0]} with tags: {tags}"

        obj_type = "Unknown Object"
        if "galaxy_tag" in tags: obj_type = "Galaxy (Conceptual)"
        elif "star_tag" in tags: obj_type = "Star (Conceptual)"
        elif "nebula_tag" in tags: obj_type = "Nebula (Conceptual)"
        elif "particle_tag" in tags: obj_type = "Particle/Atom (Conceptual)"

        print(f"{info} - Type: {obj_type}") # Print to console

        # Optional: Update description text briefly?
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.insert("1.0", f"Identified: {obj_type}\n---\n") # Add to top
        self.desc_text.config(state=tk.DISABLED)


    # --- Simulation Update Logic (Modified) ---
    def format_time(self, years):
        if years <= 0: return "0 (Singularity?)"
        if years < 1 / sec_in_year: return f"{years * sec_in_year:.2e} seconds"
        if years < 1 / (365.25): return f"{years * 365.25:.1f} days"
        if years < 1: return f"{years * 365.25:.0f} days"
        if years < 1000: return f"{years:.1f} years"
        if years < 1e6: return f"{years / 1e3:.2f} thousand years"
        if years < 1e9: return f"{years / 1e6:.2f} million years"
        if years < 1e12: return f"{years / 1e9:.2f} billion years"
        else: return f"{years / 1e12:.2f} trillion years"

    def update_simulation_from_slider(self, slider_val_str):
        try:
            slider_val = float(slider_val_str)
            log_t_sec = slider_val / 10.0
            self.update_simulation(log_t_sec)
        except ValueError:
            print(f"Error converting slider value: {slider_val_str}")

    def calculate_state(self, t_years):
        # (Keep the calculate_state function largely the same as before)
        # ... (previous implementation of calculate_state) ...
        state = {}
        state["time_years"] = t_years
        t_present_yr = 13.8e9
        t_rad_mat_eq_yr = 50000
        t_mat_lambda_eq_yr = 9.8e9

        if t_years <= 0:
             scale_factor_approx = 1e-30
             state["temp_k"] = float('inf')
        elif t_years < t_rad_mat_eq_yr:
             a_ml = (Omega_M0/Omega_L0)**(1/3) # a at matter-lambda equality relative to today
             t_ml_norm = t_mat_lambda_eq_yr
             a_at_rm_eq_approx = a_ml * (t_rad_mat_eq_yr / t_ml_norm)**(2/3) # scale factor at rad-mat eq relative to today
             scale_factor_approx = a_at_rm_eq_approx * (t_years / t_rad_mat_eq_yr)**(0.5)
             T_today = 2.725
             state["temp_k"] = T_today / scale_factor_approx # T ~ 1/a always approx holds for CMB temp equivalent
        elif t_years < t_mat_lambda_eq_yr:
             a_ml = (Omega_M0/Omega_L0)**(1/3)
             t_ml_norm = t_mat_lambda_eq_yr
             scale_factor_approx = a_ml * (t_years / t_ml_norm)**(2/3)
             T_today = 2.725
             state["temp_k"] = T_today / scale_factor_approx
        else:
             a_ml = (Omega_M0/Omega_L0)**(1/3)
             a_at_present_approx = 1.0 # By definition
             # Simple Exp fit: a(t) = a_ml * exp[ C * (t - t_ml) ] enforcing a(t_pres)=1
             # This needs numerical integration for accuracy. Using very rough scaling.
             exponent_term = H0_per_yr * math.sqrt(Omega_L0) * (t_years - t_mat_lambda_eq_yr)
             scale_factor_approx = a_ml * np.exp(exponent_term)
             scale_factor_at_present_calc = a_ml * np.exp(H0_per_yr * math.sqrt(Omega_L0) * (t_present_yr - t_mat_lambda_eq_yr))
             scale_factor_approx = scale_factor_approx / scale_factor_at_present_calc # Normalize
             T_today = 2.725
             state["temp_k"] = T_today / scale_factor_approx

        state["scale_factor"] = max(1e-30, scale_factor_approx)
        temp_k = state.get("temp_k", 0)
        T_quark_hadron = 1e12
        t_nucleosynthesis_start_yr = 10 / sec_in_year
        t_nucleosynthesis_end_yr = (20 * 60) / sec_in_year
        T_recombination = 3000
        t_recombination_yr = 377000
        t_first_stars_yr = 200e6

        if t_years * sec_in_year < 1e-12: state["description"] = "Inflation / Planck Era (Conceptual)"
        elif temp_k > T_quark_hadron: state["description"] = "Quark-Gluon Plasma"
        elif t_years > t_nucleosynthesis_start_yr and t_years < t_nucleosynthesis_end_yr: state["description"] = "Big Bang Nucleosynthesis"
        elif temp_k > T_recombination: state["description"] = "Opaque Plasma (Photon Baryon Fluid)"
        elif t_years < t_first_stars_yr:
            if t_years > t_recombination_yr: state["description"] = "Dark Ages (Neutral Atoms, CMB Released)"
            else: state["description"] = "Recombination Ongoing"
        elif t_years < t_mat_lambda_eq_yr: state["description"] = "Structure Formation (Stars, Galaxies)"
        else: state["description"] = "Dark Energy Dominated Expansion"

        state["visual_params"] = {"density": Omega_M0 / state["scale_factor"]**3, "color_temp": temp_k}
        return state


    def update_simulation(self, log_t_sec):
        # ... (Update time label and description text as before) ...
        if not hasattr(self, 'desc_text'): return
        t_sec = 10**log_t_sec
        t_years = t_sec / sec_in_year
        self.time_label_var.set(f"~ {self.format_time(t_years)}")
        current_state = self.calculate_state(t_years)
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        temp_k_str = f"{current_state.get('temp_k', 0):.2E} K" if isinstance(current_state.get('temp_k'), (int, float)) and current_state.get('temp_k') != float('inf') else f"{current_state.get('temp_k', 'N/A')}"
        info = (f"Time: {self.format_time(t_years)}\n"
                f"Approx Temp: {temp_k_str}\n"
                f"Approx Scale Factor (a): {current_state.get('scale_factor', 'N/A'):.3E} (a=1 today)\n"
                f"Dominant Phase: {current_state.get('description', 'N/A')}\n"
                f"Right-Click object to Identify. Scroll to Zoom. Drag to Pan.")
        self.desc_text.insert(tk.END, info)
        self.desc_text.config(state=tk.DISABLED)

        # --- Redraw Canvas ---
        # Important: Reset scale and view before redrawing based on new state
        self.canvas.delete("all")
        # Reset transform to identity before applying current scale
        # self.canvas.scale("all", 0, 0, 1.0/self.current_scale, 1.0/self.current_scale) # This might be tricky to get right
        # Easiest is often to just redraw with current scale applied implicitly by coordinates
        self.draw_dynamic_epoch(current_state)
        # Re-apply the current total zoom/pan state AFTER drawing
        # This is complex. Simpler: just draw objects already scaled.
        # Let's redraw everything assuming scale=1 and let the existing canvas scale handle it.


    def draw_dynamic_epoch(self, state):
        if not hasattr(self, 'canvas') or self.canvas.winfo_width() <= 1: return

        # Clear previous drawings AND kept image references
        self.canvas.delete("all")
        self.image_references.clear() # Clear the list holding PhotoImage objects

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_x, center_y = width / 2, height / 2
        max_radius = min(width, height) / 2 * 1.5 # Allow drawing slightly outside initial view

        temp_k = state.get("temp_k", 0)
        description = state.get("description", "")
        scale_factor = state.get("scale_factor", 1)
        time_years = state.get("time_years", 0)

        # --- Background ---
        # ... (set background color as before) ...
        if temp_k == float('inf'): bg_color = "white"
        elif temp_k > 1e12: bg_color = "yellow"
        elif temp_k > 1e9: bg_color = "orange"
        elif temp_k > 3000: bg_color = "darkred"
        elif temp_k > 50: bg_color = "#400040"
        elif temp_k > 2.7: bg_color = "#100015"
        else: bg_color = "black"
        try: self.canvas.config(bg=bg_color)
        except tk.TclError: self.canvas.config(bg="black")

        # --- Object Drawing Logic ---
        base_num_objects = 70 # Base number for structure era
        object_tags = ["cosmic_object"] # Common tag for interaction

        # --- Early Universe Particles ---
        if "Plasma" in description or "Nucleosynthesis" in description:
            object_tags.append("particle_tag")
            num_particles = int(max(50, min(500, 200 / scale_factor**1.0))) # More dense earlier
            particle_size = 4
            for _ in range(num_particles):
                r = random.uniform(0, max_radius) * (scale_factor**0.5) # Keep closer early on
                a_angle = random.uniform(0, 2 * math.pi)
                px = center_x + r * math.cos(a_angle)
                py = center_y + r * math.sin(a_angle)
                col = random.choice(["red", "white", "yellow", "orange"])
                # Draw simple ovals for very early universe particles
                self.canvas.create_oval(px-particle_size/2, py-particle_size/2, px+particle_size/2, py+particle_size/2, fill=col, outline="", tags=object_tags)

        # --- Neutral Atoms / Dark Ages ---
        elif "Dark Ages" in description or "Recombination" in description:
             object_tags.append("particle_tag")
             num_atoms = int(max(30, min(400, 150 / scale_factor**1.0)))
             atom_size = 3
             for _ in range(num_atoms):
                 r = random.uniform(0, max_radius) # Spread out
                 a_angle = random.uniform(0, 2 * math.pi)
                 px = center_x + r * math.cos(a_angle)
                 py = center_y + r * math.sin(a_angle)
                 # Draw simple ovals
                 self.canvas.create_oval(px-atom_size/2, py-atom_size/2, px+atom_size/2, py+atom_size/2, fill="lightgrey", outline="", tags=object_tags)

        # --- Structure Formation Era (Stars/Galaxies) ---
        elif "Structure" in description or "Expansion" in description:
            if not self.galaxy_comoving_positions or len(self.galaxy_comoving_positions) != base_num_objects:
                self.galaxy_comoving_positions = []
                for _ in range(base_num_objects):
                     # Simple clustering: bias towards center slightly? or just random?
                     r_comov = random.gauss(max_radius * 0.6, max_radius * 0.4) # Gaussian distribution
                     r_comov = max(0, min(max_radius * 1.5, r_comov)) # Clamp within reasonable bounds
                     angle = random.uniform(0, 2 * math.pi)
                     # Also assign a type conceptually (more galaxies later)
                     obj_type = "galaxy" if random.random() < (time_years / 13.8e9)**0.5 else "star" # More galaxies over time
                     if time_years < 500e6 and obj_type == "galaxy": obj_type = "star" # Mostly stars early on
                     self.galaxy_comoving_positions.append((r_comov, angle, obj_type))

            visible_count = 0
            for r_comov, angle, obj_type in self.galaxy_comoving_positions:
                 r_physical = scale_factor * r_comov
                 # Only draw if within a larger boundary to allow panning into view
                 if r_physical < max_radius * 2.0:
                     px = center_x + r_physical * math.cos(angle)
                     py = center_y + r_physical * math.sin(angle)

                     image_to_use = None
                     tags = ["cosmic_object"]
                     use_fallback_oval = False

                     if obj_type == "galaxy" and self.img_galaxy:
                         image_to_use = self.img_galaxy
                         tags.append("galaxy_tag")
                     elif obj_type == "star" and self.img_star:
                         image_to_use = self.img_star
                         tags.append("star_tag")
                     # Add nebula logic maybe? Only in certain eras?
                     # elif some_condition and self.img_nebula:
                     #    image_to_use = self.img_nebula
                     #    tags.append("nebula_tag")
                     else:
                         # Fallback to drawing ovals if image not loaded or type unknown
                         use_fallback_oval = True

                     # --- Create Image or Fallback Oval ---
                     if image_to_use and not use_fallback_oval:
                         # IMPORTANT: Keep a reference to the PhotoImage object
                         self.image_references.append(image_to_use)
                         self.canvas.create_image(px, py, image=image_to_use, tags=tags)
                     else:
                         # Fallback drawing
                         fallback_size = 10 if obj_type == "galaxy" else 4
                         fallback_color = "white" if obj_type == "galaxy" else "lightblue"
                         self.canvas.create_oval(px-fallback_size/2, py-fallback_size/2, px+fallback_size/2, py+fallback_size/2, fill=fallback_color, outline="", tags=tags)

                     visible_count += 1

        # --- Re-apply overall canvas scale after drawing all items at base scale ---
        # This ensures zoom persists across time updates
        # Get center of current view (might be panned)
        current_center_x = self.canvas.canvasx(width/2)
        current_center_y = self.canvas.canvasy(height/2)
        # Apply scale around the logical center (0,0)? or current view center?
        # Scaling around (0,0) might be easier to manage conceptually
        # self.canvas.scale("all", 0, 0, self.current_scale, self.current_scale)
        # NOTE: Re-applying scale like this on every redraw might compound or fight with user zoom.
        # It's safer to draw items already considering the current_scale OR let the existing canvas scale persist.
        # Let's stick with letting the canvas scale persist. The draw logic places items at their
        # base positions, and the existing canvas transform handles the zoom/pan.


    def on_resize(self, event=None): # Allow calling without event
        try:
            log_t_sec = self.time_slider.get() / 10.0
            self.update_simulation(log_t_sec)
        except Exception as e:
             print(f"Error during resize update: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveBigBangSim(root)
    # Ensure initial drawing happens after window is mapped
    root.after(100, app.on_resize) # Call resize/redraw shortly after mainloop starts
    root.mainloop()