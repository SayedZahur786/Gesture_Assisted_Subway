"""
Registration form GUI for player data collection
Uses tkinter for cross-platform compatibility
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re
import config

class RegistrationForm:
    def __init__(self):
        self.user_data = None
        self.root = None
        
    def validate_email(self, email):
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """Basic phone number validation (10 digits)"""
        cleaned = re.sub(r'[^\d]', '', phone)
        return len(cleaned) >= 10
    
    def on_submit(self):
        """Handle form submission"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        contact_permission = self.contact_var.get()
        
        # Validation
        errors = []
        
        if config.REQUIRE_NAME and not name:
            errors.append("Name is required")
        
        if config.REQUIRE_EMAIL:
            if not email:
                errors.append("Email is required")
            elif not self.validate_email(email):
                errors.append("Invalid email format")
        
        if config.REQUIRE_PHONE:
            if not phone:
                errors.append("Phone number is required")
            elif not self.validate_phone(phone):
                errors.append("Phone number must be at least 10 digits")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Store user data
        self.user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'contact_permission': 'Yes' if contact_permission else 'No'
        }
        
        # Close the form
        self.root.quit()
        self.root.destroy()
    
    def on_exit(self):
        """Handle window close"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit the application?"):
            self.root.quit()
            self.root.destroy()
    
    def show(self):
        """Display the registration form and return user data"""
        self.root = tk.Tk()
        self.root.title(config.FORM_TITLE)
        self.root.geometry(f"{config.FORM_WIDTH}x{config.FORM_HEIGHT}")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - config.FORM_WIDTH) // 2
        y = (screen_height - config.FORM_HEIGHT) // 2
        self.root.geometry(f"{config.FORM_WIDTH}x{config.FORM_HEIGHT}+{x}+{y}")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎮 Welcome to Subway Surfer Booth! 🎮",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="Please fill in your details to start playing",
            font=('Arial', 10)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Form fields frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name field
        ttk.Label(form_frame, text="Full Name *", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.name_entry = ttk.Entry(form_frame, font=('Arial', 11), width=40)
        self.name_entry.grid(row=1, column=0, pady=(0, 15), ipady=5)
        self.name_entry.focus()
        
        # Email field
        ttk.Label(form_frame, text="Email Address *", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.email_entry = ttk.Entry(form_frame, font=('Arial', 11), width=40)
        self.email_entry.grid(row=3, column=0, pady=(0, 15), ipady=5)
        
        # Phone field
        ttk.Label(form_frame, text="Phone Number *", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.phone_entry = ttk.Entry(form_frame, font=('Arial', 11), width=40)
        self.phone_entry.grid(row=5, column=0, pady=(0, 20), ipady=5)
        
        # Contact permission checkbox
        self.contact_var = tk.BooleanVar()
        contact_check = ttk.Checkbutton(
            form_frame,
            text="I agree to be contacted for future events",
            variable=self.contact_var,
            cursor='hand2'
        )
        contact_check.grid(row=6, column=0, sticky=tk.W, pady=(0, 25))
        
        # Submit button
        submit_btn = tk.Button(
            form_frame,
            text="START PLAYING",
            command=self.on_submit,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            relief=tk.RAISED,
            bd=3,
            padx=20,
            pady=10
        )
        submit_btn.grid(row=7, column=0, pady=(10, 0))
        
        # Bind Enter key to submit
        self.root.bind('<Return>', lambda e: self.on_submit())
        
        # Run the form
        self.root.mainloop()
        
        return self.user_data

def get_player_data():
    """Convenience function to show form and get data"""
    form = RegistrationForm()
    return form.show()

if __name__ == '__main__':
    # Test the form
    data = get_player_data()
    if data:
        print("Player data collected:")
        for key, value in data.items():
            print(f"  {key}: {value}")
    else:
        print("Form cancelled")
