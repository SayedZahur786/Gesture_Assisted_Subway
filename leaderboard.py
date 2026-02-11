"""
Modern, visually appealing leaderboard - displays as Tkinter GUI instead of OpenCV
"""

import tkinter as tk
from tkinter import ttk
from data_manager import DataManager
import config
import time


class Leaderboard:
    def __init__(self):
        self.data_manager = DataManager()
        self.entries = []
        self.refresh()
    
    def refresh(self):
        """Refresh leaderboard data from CSV."""
        top_n = getattr(config, 'LEADERBOARD_TOP_N', 3)
        self.entries = self.data_manager.get_leaderboard(top_n)
        return self.entries
    
    def get_entries(self):
        """Return current leaderboard entries."""
        return self.entries
    
    def display(self, duration=None):
        """
        Display beautiful leaderboard as Tkinter window.
        
        Args:
            duration: Seconds to show. Defaults to config.LEADERBOARD_DISPLAY_DURATION.
        """
        if duration is None:
            duration = getattr(config, 'LEADERBOARD_DISPLAY_DURATION', 5)
        
        # Refresh data
        self.refresh()
        
        root = tk.Tk()
        root.title("Leaderboard")
        root.geometry("900x700")
        root.configure(bg='#0f1419')  # Very dark blue-black
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - 450
        y = (root.winfo_screenheight() // 2) - 350
        root.geometry(f"900x700+{x}+{y}")
        
        root.attributes('-topmost', True)
        
        # HEADER - Trophy animation area
        header_frame = tk.Frame(root, bg='#1a1f2e', pady=40)
        header_frame.pack(fill='x')
        
        # Big trophy emoji
        tk.Label(
            header_frame,
            text="🏆",
            font=('Segoe UI', 80),
            bg='#1a1f2e'
        ).pack()
        
        tk.Label(
            header_frame,
            text="LEADERBOARD",
            font=('Segoe UI', 36, 'bold'),
            bg='#1a1f2e',
            fg='#ffd700'
        ).pack(pady=(10, 5))
        
        tk.Label(
            header_frame,
            text="TOP PLAYERS",
            font=('Segoe UI', 14),
            bg='#1a1f2e',
            fg='#888888'
        ).pack()
        
        # MAIN CONTENT
        content = tk.Frame(root, bg='#0f1419', pady=30)
        content.pack(fill='both', expand=True, padx=60)
        
        if not self.entries:
            tk.Label(
                content,
                text="No scores yet!\nBe the first to play!",
                font=('Segoe UI', 24),
                bg='#0f1419',
                fg='#888888',
                justify='center'
            ).pack(expand=True)
        else:
            # Medals and colors for ranks
            medal_data = [
                ('🥇', '#ffd700', '#2a2000'),  # Gold
                ('🥈', '#c0c0c0', '#1a1a1a'),  # Silver
                ('🥉', '#cd7f32', '#1a0f00'),  # Bronze
            ]
            
            for i, entry in enumerate(self.entries[:3]):
                medal, text_color, bg_color = medal_data[i]
                
                # Entry frame
                entry_frame = tk.Frame(content, bg=bg_color, pady=20, padx=30)
                entry_frame.pack(fill='x', pady=10)
                
                # Apply subtle gradient effect via border
                entry_frame.config(highlightbackground=text_color, highlightthickness=2)
                
                # Rank and medal
                rank_frame = tk.Frame(entry_frame, bg=bg_color)
                rank_frame.pack(side='left', padx=10)
                
                tk.Label(
                    rank_frame,
                    text=medal,
                    font=('Segoe UI', 48),
                    bg=bg_color
                ).pack()
                
                tk.Label(
                    rank_frame,
                    text=["1ST", "2ND", "3RD"][i],
                    font=('Segoe UI', 12, 'bold'),
                    bg=bg_color,
                    fg=text_color
                ).pack()
                
                # Player info
                info_frame = tk.Frame(entry_frame, bg=bg_color)
                info_frame.pack(side='left', fill='x', expand=True, padx=20)
                
                name = str(entry.get('Name', 'Unknown'))[:20]
                tk.Label(
                    info_frame,
                    text=name,
                    font=('Segoe UI', 24, 'bold'),
                    bg=bg_color,
                    fg='#ffffff',
                    anchor='w'
                ).pack(fill='x')
                
                # Email/phone if available
                email = entry.get('Email', '')
                if email and email != 'N/A':
                    tk.Label(
                        info_frame,
                        text=f"📧 {email[:30]}",
                        font=('Segoe UI', 11),
                        bg=bg_color,
                        fg='#888888',
                        anchor='w'
                    ).pack(fill='x', pady=(5, 0))
                
                # Score
                score_frame = tk.Frame(entry_frame, bg=bg_color)
                score_frame.pack(side='right', padx=10)
                
                try:
                    score = int(entry.get('High_Score', 0))
                except:
                    score = 0
                
                tk.Label(
                    score_frame,
                    text=str(score),
                    font=('Segoe UI', 48, 'bold'),
                    bg=bg_color,
                    fg=text_color
                ).pack()
                
                tk.Label(
                    score_frame,
                    text="POINTS",
                    font=('Segoe UI', 10),
                    bg=bg_color,
                    fg='#888888'
                ).pack()
        
        # FOOTER
        footer = tk.Frame(root, bg='#1a1f2e', pady=25)
        footer.pack(fill='x', side='bottom')
        
        tk.Label(
            footer,
            text="🎮 Play to get on the leaderboard! 🎮",
            font=('Segoe UI', 14, 'bold'),
            bg='#1a1f2e',
            fg='#00d4ff'
        ).pack()
        
        # Auto-close after duration
        root.after(duration * 1000, root.destroy)
        
        root.mainloop()
        
        print(f"\n🏆 Leaderboard displayed ({len(self.entries)} entries)")
    
    def print_to_terminal(self):
        """Print leaderboard to terminal (fallback/debug)."""
        self.refresh()
        
        print("\n" + "=" * 50)
        print("             🏆 LEADERBOARD - TOP 3 🏆")
        print("=" * 50)
        
        if not self.entries:
            print("  No scores recorded yet!")
        else:
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(self.entries[:3]):
                medal = medals[i] if i < len(medals) else f" {i+1}."
                name = str(entry.get('Name', 'Unknown'))[:20]
                try:
                    score = int(entry.get('High_Score', 0))
                except:
                    score = 0
                print(f"  {medal} {name:<20s} Score: {score}")
        
        print("=" * 50)


# Convenience function
def show_leaderboard(duration=None):
    """Show the leaderboard window."""
    lb = Leaderboard()
    lb.display(duration)
    return lb.get_entries()


if __name__ == '__main__':
    print("Testing leaderboard display...")
    lb = Leaderboard()
    lb.print_to_terminal()
    lb.display()
