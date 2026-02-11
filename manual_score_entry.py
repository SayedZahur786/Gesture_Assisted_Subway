"""
Modern, visually appealing score entry dialog with Play Again / Save & End options
"""

import tkinter as tk
from tkinter import ttk
import time

class ManualScoreEntry:
    def __init__(self, current_try, max_tries, player_name):
        self.score = None
        self.action = None
        self.current_try = current_try
        self.max_tries = max_tries
        self.player_name = player_name
        
    def show(self):
        """Show the modern score entry dialog and return (score, action) tuple"""
        # System beep
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            time.sleep(0.2)
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except:
            print("\a\a")
        
        root = tk.Tk()
        root.title("Score Entry")
        root.geometry("750x600")
        root.configure(bg='#1a1a2e')  # Dark blue-gray background
        
        # Remove window decorations for modern look
        root.overrideredirect(False)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - 375
        y = (root.winfo_screenheight() // 2) - 300
        root.geometry(f"750x600+{x}+{y}")
        
        root.attributes('-topmost', True)
        root.lift()
        root.focus_force()
        
        # Timestamp for cooldown
        dialog_start = time.time()
        
        # HEADER with gradient effect
        header_frame = tk.Frame(root, bg='#16213e', pady=30)
        header_frame.pack(fill='x')
        
        # Try indicator with progress
        progress_text = f"{'●' * self.current_try}{'○' * (self.max_tries - self.current_try)}"
        tk.Label(
            header_frame,
            text=progress_text,
            font=('Segoe UI', 16),
            bg='#16213e',
            fg='#00d4ff'
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"🎮 TRY {self.current_try} OF {self.max_tries} COMPLETE! 🎮",
            font=('Segoe UI', 28, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        ).pack(pady=(10, 5))
        
        tk.Label(
            header_frame,
            text=f"Player: {self.player_name}",
            font=('Segoe UI', 16),
            bg='#16213e',
            fg='#ffd700'
        ).pack()
        
        # MAIN CONTENT with better spacing
        content = tk.Frame(root, bg='#1a1a2e', pady=40)
        content.pack(fill='both', expand=True, padx=40)
        
        tk.Label(
            content,
            text="Enter Your Final Score:",
            font=('Segoe UI', 18, 'bold'),
            bg='#1a1a2e',
            fg='#ffffff'
        ).pack(pady=(0, 20))
        
        # Score entry with modern styling
        score_frame = tk.Frame(content, bg='#0f3460', relief='flat', bd=0)
        score_frame.pack(pady=10, ipady=5, ipadx=5)
        
        score_var = tk.StringVar()
        entry = tk.Entry(
            score_frame,
            textvariable=score_var,
            font=('Segoe UI', 48, 'bold'),
            justify='center',
            width=8,
            bg='#16213e',
            fg='#00d4ff',
            relief='flat',
            bd=0,
            insertbackground='#00d4ff'
        )
        entry.pack(padx=20, pady=20)
        entry.focus_set()
        
        # Status message
        status_label = tk.Label(
            content,
            text="",
            font=('Segoe UI', 12, 'bold'),
            bg='#1a1a2e',
            fg='#ff6b6b'
        )
        status_label.pack(pady=10)
        
        def validate_score():
            """Validate score input"""
            elapsed = time.time() - dialog_start
            if elapsed < 1.5:
                remaining = int(2 - elapsed)
                status_label.config(text=f"⏳ Wait {remaining} second(s)...")
                root.bell()
                return False
            
            score_text = score_var.get().strip()
            if not score_text:
                status_label.config(text="⚠️ Please enter a score!")
                root.bell()
                return False
            
            try:
                score = int(score_text)
                if score < 0:
                    status_label.config(text="Score must be 0 or greater!")
                    root.bell()
                    return False
                self.score = score
                return True
            except ValueError:
                status_label.config(text="Please enter a valid number!")
                root.bell()
                return False
        
        def on_play_again():
            if validate_score():
                self.action = "play_again"
                root.destroy()
        
        def on_save_end():
            if validate_score():
                self.action = "save_end"
                root.destroy()
        
        entry.bind('<Return>', lambda e: on_play_again() if self.current_try < self.max_tries else on_save_end())
        
        # BUTTONS with modern styling
        btn_frame = tk.Frame(root, bg='#1a1a2e', pady=30)
        btn_frame.pack(fill='x', padx=40)
        
        button_style = {
            'font': ('Segoe UI', 16, 'bold'),
            'relief': 'flat',
            'cursor': 'hand2',
            'bd': 0,
            'padx': 30,
            'pady': 20
        }
        
        # Play Again button (if not last try)
        if self.current_try < self.max_tries:
            play_btn = tk.Button(
                btn_frame,
                text=f"▶  PLAY AGAIN  ▶\nTry {self.current_try + 1}/{self.max_tries}",
                command=on_play_again,
                bg='#00d4ff',
                fg='#0f3460',
                activebackground='#00a8cc',
                activeforeground='#ffffff',
                **button_style
            )
            play_btn.pack(side='left', expand=True, fill='x', padx=(0, 10))
        
        # Save & End button
        save_btn = tk.Button(
            btn_frame,
            text="💾  SAVE & END  💾\nComplete Session",
            command=on_save_end,
            bg='#e94560',
            fg='#ffffff',
            activebackground='#c23854',
            activeforeground='#ffffff',
            **button_style
        )
        
        if self.current_try < self.max_tries:
            save_btn.pack(side='right', expand=True, fill='x', padx=(10, 0))
        else:
            save_btn.pack(expand=True, fill='x')
        
        # Footer
        footer = tk.Frame(root, bg='#16213e', pady=15)
        footer.pack(fill='x', side='bottom')
        
        tk.Label(
            footer,
            text="Press ENTER to submit • ESC to skip",
            font=('Segoe UI', 10),
            bg='#16213e',
            fg='#888888'
        ).pack()
        
        root.mainloop()
        
        # Return defaults if closed without selection
        if self.score is None:
            self.score = 0
        if self.action is None:
            self.action = "save_end"
        
        return (self.score, self.action)


def get_manual_score(current_try, max_tries, player_name="Player"):
    """
    Show manual score entry dialog and return (score, action) tuple
    
    Args:
        current_try: Current try number (1-3)
        max_tries: Maximum number of tries (usually 3)
        player_name: Name of the player
        
    Returns:
        tuple: (score, action) where:
            - score (int): The score entered by user (or 0 if skipped)
            - action (str): "play_again" or "save_end"
    """
    dialog = ManualScoreEntry(current_try, max_tries, player_name)
    return dialog.show()


# Test
if __name__ == '__main__':
    print("Testing modern score entry dialog...")
    
    # Test Try 1
    print("\n=== TEST: Try 1 of 3 ===")
    score, action = get_manual_score(current_try=1, max_tries=3, player_name="Test Player")
    print(f"Result: Score={score}, Action={action}")
    
    # Test Try 3 (last try)
    print("\n=== TEST: Try 3 of 3 (last try) ===")
    score, action = get_manual_score(current_try=3, max_tries=3, player_name="Test Player")
    print(f"Result: Score={score}, Action={action}")
