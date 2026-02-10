
import sys
import platform
import subprocess
import collections

# Define a named tuple for window info to mimic pygetwindow's interface
Window = collections.namedtuple('Window', ['title', 'left', 'top', 'width', 'height', 'id'])

class WindowManager:
    """
    A cross-platform window manager abstraction.
    """
    def __init__(self):
        self.os_type = platform.system()
        self.is_linux = self.os_type == 'Linux'
        self.is_windows = self.os_type == 'Windows'

    def get_all_windows(self):
        """
        Returns a list of Window objects.
        """
        if self.is_linux:
            return self._get_windows_linux()
        elif self.is_windows:
            return self._get_windows_windows()
        else:
            print(f"Warning: Unsupported OS: {self.os_type}")
            return []

    def _get_windows_linux(self):
        """
        Uses wmctrl to list windows on Linux.
        """
        try:
            # -lG lists windows with geometry: window_id, desktop_id, x, y, w, h, machine, title
            output = subprocess.check_output(['wmctrl', '-lG'], text=True)
            windows = []
            for line in output.splitlines():
                parts = line.split(maxsplit=7)
                if len(parts) >= 8:
                    win_id = parts[0]
                    # desktop_id = parts[1]
                    x = int(parts[2])
                    y = int(parts[3])
                    w = int(parts[4])
                    h = int(parts[5])
                    # machine = parts[6]
                    title = parts[7]
                    
                    # Add window ID as an attribute so we can activate it later
                    win = Window(title=title, left=x, top=y, width=w, height=h, id=win_id)
                    
                    # Monkey-patch an activate method onto the tuple instance (or use a class wrapper)
                    # Named tuples are immutable, so we can't just add a method easily.
                    # Instead of named tuple, let's use a simple class or just wrap it.
                    # But to keep compatibility with existing code that might access .title directly,
                    # let's use a class that behaves like the named tuple but has methods.
                    windows.append(LinuxWindow(win_id, title, x, y, w, h))
            return windows
        except FileNotFoundError:
            print("Error: wmctrl not found. Please install it with 'sudo apt-get install wmctrl'.")
            return []
        except Exception as e:
            print(f"Error getting windows: {e}")
            return []

    def _get_windows_windows(self):
        """
        Uses pygetwindow on Windows.
        """
        try:
            import pygetwindow as gw
            return gw.getAllWindows()
        except ImportError:
            print("Error: pygetwindow not installed.")
            return []

class LinuxWindow:
    """
    A wrapper class for a Linux window to provide methods like activate().
    """
    def __init__(self, win_id, title, left, top, width, height):
        self.id = win_id
        self.title = title
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def activate(self):
        """
        Activates (brings to front) the window using wmctrl.
        """
        try:
            subprocess.run(['wmctrl', '-ia', self.id], check=True)
        except Exception as e:
            print(f"Error activating window {self.id}: {e}")

    def __repr__(self):
        return f"Window(title='{self.title}', left={self.left}, top={self.top}, width={self.width}, height={self.height})"


# specific export to match pygetwindow interface
def getAllWindows():
    mgr = WindowManager()
    return mgr.get_all_windows()

def getWindowsWithTitle(title):
    mgr = WindowManager()
    all_windows = mgr.get_all_windows()
    return [w for w in all_windows if title.lower() in w.title.lower()]

def getActiveWindow():
    # Placeholder - implementation would require xprop on Linux
    print("Warning: getActiveWindow not fully implemented for Linux yet")
    return None

