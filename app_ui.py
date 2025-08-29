import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from multimedia_processor import ImageProcessor
import os


class ImageEditorAppUI:
    """
    This class handles the user interface and event handling for the image editor.
    It separates the frontend from the backend image processing logic.
    """

    def __init__(self, root):
        """
        Initializes the UI and connects to the image processor backend.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.geometry("1000x800")
        self.root.title("Aesthetic Image Editor")
        self.style = ttk.Style()
        self.configure_styles()

        self.original_image = None
        self.current_image = None
        self.file_path = None  # New variable to store the file path

        # Store a persistent reference to the displayed images to prevent garbage collection
        self.display_image = None
        self.bg_display_image = None
        self.canvas_image_id = None

        self.processor = ImageProcessor()

        # NOTE: Set the path to your background image here.
        self.background_image_path = "featured-image-3.png"

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.control_frame = ttk.Frame(self.main_frame, padding="10", relief=tk.RAISED)
        self.control_frame.grid(row=0, column=0, sticky="nswe")

        self.canvas_frame = ttk.Frame(self.main_frame, padding="10", relief=tk.SUNKEN)
        self.canvas_frame.grid(row=0, column=1, sticky="nswe")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.status_bar_frame = ttk.Frame(self.root, padding="5")
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.canvas_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.create_status_bar()
        self.create_buttons()
        self.create_menus()
        self.bind_events()

        # Initially display the background image
        self.update_canvas_display()

        self.toggle_widgets(tk.DISABLED)

    def configure_styles(self):
        """Configures the custom styles for the UI elements."""
        self.style.configure("TFrame", background="black")
        self.style.configure("TLabel", background="black", font=("Poppins", 10), foreground="white")
        self.style.configure("TScale", troughcolor="white", background="black")
        self.style.configure("TScale.slider", background="black", bordercolor="black")
        self.style.map("TScale.slider", background=[("active", "black"), ("pressed", "black")])
        self.style.configure("TMenubutton", font=("Poppins", 10))
        self.style.configure("TMenu", font=("Poppins", 10))

    def create_buttons(self):
        """Creates the action buttons and sliders for the editor."""
        self.tools_canvas = tk.Canvas(self.control_frame, highlightthickness=0, bg="black")
        self.tools_scrollbar = ttk.Scrollbar(self.control_frame, orient="vertical", command=self.tools_canvas.yview)

        self.tools_canvas.grid(row=0, column=0, sticky="nswe")
        self.tools_scrollbar.grid(row=0, column=1, sticky="ns")

        self.control_frame.grid_rowconfigure(0, weight=1)
        self.control_frame.grid_columnconfigure(0, weight=1)

        self.tools_frame = tk.Frame(self.tools_canvas, bg="black")

        def center_frame(event):
            canvas_width = event.width
            self.tools_canvas.itemconfig(self.tools_window_id, width=canvas_width)
            self.tools_canvas.coords(self.tools_window_id, canvas_width / 2, 0)
            self.tools_canvas.xview_moveto(0)

        def on_frame_configure(event):
            self.tools_canvas.configure(scrollregion=self.tools_canvas.bbox("all"))

        self.tools_window_id = self.tools_canvas.create_window(0, 0, window=self.tools_frame, anchor="n")

        self.tools_canvas.bind("<Configure>", center_frame)
        self.tools_frame.bind("<Configure>", on_frame_configure)
        self.tools_canvas.configure(yscrollcommand=self.tools_scrollbar.set)

        tk.Label(self.tools_frame, text="Tools", font=("Poppins", 16, "bold"), bg="black", fg="yellow").pack(
            pady=(20, 10))

        # File management buttons
        self.open_button = tk.Button(self.tools_frame, text="Open Image", bg="yellow", fg="black",
                                     font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.open_image)
        self.open_button.pack(pady=5)

        self.save_button = tk.Button(self.tools_frame, text="Save", bg="yellow", fg="black",
                                     font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.save_image,
                                     state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.save_as_button = tk.Button(self.tools_frame, text="Save As", bg="yellow", fg="black",
                                        font=("Poppins", 10, "bold"), relief="flat", width=20,
                                        command=self.save_image_as, state=tk.DISABLED)
        self.save_as_button.pack(pady=5)

        self.convert_button = tk.Button(self.tools_frame, text="Convert Format", bg="yellow", fg="black",
                                        font=("Poppins", 10, "bold"), relief="flat", width=20,
                                        command=self.convert_image, state=tk.DISABLED)
        self.convert_button.pack(pady=5)

        self.clear_button = tk.Button(self.tools_frame, text="Clear Canvas", bg="yellow", fg="black",
                                      font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.clear_canvas,
                                      state=tk.DISABLED)
        self.clear_button.pack(pady=5)

        ttk.Separator(self.tools_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Edit and filter buttons/sliders
        self.reset_button = tk.Button(self.tools_frame, text="Reset", bg="yellow", fg="black",
                                      font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.reset_image,
                                      state=tk.DISABLED)
        self.reset_button.pack(pady=5)

        # Updated labels to have a yellow background
        tk.Label(self.tools_frame, text="Brightness", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=(10, 0))
        self.brightness_slider = ttk.Scale(self.tools_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=180,
                                           command=self.apply_adjustments, state=tk.DISABLED)
        self.brightness_slider.set(0)
        self.brightness_slider.pack(pady=5)

        tk.Label(self.tools_frame, text="Contrast", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=(10, 0))
        self.contrast_slider = ttk.Scale(self.tools_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=180,
                                         command=self.apply_adjustments, state=tk.DISABLED)
        self.contrast_slider.set(0)
        self.contrast_slider.pack(pady=5)

        tk.Label(self.tools_frame, text="Saturation", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=(10, 0))
        self.saturation_slider = ttk.Scale(self.tools_frame, from_=0, to=200, orient=tk.HORIZONTAL, length=180,
                                           command=self.apply_adjustments, state=tk.DISABLED)
        self.saturation_slider.set(100)
        self.saturation_slider.pack(pady=5)

        tk.Label(self.tools_frame, text="Warmth", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=(10, 0))
        self.warmth_slider = ttk.Scale(self.tools_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=180,
                                       command=self.apply_adjustments, state=tk.DISABLED)
        self.warmth_slider.set(0)
        self.warmth_slider.pack(pady=5)

        tk.Label(self.tools_frame, text="Grayscale Level", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=(10, 0))
        self.grayscale_slider = ttk.Scale(self.tools_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=180,
                                          command=self.apply_adjustments, state=tk.DISABLED)
        self.grayscale_slider.pack(pady=5)

        tk.Label(self.tools_frame, text="Blur Level", bg="yellow", fg="black", font=("Poppins", 10), relief="flat", width=20).pack(
            pady=5)
        self.blur_slider = ttk.Scale(self.tools_frame, from_=0, to=20, orient=tk.HORIZONTAL, length=180,
                                     command=self.apply_adjustments, state=tk.DISABLED)
        self.blur_slider.pack(pady=5)

        self.rotate_button = tk.Button(self.tools_frame, text="Rotate 90°", bg="yellow", fg="black",
                                       font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.rotate_image,
                                       state=tk.DISABLED)
        self.rotate_button.pack(pady=5)

        self.sharpen_button = tk.Button(self.tools_frame, text="Sharpen", bg="yellow", fg="black",
                                        font=("Poppins", 10, "bold"), relief="flat", width=20,
                                        command=self.sharpen_image, state=tk.DISABLED)
        self.sharpen_button.pack(pady=5)

        self.vignette_button = tk.Button(self.tools_frame, text="Vignette", bg="yellow", fg="black",
                                         font=("Poppins", 10, "bold"), relief="flat", width=20,
                                         command=self.apply_vignette, state=tk.DISABLED)
        self.vignette_button.pack(pady=5)

        ttk.Separator(self.tools_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        self.quit_button = tk.Button(self.tools_frame, text="Quit", bg="yellow", fg="black",
                                     font=("Poppins", 10, "bold"), relief="flat", width=20, command=self.root.quit)
        self.quit_button.pack(pady=5, side=tk.BOTTOM)

    def toggle_widgets(self, state):
        """Enables or disables all non-essential widgets."""
        self.save_button.config(state=state)
        self.save_as_button.config(state=state)
        self.convert_button.config(state=state)
        self.clear_button.config(state=state)
        self.reset_button.config(state=state)
        self.brightness_slider.config(state=state)
        self.contrast_slider.config(state=state)
        self.saturation_slider.config(state=state)
        self.warmth_slider.config(state=state)
        self.grayscale_slider.config(state=state)
        self.blur_slider.config(state=state)
        self.rotate_button.config(state=state)
        self.sharpen_button.config(state=state)
        self.vignette_button.config(state=state)

        self.file_menu.entryconfig("Save", state=state)
        self.file_menu.entryconfig("Save As", state=state)

    def create_status_bar(self):
        """Creates the status bar at the bottom of the window."""
        self.status_bar = tk.Label(self.status_bar_frame, text="Ready", relief=tk.FLAT, anchor=tk.CENTER,
                                   font=("Poppins", 10, "bold"), background="black", fg="yellow")
        self.status_bar.pack(fill=tk.X)

    def create_menus(self):
        """Creates the main menu bar with File and Filters options."""
        self.menubar = tk.Menu(self.root, font=("Poppins", 10))
        self.root.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0, font=("Poppins", 10))
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_image)
        self.file_menu.add_command(label="Save", command=self.save_image)
        self.file_menu.add_command(label="Save As", command=self.save_image_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

    def bind_events(self):
        """Binds the resize event to the canvas so the image can be re-displayed."""
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        """
        Callback to re-display the image when the window is resized.
        This keeps the image scaled correctly.
        """
        self.update_canvas_display()

    def update_canvas_display(self):
        """
        This is the main function for updating the canvas. It decides whether
        to show the current image or the background image.
        """
        # Ensure canvas dimensions are available
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width == 0 or canvas_height == 0:
            self.root.after(100, self.update_canvas_display)
            return

        self.canvas.delete("all")  # Clear the entire canvas

        if self.current_image:
            self.display_image_on_canvas()
        else:
            self.set_background_image()

    def open_image(self):
        """
        Opens a file dialog to select and display an image.
        It handles errors for invalid or corrupted files.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if not file_path:
            return

        try:
            new_image = Image.open(file_path)
            if new_image.width > 0 and new_image.height > 0:
                self.original_image = new_image.copy()
                self.current_image = new_image.copy()
                self.file_path = file_path  # Store the file path
                self.processor.set_image(self.current_image)
                self.update_canvas_display()
                self.status_bar.config(text=f"Opened: {file_path}")
                self.toggle_widgets(tk.NORMAL)
            else:
                self.status_bar.config(
                    text=f"Error: The image file '{os.path.basename(file_path)}' appears to be corrupted.")
                self.toggle_widgets(tk.DISABLED)
        except Exception as e:
            self.status_bar.config(text=f"Error opening image: {e}")
            self.toggle_widgets(tk.DISABLED)

    def set_background_image(self):
        """Displays the specified background image on the canvas."""
        if not os.path.exists(self.background_image_path):
            self.status_bar.config(text=f"Error: Background image not found at '{self.background_image_path}'")
            return

        try:
            bg_image = Image.open(self.background_image_path)
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            resized_bg_image = bg_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.bg_display_image = ImageTk.PhotoImage(resized_bg_image)

            self.canvas.create_image(
                0, 0, anchor=tk.NW, image=self.bg_display_image, tags="background_image"
            )
            self.canvas.tag_lower("background_image")

        except Exception as e:
            self.status_bar.config(text=f"Error setting background image: {e}")

    def display_image_on_canvas(self):
        """
        Resizes the image to fit within the canvas while maintaining its aspect ratio
        and displays it.
        """
        if self.current_image is None:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        try:
            image_aspect = self.current_image.width / self.current_image.height
            canvas_aspect = canvas_width / canvas_height

            if canvas_aspect > image_aspect:
                new_height = canvas_height
                new_width = int(new_height * image_aspect)
            else:
                new_width = canvas_width
                new_height = int(new_width / image_aspect)

            resized_image = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Store the PhotoImage object as an instance variable to prevent garbage collection
            self.display_image = ImageTk.PhotoImage(resized_image)

            # Use the stored reference to display the image
            self.canvas_image_id = self.canvas.create_image(
                canvas_width / 2,
                canvas_height / 2,
                anchor=tk.CENTER,
                image=self.display_image
            )
        except Exception as e:
            self.status_bar.config(text=f"Error displaying image: {e}")
            messagebox.showerror("Display Error", f"Failed to display image. Details: {e}")

    def clear_canvas(self):
        """Clears the image from the canvas and resets the state."""
        self.current_image = None
        self.original_image = None
        self.processor.set_image(None)
        self.update_canvas_display()  # This will now show the background
        self.toggle_widgets(tk.DISABLED)
        self.status_bar.config(text="Canvas cleared. Ready to open a new image.")

    def reset_image(self):
        """Resets the image to its original state."""
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.processor.set_image(self.current_image)
            self.brightness_slider.set(0)
            self.contrast_slider.set(0)
            self.saturation_slider.set(100)
            self.warmth_slider.set(0)
            self.grayscale_slider.set(0)
            self.blur_slider.set(0)
            self.update_canvas_display()
            self.status_bar.config(text="Image reset.")
        else:
            messagebox.showinfo("No Image", "Please open an image first.")

    def save_image(self):
        """Saves the current image to its original file path."""
        # Check if an image is currently loaded in the processor
        if self.current_image is None or self.file_path is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        try:
            self.current_image.save(self.file_path)
            self.status_bar.config(text=f"Image saved to {os.path.basename(self.file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
            self.status_bar.config(text="Error saving image.")

    def save_image_as(self):
        """Allows the user to save the current image to a new file path."""
        # Check if an image is currently loaded
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.current_image.save(file_path)
            self.status_bar.config(text=f"Image saved as {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
            self.status_bar.config(text="Error saving image.")

    def convert_image(self):
        """Allows the user to save the current image in a different file format."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        filetypes = [
            ("JPEG files", "*.jpg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=filetypes
        )

        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            image_to_save = self.current_image.copy()

            if ext in ['.jpg', '.jpeg'] and image_to_save.mode in ('RGBA', 'P'):
                image_to_save = image_to_save.convert('RGB')

            image_to_save.save(file_path)
            self.status_bar.config(text=f"Image saved as {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")
            self.status_bar.config(text=f"Error saving image.")

    def apply_adjustments(self, *args):
        """Applies all slider adjustments by calling the backend."""
        if self.original_image is None:
            return

        brightness_val = self.brightness_slider.get()
        contrast_val = self.contrast_slider.get()
        saturation_val = self.saturation_slider.get()
        warmth_val = self.warmth_slider.get()
        grayscale_val = self.grayscale_slider.get()
        blur_val = self.blur_slider.get()

        self.current_image = self.processor.apply_adjustments(
            brightness_val, contrast_val, saturation_val, warmth_val, grayscale_val, blur_val
        )
        self.update_canvas_display()
        self.status_bar.config(text="Adjustments applied.")

    def rotate_image(self):
        """Rotates the current image by calling the backend."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        self.current_image = self.processor.rotate_image()
        self.processor.set_image(self.current_image)
        self.update_canvas_display()
        self.status_bar.config(text="Image rotated 90 degrees.")

    def sharpen_image(self):
        """Sharpens the current image by calling the backend."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        self.current_image = self.processor.sharpen_image()
        self.processor.set_image(self.current_image)
        self.update_canvas_display()
        self.status_bar.config(text="Image sharpened.")

    def apply_vignette(self):
        """Applies a vignette effect by calling the backend."""
        if self.current_image is None:
            messagebox.showwarning("No Image", "Please open an image first.")
            return

        self.current_image = self.processor.apply_vignette()
        self.processor.set_image(self.current_image)
        self.update_canvas_display()
        self.status_bar.config(text="Applied Vignette.")
