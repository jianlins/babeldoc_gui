#!/usr/bin/env python3
"""
Simple test script to verify tkinterdnd2 drag and drop functionality on macOS ARM
"""

import tkinter as tk
import sys
import os

def test_drag_drop():
    """Test basic drag and drop functionality"""
    print("Testing drag and drop support...")
    
    # Test 1: Check if tkinterdnd2 is available
    try:
        import tkinterdnd2
        from tkinterdnd2 import DND_FILES, TkinterDnD
        print("✅ tkinterdnd2 is available")
        tkinterdnd2_available = True
    except ImportError as e:
        print(f"❌ tkinterdnd2 not available: {e}")
        tkinterdnd2_available = False
    
    # Test 2: Check platform
    import platform
    print(f"Platform: {platform.system()} {platform.machine()}")
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        print("✅ Running on macOS ARM (M1/M2)")
    
    # Test 3: Create simple drag and drop window
    if tkinterdnd2_available:
        try:
            print("Creating test window...")
            root = TkinterDnD.Tk()
            root.title("Drag & Drop Test")
            root.geometry("400x200")
            
            label = tk.Label(root, 
                           text="🎯 Drag PDF files here to test\n\nDrop files and check the console output",
                           font=("Arial", 12),
                           justify="center",
                           relief="groove",
                           borderwidth=2,
                           pady=20)
            label.pack(fill="both", expand=True, padx=20, pady=20)
            
            def on_drop(event):
                files = event.data
                print(f"Files dropped: {files}")
                label.configure(text=f"✅ Drop successful!\n\nFiles: {files}\n\nDrag more files to test again")
                root.after(3000, lambda: label.configure(text="🎯 Drag PDF files here to test\n\nDrop files and check the console output"))
            
            # Register drag and drop
            label.drop_target_register(DND_FILES)
            label.dnd_bind('<<Drop>>', on_drop)
            
            print("✅ Test window created with drag and drop support")
            print("Try dragging some PDF files into the window...")
            
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Error creating test window: {e}")
    else:
        print("Skipping GUI test - tkinterdnd2 not available")
        print("\nTo install tkinterdnd2:")
        print("pip install tkinterdnd2")

if __name__ == "__main__":
    test_drag_drop()
