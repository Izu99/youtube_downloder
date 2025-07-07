import customtkinter as ctk

def main():
    app = ctk.CTk()
    app.title("Progress Bar Test")
    app.geometry("400x200")

    progressbar = ctk.CTkProgressBar(app)
    progressbar.pack(pady=50)
    progressbar.set(0.5) # Set to 50% for testing

    label = ctk.CTkLabel(app, text="Test Progress Bar")
    label.pack()

    app.mainloop()

if __name__ == "__main__":
    main()