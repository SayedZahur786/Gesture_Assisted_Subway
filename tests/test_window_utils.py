import window_utils as gw
import sys

def main():
    print("Testing window_utils.py on this system...")
    
    # 1. List all windows
    print("\n1. Listing all windows:")
    windows = gw.getAllWindows()
    for w in windows:
        print(f"  - '{w.title}' (ID: {w.id}) at ({w.left}, {w.top}) {w.width}x{w.height}")
    
    if not windows:
        print("No windows found! (Is wmctrl working?)")
        sys.exit(1)
    
    # 2. Find a specific window (e.g. terminal or browser)
    print("\n2. Finding specific window ('Term' or 'Mozilla'):")
    target_title = "Mozilla" # Usually present in the test environment
    matching = gw.getWindowsWithTitle(target_title)
    
    if matching:
        print(f"  Found {len(matching)} windows containing '{target_title}':")
        for m in matching:
            print(f"    - {m.title}")
            
        # 3. Test activation (optional, might not be visible in headless but worth trying)
        # print(f"\n3. Attempting to activate: '{matching[0].title}'")
        # matching[0].activate()
        # print("  Activation command sent.")
    else:
        print(f"  No window found with title '{target_title}'")

    print("\nTest complete.")

if __name__ == "__main__":
    main()
