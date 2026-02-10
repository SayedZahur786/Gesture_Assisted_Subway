"""
One-time calibration tool to identify the score display region
Now with WINDOW-BASED detection - works on any monitor!
"""

import mss
import cv2
import numpy as np
import time
# try:
#     import pygetwindow as gw
# except ImportError:
#     print("Installing pygetwindow...")
#     import subprocess
#     subprocess.check_call(['pip', 'install', 'pygetwindow'])
#     import pygetwindow as gw

import window_utils as gw

import config

class ScoreRegionCalibrator:
    def __init__(self):
        self.points = []
        self.screenshot = None
        self.display_img = None
        self.window_name = 'Calibration - Click Score Corners'
        self.game_window = None
        self.window_offset = (0, 0)
        
    def find_game_window(self):
        """Find the game window by title"""
        print(f"\n🔍 Looking for game window containing '{config.GAME_WINDOW_TITLE}'...")
        
        all_windows = gw.getAllWindows()
        
        # Find windows matching the title
        matching_windows = [w for w in all_windows if config.GAME_WINDOW_TITLE.lower() in w.title.lower()]
        
        if not matching_windows:
            print(f"\n✗ No window found with title containing '{config.GAME_WINDOW_TITLE}'")
            print("\n📋 Available windows:")
            for w in all_windows[:10]:  # Show first 10
                if w.title:
                    print(f"  - {w.title}")
            return None
        
        # Use the first matching window
        game_window = matching_windows[0]
        print(f"✓ Found game window: '{game_window.title}'")
        print(f"  Position: ({game_window.left}, {game_window.top})")
        print(f"  Size: {game_window.width}x{game_window.height}")
        
        return game_window
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to select region"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 2:
                self.points.append((x, y))
                print(f"\n✓ Point {len(self.points)} selected: ({x}, {y})")
                
                # Redraw the image with all points and lines
                self.display_img = self.screenshot.copy()
                
                # Draw all points
                for i, pt in enumerate(self.points):
                    cv2.circle(self.display_img, pt, 8, (0, 255, 0), -1)
                    cv2.putText(self.display_img, f"{i+1}", (pt[0]+15, pt[1]), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # If we have both points, draw rectangle
                if len(self.points) == 2:
                    cv2.rectangle(self.display_img, self.points[0], self.points[1], (0, 255, 0), 3)
                    cv2.putText(self.display_img, "SCORE REGION", 
                               (self.points[0][0], self.points[0][1]-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    print("\n✓ Region selected! Press ANY KEY to save (or ESC to cancel)...")
                else:
                    print("  Now click the BOTTOM-RIGHT corner of the score...")
                
                cv2.imshow(self.window_name, self.display_img)
    
    def capture_game_window(self):
        """Capture just the game window"""
        try:
            with mss.mss() as sct:
                # Define region based on game window position
                monitor = {
                    'left': self.game_window.left,
                    'top': self.game_window.top,
                    'width': self.game_window.width,
                    'height': self.game_window.height
                }
                
                print(f"\n📸 Capturing game window...")
                print(f"   Region: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
                
                # Capture screenshot of game window only
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array (BGR format for OpenCV)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                print(f"✓ Game window captured: {img.shape}")
                return img
        except Exception as e:
            print(f"✗ Error capturing game window: {e}")
            return None
    
    def run(self):
        """Main calibration process"""
        print("=" * 70)
        print("WINDOW-BASED SCORE REGION CALIBRATION".center(70))
        print("=" * 70)
        print("\n📋 NEW FEATURE: Window-based coordinates!")
        print("   → Works on ANY monitor or window position")
        print("   → Automatically finds the game window")
        print("\n📋 INSTRUCTIONS:")
        print("  1. Make sure Subway Surfer is running (any monitor, any position)")
        print("  2. When the screenshot appears, click TOP-LEFT corner of the score")
        print("  3. Then click BOTTOM-RIGHT corner of the score")
        print("  4. Press any key to save (ESC to cancel)")
        
        # Find the game window
        self.game_window = self.find_game_window()
        
        if self.game_window is None:
            print("\n⚠️ Could not find game window. Make sure Subway Surfer is running!")
            print(f"   Looking for window title containing: '{config.GAME_WINDOW_TITLE}'")
            print("\n💡 TIP: You can change GAME_WINDOW_TITLE in config.py")
            return
        
        print("\n⏳ Capturing in 2 seconds...")
        print("   (Bringing game window to front...)")
        
        # Try to activate the window
        try:
            self.game_window.activate()
            time.sleep(0.5)
        except:
            print("   (Could not activate window automatically)")
        
        time.sleep(1.5)
        
        # Capture game window
        self.screenshot = self.capture_game_window()
        
        if self.screenshot is None:
            print("\n✗ Failed to capture game window. Exiting.")
            return
        
        # Resize if too large for screen
        screen_height = 900  # Max window height
        scale_factor = 1.0
        if self.screenshot.shape[0] > screen_height:
            scale_factor = screen_height / self.screenshot.shape[0]
            new_width = int(self.screenshot.shape[1] * scale_factor)
            new_height = int(self.screenshot.shape[0] * scale_factor)
            self.screenshot = cv2.resize(self.screenshot, (new_width, new_height))
            print(f"✓ Resized for display: {new_width}x{new_height} (scale: {scale_factor:.2f})")
        
        self.display_img = self.screenshot.copy()
        
        # Add instructions overlay
        overlay = self.display_img.copy()
        cv2.rectangle(overlay, (10, 10), (600, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, self.display_img, 0.3, 0, self.display_img)
        cv2.putText(self.display_img, "Click TOP-LEFT corner of score", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(self.display_img, "Then click BOTTOM-RIGHT corner", 
                   (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        cv2.imshow(self.window_name, self.display_img)
        
        print("\n✓ Game window displayed!")
        print("  Click the two corners of the score region...\n")
        
        # Wait for user to select region
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Check if cancelled
        if key == 27:  # ESC
            print("\n✗ Calibration cancelled by user")
            return
        
        if len(self.points) == 2:
            # Calculate region coordinates (accounting for any scaling)
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            
            # Scale back to original size if we resized
            if scale_factor != 1.0:
                x1 = int(x1 / scale_factor)
                y1 = int(y1 / scale_factor)
                x2 = int(x2 / scale_factor)
                y2 = int(y2 / scale_factor)
            
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            print("\n" + "=" * 70)
            print("CALIBRATION COMPLETE!".center(70))
            print("=" * 70)
            print(f"\n📍 Score Region Coordinates (relative to game window):")
            print(f"   X: {x}")
            print(f"   Y: {y}")
            print(f"   Width: {width}")
            print(f"   Height: {height}")
            print(f"\n✨ These coordinates work on ANY monitor or window position!")
            
            # Update config.py file
            self.update_config(x, y, width, height)
            
            # Show preview of selected region
            self.show_preview(x, y, width, height, scale_factor)
        else:
            print("\n✗ Calibration incomplete - not enough points selected")
    
    def update_config(self, x, y, width, height):
        """Update config.py with new coordinates"""
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find and update SCORE_REGION
            in_score_region = False
            new_lines = []
            
            for line in lines:
                if 'SCORE_REGION = {' in line:
                    in_score_region = True
                    new_lines.append(line)
                elif in_score_region:
                    if "'x':" in line:
                        new_lines.append(f"    'x': {x},  # Left edge of score region (relative to game window)\n")
                    elif "'y':" in line:
                        new_lines.append(f"    'y': {y},   # Top edge of score region (relative to game window)\n")
                    elif "'width':" in line:
                        new_lines.append(f"    'width': {width},  # Width of score region\n")
                    elif "'height':" in line:
                        new_lines.append(f"    'height': {height}   # Height of score region\n")
                        in_score_region = False
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("\n✅ config.py updated successfully!")
        
        except Exception as e:
            print(f"\n⚠️ Could not update config.py automatically: {e}")
            print("\nPlease manually update config.py with these values:")
            print(f"SCORE_REGION = {{'x': {x}, 'y': {y}, 'width': {width}, 'height': {height}}}")
    
    def show_preview(self, x, y, width, height, scale_factor):
        """Show preview of the selected region"""
        print("\n👁️ Showing preview of selected region...")
        
        # Get the region from original screenshot (before any resize)
        # We need to recapture at full size
        with mss.mss() as sct:
            monitor = {
                'left': self.game_window.left + x,
                'top': self.game_window.top + y,
                'width': width,
                'height': height
            }
            screenshot = sct.grab(monitor)
            region = np.array(screenshot)
            region = cv2.cvtColor(region, cv2.COLOR_BGRA2BGR)
        
        # Resize for better visibility (3x zoom)
        scale = 3
        preview = cv2.resize(region, (width * scale, height * scale), 
                           interpolation=cv2.INTER_CUBIC)
        
        # Add border
        preview = cv2.copyMakeBorder(preview, 10, 10, 10, 10, 
                                     cv2.BORDER_CONSTANT, value=(0, 255, 0))
        
        cv2.namedWindow('Score Region Preview - Press any key to close', cv2.WINDOW_NORMAL)
        cv2.imshow('Score Region Preview - Press any key to close', preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        print("\n✅ Calibration saved! You can now run: python main.py")
        print("   The system will automatically find the game window!")
        print("=" * 70)

if __name__ == '__main__':
    try:
        calibrator = ScoreRegionCalibrator()
        calibrator.run()
    except KeyboardInterrupt:
        print("\n\n✗ Calibration cancelled by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

