"""
Main orchestrator for the Subway Surfer Booth System
Manages the complete user journey: Registration -> Game Session -> Data Storage -> Loop
"""

import cv2
import time
from registration_form import get_player_data
from Subway import start_game_interface
from score_tracker import ScoreTracker
from data_manager import save_player_session
import config

def show_thank_you_screen(user_data, scores):
    """Display a thank you screen with session results"""
    # Create a simple thank you window
    thank_you = cv2.imread('thank_you.png') if cv2.os.path.exists('thank_you.png') else None
    
    if thank_you is None:
        # Create a blank image
        thank_you = cv2.imread('blank_screen.png') if cv2.os.path.exists('blank_screen.png') else None
        if thank_you is None:
            # Fallback: create a simple colored background
            thank_you = (50, 50, 50) + (255,) * (800 * 600 * 3 - 3)
            thank_you = cv2.resize(cv2.imread('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', cv2.IMREAD_COLOR), (800, 600)) if False else (
                (50 * (255 << 16 | 50 << 8 | 50)) * 600 * 800 // (255 * 255 * 255)
            )
            # Simple approach - just create numpy array
            import numpy as np
            thank_you = np.zeros((600, 800, 3), dtype=np.uint8)
            thank_you[:] = (50, 50, 50)  # Dark gray
    
    # Add text
    high_score = max(scores) if scores else 0
    
    cv2.putText(thank_you, "Thank You for Playing!", (150, 200), 
                cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 3)
    cv2.putText(thank_you, f"Player: {user_data['name']}", (200, 300), 
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    cv2.putText(thank_you, f"High Score: {high_score}", (200, 360), 
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.putText(thank_you, f"Scores: {', '.join(map(str, scores))}", (200, 420), 
                cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)
    cv2.putText(thank_you, "Next player loading...", (200, 520), 
                cv2.FONT_HERSHEY_PLAIN, 1.5, (200, 200, 200), 2)
    
    cv2.namedWindow('Thank You', cv2.WINDOW_NORMAL)
    cv2.imshow('Thank You', thank_you)
    cv2.waitKey(config.THANK_YOU_DURATION * 1000)
    cv2.destroyAllWindows()

def main():
    """Main orchestrator - runs in infinite loop for booth operation"""
    print("=" * 60)
    print("SUBWAY SURFER BOOTH SYSTEM")
    print("=" * 60)
    print("\nStarting booth in continuous mode...")
    print("Press Ctrl+C in terminal or close registration form to exit\n")
    
    session_count = 0
    
    try:
        while True:  # Infinite loop for continuous booth operation
            session_count += 1
            print(f"\n{'='*60}")
            print(f"SESSION {session_count}")
            print(f"{'='*60}\n")
            
            # Step 1: Show registration form
            print("Waiting for player registration...")
            user_data = get_player_data()
            
            # Check if form was cancelled (user closed window)
            if user_data is None:
                print("\nRegistration cancelled. Exiting booth system...")
                break
            
            print(f"\n✓ Player registered: {user_data['name']}")
            print(f"  Email: {user_data['email']}")
            print(f"  Phone: {user_data['phone']}")
            print(f"  Contact Permission: {user_data['contact_permission']}")
            
            # Step 2: Initialize score tracker
            tracker = ScoreTracker()
            
            # Step 3: Start game session (3 tries)
            print(f"\nStarting game session for {user_data['name']}...")
            print("Player will get 3 tries. Join hands to start each try.")
            
            try:
                scores = start_game_interface(
                    user_data=user_data,
                    max_tries=config.MAX_TRIES,
                    score_tracker=tracker
                )
            except Exception as e:
                print(f"\n⚠️ Error during game session: {e}")
                scores = []
            
            # Ensure we have valid scores
            if not scores:
                scores = [0, 0, 0]
            
            print(f"\n{'='*60}")
            print(f"SESSION COMPLETE")
            print(f"{'='*60}")
            print(f"Player: {user_data['name']}")
            print(f"Try 1: {scores[0] if len(scores) > 0 else 0}")
            print(f"Try 2: {scores[1] if len(scores) > 1 else 0}")
            print(f"Try 3: {scores[2] if len(scores) > 2 else 0}")
            print(f"High Score: {max(scores) if scores else 0}")
            print(f"{'='*60}\n")
            
            # Step 4: Save to CSV
            print("Saving session data...")
            save_player_session(user_data, scores)
            
            # Step 5: Show thank you screen
            show_thank_you_screen(user_data, scores)
            
            # Step 6: Loop back to registration
            print(f"\nReturning to registration form for next player...\n")
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nBooth system stopped by operator.")
    except Exception as e:
        print(f"\n\n⚠️ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("BOOTH SYSTEM SHUTDOWN")
        print("=" * 60)
        print(f"Total sessions completed: {session_count - 1}")
        print("\nThank you for using the Subway Surfer Booth System!")

if __name__ == '__main__':
    main()
