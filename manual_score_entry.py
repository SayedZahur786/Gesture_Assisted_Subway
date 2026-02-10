"""
Manual score entry dialog for when OCR doesn't work
Simple tkinter dialog to quickly enter score
"""

import tkinter as tk
from tkinter import ttk

class ManualScoreEntry:
    def __init__(self, try_number, player_name):
        self.score = None
        self.try_number = try_number
        self.player_name = player_name
        
    def show(self):
        """Show the score entry dialog and return the entered score"""
        root = tk.Tk()
        root.title("Enter Score")
        root.geometry("400x250")
        root.configure(bg='#2c3e50')
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (400 // 2)
        y = (root.winfo_screenheight() // 2) - (250 // 2)
        root.geometry(f"400x250+{x}+{y}")
        
        # Make window always on top
        root.attributes('-topmost', True)
        
        # Title
        title_frame = tk.Frame(root, bg='#34495e', pady=15)
        title_frame.pack(fill='x')
        
        title = tk.Label(
            title_frame,
            text=f"Try {self.try_number}/3 Complete!",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white'
        )
        title.pack()
        
        player_label = tk.Label(
            title_frame,
            text=f"Player: {self.player_name}",
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1'
        )
        player_label.pack()
        
        # Input frame
        input_frame = tk.Frame(root, bg='#2c3e50', pady=20)
        input_frame.pack(fill='both', expand=True)
        
        label = tk.Label(
            input_frame,
            text="Enter Final Score:",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='white'
        )
        label.pack(pady=(10, 5))
        
        # Score entry
        score_var = tk.StringVar()
        entry = tk.Entry(
            input_frame,
            textvariable=score_var,
            font=('Arial', 20, 'bold'),
            justify='center',
            width=15
        )
        entry.pack(pady=10, ipady=8)
        entry.focus_set()
        
        # Validation message
        msg_label = tk.Label(
            input_frame,
            text="",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#e74c3c'
        )
        msg_label.pack()
        
        def validate_and_submit():
            """Validate score and close"""
            try:
                score = int(score_var.get().strip())
                if score < 0:
                    msg_label.config(text="Score must be 0 or greater")
                    return
                
                self.score = score
                root.destroy()
            except ValueError:
                msg_label.config(text="Please enter a valid number")
        
        def on_enter(event):
            validate_and_submit()
        
        entry.bind('<Return>', on_enter)
        
        # Buttons frame
        button_frame = tk.Frame(root, bg='#2c3e50', pady=10)
        button_frame.pack(fill='x')
        
        # Submit button
        submit_btn = tk.Button(
            button_frame,
            text="Submit Score",
            command=validate_and_submit,
            font=('Arial', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        submit_btn.pack(side='right', padx=20)
        
        # Skip button (score = 0)
        def skip():
            self.score = 0
            root.destroy()
        
        skip_btn = tk.Button(
            button_frame,
            text="Skip (Score = 0)",
            command=skip,
            font=('Arial', 9),
            bg='#7f8c8d',
            fg='white',
            activebackground='#95a5a6',
            activeforeground='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        skip_btn.pack(side='left', padx=20)
        
        # Run
        root.mainloop()
        
        return self.score if self.score is not None else 0


def get_manual_score(try_number, player_name="Player"):
    """
    Show manual score entry dialog and return the score
    
    Args:
        try_number: Current try number (1-3)
        player_name: Name of the player
        
    Returns:
        int: The score entered by user (or 0 if skipped)
    """
    dialog = ManualScoreEntry(try_number, player_name)
    return dialog.show()


# Test
if __name__ == '__main__':
    print("Testing manual score entry dialog...")
    score = get_manual_score(try_number=1, player_name="Test Player")
    print(f"Score entered: {score}")
