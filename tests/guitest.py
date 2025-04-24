import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("GPIO Screen App")

# Add a label
label = tk.Label(window, text="Hello, GPIO Screen!")
label.pack(pady=20)

# Run the Tkinter event loop
window.mainloop()