"""
Debug tool to test score detection and see what's being captured
Saves images and shows OCR output to help troubleshoot
"""

import mss
import cv2
import numpy as np
import pytesseract
import time
import config

# try:
#     import pygetwindow as gw
# except ImportError:
#     print("Installing pygetwindow...")
#     import subprocess
#     subprocess.check_call(['pip', 'install', 'pygetwindow'])
#     import pygetwindow as gw

import window_utils as gw

# Set tesseract path if specified in config
if hasattr(config, 'TESSERACT_PATH') and config.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

def find_game_window():
    """Find the game window by title"""
    try:
        all_windows = gw.getAllWindows()
        matching_windows = [w for w in all_windows if config.GAME_WINDOW_TITLE.lower() in w.title.lower()]
        
        if not matching_windows:
            return None
        
        return matching_windows[0]
    except:
        return None

def capture_score_region(game_window):
    """Capture the score region from game window"""
    try:
        with mss.mss() as sct:
            monitor = {
                'left': game_window.left + config.SCORE_REGION['x'],
                'top': game_window.top + config.SCORE_REGION['y'],
                'width': config.SCORE_REGION['width'],
                'height': config.SCORE_REGION['height']
            }
            
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
    except Exception as e:
        print(f"✗ Error capturing: {e}")
        return None

def preprocess_variations(image):
    """Try multiple preprocessing approaches"""
    variations = {}
    
    # Original
    variations['1_original'] = image.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variations['2_grayscale'] = gray
    
    # High contrast
    alpha = 2.0
    enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)
    variations['3_high_contrast'] = enhanced
    
    # Binary threshold (OTSU)
    _, thresh_otsu = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variations['4_binary_otsu'] = thresh_otsu
    
    # Inverted binary
    _, thresh_inv = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    variations['5_binary_inverted'] = thresh_inv
    
    # Adaptive threshold
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    variations['6_adaptive'] = adaptive
    
    # Denoised
    denoised = cv2.fastNlMeansDenoising(thresh_otsu)
    variations['7_denoised'] = denoised
    
    # Scaled up 3x
    scale = 3
    scaled = cv2.resize(denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    variations['8_scaled_3x'] = scaled
    
    return variations

def test_ocr(variations):
    """Test OCR on all preprocessing variations"""
    print("\n" + "="*70)
    print("OCR RESULTS FOR EACH PREPROCESSING METHOD:")
    print("="*70)
    
    best_score = None
    best_method = None
    
    for name, img in variations.items():
        try:
            # Try default config
            text1 = pytesseract.image_to_string(img, config=config.OCR_CONFIG)
            digits1 = ''.join(filter(str.isdigit, text1))
            
            # Try with different config (allow more characters)
            text2 = pytesseract.image_to_string(img, config='--psm 7')
            digits2 = ''.join(filter(str.isdigit, text2))
            
            # Try with no config
            text3 = pytesseract.image_to_string(img)
            digits3 = ''.join(filter(str.isdigit, text3))
            
            print(f"\n{name}:")
            print(f"  Default OCR: '{text1.strip()}' → Digits: {digits1 if digits1 else '(none)'}")
            print(f"  PSM 7:       '{text2.strip()}' → Digits: {digits2 if digits2 else '(none)'}")
            print(f"  No config:   '{text3.strip()}' → Digits: {digits3 if digits3 else '(none)'}")
            
            # Track best result
            for d in [digits1, digits2, digits3]:
                if d and (best_score is None or len(d) > len(best_score)):
                    best_score = d
                    best_method = name
                    
        except Exception as e:
            print(f"{name}: ERROR - {e}")
    
    if best_score:
        print("\n" + "="*70)
        print(f"✓ BEST RESULT: {best_score} (from {best_method})")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("✗ NO DIGITS DETECTED IN ANY METHOD")
        print("="*70)

def main():
    print("="*70)
    print("SCORE DETECTION DEBUG TOOL".center(70))
    print("="*70)
    
    # Find game window
    print("\n1. Finding game window...")
    game_window = find_game_window()
    
    if game_window is None:
        print(f"✗ Could not find game window with title containing '{config.GAME_WINDOW_TITLE}'")
        return
    
    print(f"✓ Found: '{game_window.title}'")
    print(f"  Position: ({game_window.left}, {game_window.top})")
    print(f"  Size: {game_window.width}x{game_window.height}")
    
    # Capture score region
    print("\n2. Capturing score region...")
    print(f"  Region (relative to window): {config.SCORE_REGION}")
    
    img = capture_score_region(game_window)
    
    if img is None:
        print("✗ Failed to capture image")
        return
    
    print(f"✓ Captured: {img.shape}")
    
    # Save original
    cv2.imwrite('debug_original.png', img)
    print("  Saved: debug_original.png")
    
    # Create preprocessing variations
    print("\n3. Creating preprocessing variations...")
    variations = preprocess_variations(img)
    
    # Save all variations
    for name, var_img in variations.items():
        filename = f'debug_{name}.png'
        cv2.imwrite(filename, var_img)
    
    print(f"✓ Saved {len(variations)} variations as debug_*.png")
    
    # Test OCR
    print("\n4. Testing OCR on all variations...")
    test_ocr(variations)
    
    # Display images
    print("\n5. Displaying captured region (press any key to close)...")
    
    # Create a grid of images
    rows = []
    for i in range(0, len(variations), 3):
        items = list(variations.items())[i:i+3]
        row_imgs = []
        for name, img in items:
            # Add label
            labeled = img.copy()
            if len(labeled.shape) == 2:
                labeled = cv2.cvtColor(labeled, cv2.COLOR_GRAY2BGR)
            cv2.putText(labeled, name, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            row_imgs.append(labeled)
        
        # Pad if needed
        while len(row_imgs) < 3:
            row_imgs.append(np.zeros_like(row_imgs[0]))
        
        rows.append(np.hstack(row_imgs))
    
    grid = np.vstack(rows)
    
    cv2.namedWindow('All Preprocessing Methods - Press any key to close', cv2.WINDOW_NORMAL)
    cv2.imshow('All Preprocessing Methods - Press any key to close', grid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE")
    print("="*70)
    print("\nCheck the debug_*.png files to see what's being captured")
    print("If the score is not visible in the images, recalibrate the region")
    print("\nIf score IS visible but OCR failed, try updating:")
    print("  - OCR_CONFIG in config.py")
    print("  - Preprocessing steps in score_tracker.py")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
