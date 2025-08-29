import tkinter as tk
from app_ui import ImageEditorAppUI

def main():
    """
    The main function to create and run the image editor application.
    """
    root = tk.Tk()
    app = ImageEditorAppUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
