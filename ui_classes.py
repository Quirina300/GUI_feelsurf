import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

from PIL import ImageTk, Image
import numpy as np
import os


from FeelSurf_Demo import gameWindow


"""----------------------------PARAMETERS AND VARIABLES----------------------------"""
textures = ["Wood", "RoughFoam", "Texture 3","Texture 4","Texture 5"]
trials_per_texture = 3


likert_labels = ["Extremely\nDissimilar", 
                 "Dissimilar", 
                 "Slightly\nDissimilar", 
                 "Neutral", 
                 "Slightly\nSimilar", 
                 "Similar", 
                 "Extremely\nSimilar"]
participant_scores = np.zeros(trials_per_texture*len(textures))

conditions = ["No visual", "Visual"]


num_participants = 20

default_gain = 20

# window vars
window_width = 600
window_height = 400
root = None
texture_popup = None
slider_popup = None


# [TODO] deze variable is tijdelijk, we need to actually generate random sequence of textures
# rndm_text = ["Wood", "Metal", "RoughFoam", "Carpet", "Rubber","Wood", "Metal", "RoughFoam", "Carpet", "Rubber","Wood", "Metal", "RoughFoam", "Carpet", "Rubber"]
# order_textures = ["Wood", "RoughFoam", "RoughFoam", "Wood", "RoughFoam", "Wood"]
order_textures = np.loadtxt("order.csv", delimiter=",", dtype=str)

# Main GUI window
class FeelSurfGUI:
    # Class attributes
    gain_spinboxes = []
    other_gains = [1,0.5,0,0,0]
    current_condition = 0
    current_participant = 1
    current_trial = 1

    def __init__(self, root):
        # -- Main window with two left-right frames
        self.root = root
        self.font_titles = tkFont.Font(size=14)
        self.root.title("Main Window")
        self.root.geometry(f"{window_width}x{window_height}")

        self.left_frame = tk.Frame(self.root, width=window_width//2, height=window_height)
        self.right_frame = tk.Frame(self.root, width=window_width//2, height=window_height)

        self.left_frame.pack(side="left", expand=True, fill="both")
        self.right_frame.pack(side="right", expand=True, fill="both")

        # -- Subframes
        self.f_participant_info = tk.Frame(self.left_frame, width=window_width//4, height=window_height//2, bg="lightyellow")
        self.f_participant_info.pack(side="top", fill="both", expand=True)

        self.f_gains = tk.Frame(self.right_frame, width=window_width//4, height=window_height//2, bg="lightgreen")
        self.f_gains.pack(side="bottom", fill="both", expand=True)

        self.f_start_experiment = tk.Frame(self.left_frame, width=window_width//4, height=window_height//2, bg="lightblue")
        self.f_start_experiment.pack(side="top", fill="both", expand=True)

        self.f_start_calibration = tk.Frame(self.right_frame, width=window_width//4, height=window_height//2, bg="lightgreen")
        self.f_start_calibration.pack(side="bottom", fill="both", expand=True)

        """---------------------------- GAIN FRAME ELEMENTS ----------------------------"""
        # -- 'Textures' and 'Gains' column titles
        l_textures = tk.Label(self.f_gains, text="Textures")
        l_textures.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        l_gains = tk.Label(self.f_gains, text="Gains")
        l_gains.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # -- Spinboxes to set the gain
        gains_starting_point = [15,45,0,0,0]
        for i in range(len(textures)):
            l = ttk.Label(self.f_gains, text=textures[i])
            l.grid(row=i+1, column=0, padx=5, pady=5, sticky='nsew')

            sb = ttk.Spinbox(self.f_gains, from_=0, to=100, width=10)
            sb.grid(row=i+1, column=1, padx=5, pady=5, sticky='nsew')
            sb.set(gains_starting_point[i])

            self.gain_spinboxes.append(sb) # So we can access their values later

        """---------------------------- PARTICIPANT INFO FRAME ----------------------------"""
        # -- Title of frame
        title_participant = tk.Label(self.f_participant_info, text="Participant info", font=self.font_titles)
        title_participant.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # --Spinbox to set participant number + its label
        l_participant = tk.Label(self.f_participant_info, text="Participant nr: ", width=10)
        l_participant.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.sb_participant = ttk.Spinbox(self.f_participant_info, from_=1, to=20, width=10, command=self.update_participant)
        self.sb_participant.set(self.current_participant)
        self.sb_participant.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        
        # -- Buttons to import and export gains
        b_import = tk.Button(self.f_participant_info, text='Import gains', width=10, command=self.import_gains)
        b_import.grid(row=2, column=0, padx=5, pady=5, sticky='nsew')

        b_export = tk.Button(self.f_participant_info, text='Export gains', width=10, command=self.export_gains)
        b_export.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        """---------------------------- CALIBRATION FRAME ----------------------------"""
        # -- Title of frame
        title_calibration = tk.Label(self.f_start_calibration, text="Calibration options", font=self.font_titles)
        title_calibration.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # -- Combobox to select texture to calibrate
        l_cbox_calibrate = tk.Label(self.f_start_calibration, text="Texture: ")
        l_cbox_calibrate.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.cbox_calibrate = ttk.Combobox(self.f_start_calibration, values=textures, width=10)
        self.cbox_calibrate.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        self.cbox_calibrate.set(textures[0])

        # self.cbox_calibrate.bind("<<ComboboxSelected>>", self.update_calibration_texture)

        # -- Button to start calibration
        b_calibration_start = tk.Button(self.f_start_calibration, text='Start', width=10, command=self.calibrate)
        b_calibration_start.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        """----------------------------START EXPERIMENT FRAME ----------------------------"""
        # -- Title of frame
        title_start_experiment = tk.Label(self.f_start_experiment, text="Experiment options", font=self.font_titles)
        title_start_experiment.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # -- Combobox to select condition
        l_cbox_condition = tk.Label(self.f_start_experiment, text="Condition: ")
        l_cbox_condition.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.cbox_condition = ttk.Combobox(self.f_start_experiment, values=conditions,width=10)
        self.cbox_condition.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        self.cbox_condition.set(conditions[self.current_condition])

        self.cbox_condition.bind("<<ComboboxSelected>>", self.update_condition)

        # -- Visual/no visual indicator image
        self.img_visual = ImageTk.PhotoImage(Image.open("Texture_images/texture.png").resize((120, 120)))
        self.img_no_visual = ImageTk.PhotoImage(Image.open("Texture_images/notexture.png").resize((120, 120)))
        self.l_img_visual = tk.Label(self.f_start_experiment, image = self.img_no_visual)
        self.l_img_visual.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # -- Button to start experiment
        self.b_start_experiment = tk.Button(self.f_start_experiment, text='Start', width=10, command=self.start_experiment)
        self.b_start_experiment.grid(row=3, column=0, padx=5, pady=5, sticky='nsew')

        # -- Button to save & quit
        self.b_save_and_quit = tk.Button(self.f_start_experiment, text='Save & Quit', width=10, command=self.save_and_quit)
        self.b_save_and_quit.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')

    # Run tkinter main loop
    def mainloop(self):
        self.root.mainloop()

    # Import participant gains on button click
    def import_gains(self):
        file_path = f'gains/gains_{self.current_participant}.csv'

        try:
            gains = np.genfromtxt(file_path, delimiter=',', dtype=None, encoding=None)

            # Put gains in spinboxes
            for i, gain in enumerate(gains):
                self.gain_spinboxes[i].set(gain) 

            print(f'Imported the following gains for participant {self.current_participant}: {gains}')

        except FileNotFoundError:
            print(f"Failed to import gains, '{file_path}' does not exist. ")

        except Exception as e:
            print(f"Failed to import gains, an error occurred: {e}")
    
    # Export participant gains on button click
    def export_gains(self):
        gains = np.array([spinbox.get() for spinbox in self.gain_spinboxes]).T
        np.savetxt(f'gains/gains_{self.current_participant}.csv', gains, delimiter=',', fmt='%s')
        print(f'Exported the following gains for participant {self.current_participant}: {gains}')

    # Update current participant when spinbox changes
    def update_participant(self):
        self.current_participant = int(self.sb_participant.get())
        print(type(self.current_participant))
        print(f'Current participant: {self.current_participant}')

    def calibrate(self):
        self.render_texture(self.cbox_calibrate.get(), True)

    # Update current condition and condition preview image when combobox changes
    def update_condition(self, event):
        selected_item = self.cbox_condition.get()
        self.current_condition = conditions.index(selected_item)
        print(selected_item)

        if selected_item == conditions[0]:
            self.l_img_visual.configure(image=self.img_no_visual)
            self.l_img_visual.image = self.img_no_visual
        else:
            self.l_img_visual.configure(image=self.img_visual)
            self.l_img_visual.image = self.img_visual

    # Start experiment on button press
    def start_experiment(self):
        print('started experiment')

        # reset trial counter
        
        self.current_trial = 1

        # reset participant answers
        global participant_scores
        participant_scores = np.zeros(trials_per_texture*len(textures))

        # Spawn texture and slider popup windows, pass self so that it can be used as the parent window
        slider_popup = FeelSurfPopupSlider(self)
        temp_current_participant = (self.current_participant-1)*2 + self.current_condition
        selected_item = order_textures[temp_current_participant, self.current_trial-1]
        self.render_texture(selected_item)
        

    # Save & quit feature (used when button pressed AND when all trials hare finished (slider window))
    def save_and_quit(self, window=None):
        # Close slider window if this function is called from the 'Next' button
        if window:
            window.destroy()
        
        # Handle duplicate filenames
        file_path = f"data/{self.current_participant}_{self.current_condition}.csv"
        if os.path.exists(file_path):
            print(f"Warning: '{file_path}' already exists.")
            base = f"data/{self.current_participant}_{self.current_condition}"
            i = 1
            while True:
                new_path = base + ' (' + str(i) + ').csv'
                if not os.path.exists(new_path):
                    file_path = new_path
                    break
                i += 1
            print(f"Saved as copy instead: {file_path}")

        # Save as csv
        temp_current_participant = (self.current_participant-1)*2 + self.current_condition
        results = np.array([order_textures[temp_current_participant], participant_scores]).T
        np.savetxt(file_path, results, delimiter=",", fmt='%s') 
        print('Quit experiment and saved participant data.')
    
    def render_texture(self, selected_item, calibrating=False):
        selected_item_index = textures.index(selected_item)
        Gain1 = self.gain_spinboxes[selected_item_index].get()
        Gain2 = self.other_gains[selected_item_index]

        texture_file_info = np.loadtxt(f"Texture_signals/{selected_item}.csv")
        if self.cbox_condition.get() == conditions[1] or calibrating: 
            img = True
        else:
            img = False
        gameWindow(selected_item, texture_file_info, Gain1, Gain2, img)


# Popup window that shows likert scale slider
class FeelSurfPopupSlider:
    
    def __init__(self, parent):
        self.parent = parent
        self.font_titles = parent.font_titles

        # Init texture window
        self.window_slider = tk.Toplevel(parent.root)
        self.window_slider.title("slider")

        # Window title
        self.title_slider = tk.Label(self.window_slider, text=f"Trial {gui.current_trial}/{trials_per_texture*len(textures)}", padx=2, font=self.font_titles)
        self.title_slider.grid(row=0, column=2, columnspan=3, padx=20, pady=20)

        # Likert scale
        self.slider_likert = tk.Scale(self.window_slider, from_=1, to=len(likert_labels), orient=tk.HORIZONTAL, label="How similar is the virtual texture to the physical texture?")
        self.slider_likert.config(length=650, tickinterval=1, showvalue=False)
        self.slider_likert.grid(row=1, column=0, columnspan=len(likert_labels), padx=20, pady=20)

        # Likert scale labels
        for i, label_text in enumerate(likert_labels):
            l = tk.Label(self.window_slider, text=label_text, padx=2, width=10)
            l.grid(row=2, column=i, padx=2)

        # 'Next' button
        b_next = tk.Button(self.window_slider, text='Next', width=10, command=self.next)
        b_next.grid(row=3, column=5, columnspan=2, padx=5, pady=5, sticky='nsew')


    def next(self):
        # store participant answer in array
        val = self.slider_likert.get()
        participant_scores[gui.current_trial-1] = val
        print(f"Saved participant answer. Current array of answers: {participant_scores}")

        # advance trial
        gui.current_trial += 1
        
        self.title_slider.config(text=f"Trial {gui.current_trial}/{trials_per_texture*len(textures)}")
        
        # close slider window and call save command in parent window
        if gui.current_trial > trials_per_texture*len(textures):
            self.parent.save_and_quit(self.window_slider)
        else: 
            temp_current_participant = (gui.current_participant-1)*2 + gui.current_condition
            selected_item = order_textures[temp_current_participant, gui.current_trial-1]
            print('current_trial: ', gui.current_trial)
            print('condition: ', selected_item)
            gui.render_texture(selected_item)


if __name__ == "__main__":
    root = tk.Tk()
    gui = FeelSurfGUI(root)
    gui.mainloop()

