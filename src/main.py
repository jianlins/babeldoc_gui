#!/usr/bin/env python3
"""
PDF Translation GUI Application using BabelDOC and Ollama
A Python GUI application for translating PDF files to Chinese using BabelDOC and local Ollama LLM server.
"""

import asyncio
import json
import logging
import os
import platform
import sys
import threading
import tkinter as tk
import urllib.parse
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

import requests

# Import TOML for configuration handling
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        tomllib = None

try:
    import tomli_w  # For writing TOML files
except ImportError:
    tomli_w = None

# Import BabelDOC components
try:
    import babeldoc.format.pdf.high_level
    from babeldoc.format.pdf.translation_config import TranslationConfig
    from babeldoc.translator.translator import OpenAITranslator
    from babeldoc.docvision.doclayout import DocLayoutModel
except ImportError as e:
    print(f"Error importing BabelDOC: {e}")
    print("\nIMPORTANT: Please ensure you're running this in the correct conda environment!")
    print("Steps to fix this:")
    print("1. Activate the 'pdf' conda environment:")
    print("   conda activate pdf")
    print("2. Then run the application:")
    print("   python src/main.py")
    print("\nAlternatively, use the launcher script:")
    print("   ./run.sh")
    
    # Try to show a simple error dialog
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "BabelDOC Not Found", 
            f"Error importing BabelDOC: {e}\n\n"
            "Please ensure you're running this in the 'pdf' conda environment:\n"
            "1. conda activate pdf\n"
            "2. python src/main.py\n\n"
            "Or use the launcher script: ./run.sh"
        )
        root.destroy()
    except:
        pass
    
    sys.exit(1)


class OllamaTranslator(OpenAITranslator):
    """Custom translator that uses Ollama as the backend"""
    
    def __init__(self, lang_in="en", lang_out="zh", model="qwen2.5:14b", 
                 base_url="http://localhost:11434/v1", api_key="ollama", ignore_cache=False):
        super().__init__(
            lang_in=lang_in,
            lang_out=lang_out,
            model=model,
            base_url=base_url,
            api_key=api_key,
            ignore_cache=ignore_cache
        )
        self.name = "ollama"


class DragDropMixin:
    """Mixin class to add drag and drop functionality to tkinter widgets"""
    
    def __init__(self):
        self.drag_drop_enabled = False
        
    def enable_drag_drop(self, widget, callback):
        """Enable drag and drop on a widget with a callback function"""
        self.drag_drop_enabled = True
        self.drop_callback = callback
        
        # Try different drag and drop implementations based on platform
        try:
            self._setup_drag_drop_native(widget)
        except:
            # Fallback to simpler implementation
            try:
                self._setup_drag_drop_simple(widget)
            except Exception as e:
                self.logger.warning(f"Drag and drop not available on this system: {e}")
                self.drag_drop_enabled = False
    
    def _setup_drag_drop_native(self, widget):
        """Setup native drag and drop using tkinterdnd2 if available"""
        try:
            import tkinterdnd2 as tkdnd
            
            # Convert the widget to support drag and drop
            if not hasattr(widget, 'tk'):
                return False
                
            widget.drop_target_register(tkdnd.DND_FILES)
            widget.dnd_bind('<<Drop>>', self._on_drop_event)
            widget.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            widget.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            
            return True
        except ImportError:
            raise ImportError("tkinterdnd2 not available")
        except Exception as e:
            raise Exception(f"Failed to setup native drag drop: {e}")
    
    def _setup_drag_drop_simple(self, widget):
        """Setup simple drag and drop fallback"""
        # Bind to general events that might indicate file drops
        widget.bind("<Button-1>", self._on_click)
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        
        # Add visual feedback
        original_bg = widget.cget("background") if hasattr(widget, 'cget') else None
        widget._original_bg = original_bg
    
    def _on_drop_event(self, event):
        """Handle drop event from tkinterdnd2"""
        try:
            files = event.data.split()
            # Clean file paths (remove file:// prefix, decode URLs)
            cleaned_files = []
            for file_path in files:
                if file_path.startswith('file://'):
                    file_path = file_path[7:]  # Remove file:// prefix
                file_path = urllib.parse.unquote(file_path)  # Decode URL encoding
                
                # Only accept PDF files
                if file_path.lower().endswith('.pdf') and os.path.exists(file_path):
                    cleaned_files.append(file_path)
            
            if cleaned_files:
                self.drop_callback(cleaned_files)
            elif files:
                messagebox.showwarning("Invalid Files", 
                                     "Please drop only PDF files that exist on your system.")
        except Exception as e:
            self.logger.error(f"Error handling drop event: {e}")
            messagebox.showerror("Drop Error", f"Error processing dropped files: {e}")
    
    def _on_drag_enter(self, event):
        """Handle drag enter event (visual feedback)"""
        try:
            event.widget.configure(relief="solid", borderwidth=2)
        except:
            pass
    
    def _on_drag_leave(self, event):
        """Handle drag leave event"""
        try:
            event.widget.configure(relief="flat", borderwidth=1)
        except:
            pass
    
    def _on_enter(self, event):
        """Handle mouse enter event (visual feedback for fallback)"""
        try:
            if hasattr(event.widget, 'configure'):
                event.widget.configure(relief="ridge")
        except:
            pass
    
    def _on_leave(self, event):
        """Handle mouse leave event (fallback)"""
        try:
            if hasattr(event.widget, 'configure'):
                event.widget.configure(relief="flat")
        except:
            pass
    
    def _on_click(self, event):
        """Handle click event (fallback)"""
        # This could be enhanced to show a file dialog as fallback
        pass


class PDFTranslatorGUI(DragDropMixin):
    def __init__(self, root):
        # Initialize DragDropMixin
        DragDropMixin.__init__(self)
        
        self.root = root
        self.root.title("PDF Translator - BabelDOC + Ollama")
        self.root.geometry("800x700")
        
        # Initialize variables
        self.selected_files: List[str] = []
        self.output_directory = ""
        self.translation_config = None
        self.translator = None
        self.is_translating = False
        
        # Configuration file path - using TOML format like BabelDOC
        self.config_file = Path.home() / ".pdf_translator_config.toml"
        
        # Setup logging
        self.setup_logging()
        
        # Create GUI
        self.create_widgets()
        
        # Load saved configuration
        self.load_configuration()
        
        # Initialize BabelDOC
        self.initialize_babeldoc()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_babeldoc(self):
        """Initialize BabelDOC components"""
        try:
            babeldoc.format.pdf.high_level.init()
            self.logger.info("BabelDOC initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize BabelDOC: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize BabelDOC: {e}")
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Save Configuration", command=self.save_configuration)
        settings_menu.add_command(label="Export Config for CLI", command=self.export_config_for_cli)
        settings_menu.add_command(label="Reset to Defaults", command=self.reset_configuration)
        settings_menu.add_separator()
        settings_menu.add_command(label="Configuration Info", command=self.show_configuration_info)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def save_configuration(self):
        """Save current configuration to TOML file in BabelDOC format (excluding input files)"""
        try:
            # Prepare output directory path for TOML (escape backslashes)
            output_dir = self.output_directory.replace('\\', '\\\\') if self.output_directory else ''
            base_url = self.ollama_url_var.get().rstrip('/') + '/v1'
            pool_workers = int(self.qps_var.get()) * 2
            no_dual = str(not self.dual_output_var.get()).lower()
            no_mono = str(not self.mono_output_var.get()).lower()
            show_api_key = str(self.show_api_key).lower()
            
            # Create configuration in BabelDOC TOML format
            config_content = f"""[babeldoc]
# Basic settings
debug = false
lang-in = "{self.source_lang_var.get()}"
lang-out = "{self.target_lang_var.get()}"
qps = {self.qps_var.get()}
output = "{output_dir}"

# PDF processing options
split-short-lines = false
short-line-split-factor = 0.8
skip-clean = false
dual-translate-first = false
disable-rich-text-translate = false
use-alternating-pages-dual = false
watermark-output-mode = "no_watermark"
max-pages-per-part = 50
only_include_translated_page = false
skip-scanned-detection = false
auto_extract_glossary = true
formular_font_pattern = ""
formular_char_pattern = ""
show_char_box = false
ocr_workaround = false
rpc_doclayout = ""
working_dir = ""
auto_enable_ocr_workaround = false

# Translation service
openai = true
openai-model = "{self.model_var.get()}"
openai-base-url = "{base_url}"
openai-api-key = "{self.api_key_var.get()}"
pool-max-workers = {pool_workers}

# Output control
no-dual = {no_dual}
no-mono = {no_mono}
min-text-length = 5
report-interval = 0.5

# GUI-specific settings (not used by BabelDOC CLI)
# These are custom settings for the GUI application
[gui]
window_geometry = "{self.root.geometry()}"
show_api_key = {show_api_key}
"""
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
            # Show brief status message
            if hasattr(self, 'status_var'):
                original_status = self.status_var.get()
                self.status_var.set("Configuration saved")
                self.root.after(2000, lambda: self.status_var.set(original_status))
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            if hasattr(self, 'log_message'):
                self.log_message(f"Failed to save configuration: {e}")
    
    def load_configuration(self):
        """Load configuration from TOML file if it exists"""
        try:
            if self.config_file.exists():
                # Try to parse TOML file
                config = self._parse_toml_config()
                
                if config:
                    # Apply BabelDOC configuration to GUI elements
                    babeldoc_config = config.get('babeldoc', {})
                    gui_config = config.get('gui', {})
                    
                    if "lang-in" in babeldoc_config:
                        self.source_lang_var.set(babeldoc_config["lang-in"])
                    if "lang-out" in babeldoc_config:
                        self.target_lang_var.set(babeldoc_config["lang-out"])
                    if "qps" in babeldoc_config:
                        self.qps_var.set(str(babeldoc_config["qps"]))
                    if "openai-model" in babeldoc_config:
                        self.model_var.set(babeldoc_config["openai-model"])
                    if "openai-base-url" in babeldoc_config:
                        # Remove /v1 suffix for GUI display
                        base_url = babeldoc_config["openai-base-url"]
                        if base_url.endswith("/v1"):
                            base_url = base_url[:-3]
                        self.ollama_url_var.set(base_url)
                    if "openai-api-key" in babeldoc_config:
                        self.api_key_var.set(babeldoc_config["openai-api-key"])
                    if "no-dual" in babeldoc_config:
                        self.dual_output_var.set(not babeldoc_config["no-dual"])
                    if "no-mono" in babeldoc_config:
                        self.mono_output_var.set(not babeldoc_config["no-mono"])
                    if "output" in babeldoc_config and babeldoc_config["output"]:
                        self.output_directory = babeldoc_config["output"]
                        self.output_var.set(f"Output: {self.output_directory}")
                    
                    # Apply GUI-specific settings
                    if "window_geometry" in gui_config:
                        try:
                            self.root.geometry(gui_config["window_geometry"])
                        except:
                            pass  # Ignore invalid geometry
                    if "show_api_key" in gui_config:
                        self.show_api_key = gui_config["show_api_key"]
                        # Apply the API key visibility after widgets are created
                        self.root.after(100, self._apply_api_key_visibility)
                    
                    self.logger.info(f"Configuration loaded from {self.config_file}")
                    self.log_message("Previous configuration loaded successfully")
                
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}")
    
    def _parse_toml_config(self):
        """Parse TOML configuration file with fallback methods"""
        try:
            # Try with tomllib first (Python 3.11+)
            if tomllib:
                with open(self.config_file, 'rb') as f:
                    return tomllib.load(f)
        except:
            pass
        
        try:
            # Fallback to manual parsing for simple TOML structure
            config = {'babeldoc': {}, 'gui': {}}
            current_section = None
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        if current_section not in config:
                            config[current_section] = {}
                        continue
                    
                    if '=' in line and current_section:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Parse value types
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        elif value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]  # Remove quotes
                        elif value.isdigit():
                            value = int(value)
                        elif '.' in value and value.replace('.', '').isdigit():
                            value = float(value)
                        
                        config[current_section][key] = value
            
            return config
        except Exception as e:
            self.logger.error(f"Failed to parse TOML config manually: {e}")
            return None
    
    def _apply_api_key_visibility(self):
        """Apply the saved API key visibility setting"""
        if hasattr(self, 'api_key_entry') and hasattr(self, 'toggle_api_key_button'):
            if self.show_api_key:
                self.api_key_entry.configure(show="")
                self.toggle_api_key_button.configure(text="Hide")
            else:
                self.api_key_entry.configure(show="*")
                self.toggle_api_key_button.configure(text="Show")
    
    def auto_save_configuration(self):
        """Automatically save configuration when settings change"""
        # Cancel any pending save to avoid too frequent saves
        if hasattr(self, '_save_after_id'):
            self.root.after_cancel(self._save_after_id)
        
        # Schedule save after 2 seconds of inactivity
        self._save_after_id = self.root.after(2000, self.save_configuration)
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        try:
            if messagebox.askyesno("Reset Configuration", 
                                 "Are you sure you want to reset all settings to default values?\n\n"
                                 "This will not affect your selected files."):
                # Reset to default values
                self.ollama_url_var.set("http://localhost:11434")
                self.model_var.set("qwen2.5:14b")
                self.api_key_var.set("ollama")
                self.source_lang_var.set("en")
                self.target_lang_var.set("zh")
                self.qps_var.set("2")
                self.dual_output_var.set(True)
                self.mono_output_var.set(True)
                self.output_directory = ""
                self.output_var.set("Current directory")
                self.show_api_key = False
                self._apply_api_key_visibility()
                
                # Remove config file
                if self.config_file.exists():
                    self.config_file.unlink()
                
                self.log_message("Configuration reset to defaults")
                messagebox.showinfo("Reset Complete", "Configuration has been reset to default values.")
                
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset configuration: {e}")
    
    def show_configuration_info(self):
        """Show information about the configuration file"""
        config_info = f"""Configuration File Location:
{self.config_file}

Configuration Format: TOML (BabelDOC compatible)

Configuration is automatically saved when you change settings.

The configuration file uses BabelDOC's native TOML format, so you can:
• Use it directly with BabelDOC CLI: babeldoc --config {self.config_file.name}
• Edit it manually with any text editor
• Share it with other BabelDOC users

Saved settings include:
• Translation service configuration (Ollama/OpenAI)
• Language settings and processing options
• Output preferences and directories
• GUI-specific settings (window size, etc.)

Note: Input PDF files are NOT saved in the configuration for privacy."""
        
        messagebox.showinfo("Configuration Information", config_info)
    
    def export_config_for_cli(self):
        """Export configuration file for use with BabelDOC CLI"""
        try:
            # Ask user where to save the exported config
            export_file = filedialog.asksaveasfilename(
                title="Export Configuration for BabelDOC CLI",
                defaultextension=".toml",
                filetypes=[("TOML files", "*.toml"), ("All files", "*.*")],
                initialvalue="babeldoc_config.toml"
            )
            
            if export_file:
                # Save current configuration first
                self.save_configuration()
                
                # Copy the configuration file to the selected location
                import shutil
                shutil.copy2(self.config_file, export_file)
                
                self.log_message(f"Configuration exported to: {export_file}")
                
                # Show usage instructions
                usage_info = f"""Configuration exported successfully!

Exported to: {export_file}

To use with BabelDOC CLI:
babeldoc --config "{export_file}" --files your-document.pdf

Example command:
babeldoc --config "{export_file}" --files document1.pdf --files document2.pdf

The exported configuration includes all your current settings:
• Translation service (Ollama/OpenAI)
• Language and processing options
• Output preferences

Note: You may need to adjust file paths in the config file for different environments."""
                
                messagebox.showinfo("Export Complete", usage_info)
                
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            messagebox.showerror("Export Error", f"Failed to export configuration: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """PDF Translator - BabelDOC + Ollama

A Python GUI application for translating PDF files using:
• BabelDOC - Advanced PDF processing and translation
• Ollama - Local LLM server for translation

Features:
• BabelDOC-compatible TOML configuration format
• Automatic configuration saving/loading
• Drag and drop PDF file support
• Dual-language and Chinese-only output
• Cross-platform compatibility
• OpenAI API key support for various LLM services

Configuration is automatically saved in BabelDOC TOML format to:
~/.pdf_translator_config.toml

This configuration file can be used directly with BabelDOC CLI:
babeldoc --config ~/.pdf_translator_config.toml

Input PDF files are never saved in the configuration for privacy.

© 2025 - PDF Translation GUI"""
        
        messagebox.showinfo("About PDF Translator", about_text)
    
    def toggle_api_key_visibility(self):
        """Toggle visibility of the API key field"""
        self.show_api_key = not self.show_api_key
        if self.show_api_key:
            self.api_key_entry.configure(show="")
            self.toggle_api_key_button.configure(text="Hide")
        else:
            self.api_key_entry.configure(show="*")
            self.toggle_api_key_button.configure(text="Show")
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Create menu bar
        self.create_menu_bar()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Translator with BabelDOC + Ollama", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="PDF Files Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select PDF Files", 
                  command=self.select_files).grid(row=0, column=0, padx=(0, 10))
        
        self.files_var = tk.StringVar(value="No files selected")
        files_label = ttk.Label(file_frame, textvariable=self.files_var, wraplength=600)
        files_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Drag and drop area
        drop_frame = ttk.Frame(file_frame, relief="groove", borderwidth=2)
        drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        drop_frame.columnconfigure(0, weight=1)
        
        self.drop_label = ttk.Label(drop_frame, 
                                   text="📄 Drag and drop PDF files here\n"
                                        "or use the 'Select PDF Files' button above\n"
                                        "Supports multiple files and cross-platform drag & drop",
                                   justify="center",
                                   font=("Arial", 10),
                                   foreground="gray")
        self.drop_label.grid(row=0, column=0, pady=20, padx=20)
        
        # Enable drag and drop on the drop area
        try:
            self.enable_drag_drop(drop_frame, self.handle_dropped_files)
            self.enable_drag_drop(self.drop_label, self.handle_dropped_files)
            self.logger.info("Drag and drop enabled")
        except Exception as e:
            self.logger.warning(f"Could not enable drag and drop: {e}")
            # Update label to indicate drag and drop is not available
            self.drop_label.configure(text="📄 Use the 'Select PDF Files' button above\n"
                                          "(Drag and drop not available on this system)")
        
        # Store the frames for later access
        self.file_frame = file_frame
        self.drop_frame = drop_frame
        
        # Output directory section
        output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Button(output_frame, text="Select Output Directory", 
                  command=self.select_output_directory).grid(row=0, column=0, padx=(0, 10))
        
        self.output_var = tk.StringVar(value="Current directory")
        output_label = ttk.Label(output_frame, textvariable=self.output_var, wraplength=600)
        output_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Ollama configuration section
        ollama_frame = ttk.LabelFrame(main_frame, text="Ollama Configuration", padding="10")
        ollama_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        ollama_frame.columnconfigure(1, weight=1)
        
        # Ollama URL
        ttk.Label(ollama_frame, text="Ollama URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.ollama_url_var = tk.StringVar(value="http://localhost:11434")
        self.ollama_url_var.trace_add('write', lambda *args: self.auto_save_configuration())
        ollama_url_entry = ttk.Entry(ollama_frame, textvariable=self.ollama_url_var, width=50)
        ollama_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(ollama_frame, text="Test Connection", 
                  command=self.test_ollama_connection).grid(row=0, column=2)
        
        # Model selection
        ttk.Label(ollama_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.model_var = tk.StringVar(value="qwen2.5:14b")
        self.model_var.trace_add('write', lambda *args: self.auto_save_configuration())
        model_entry = ttk.Entry(ollama_frame, textvariable=self.model_var, width=50)
        model_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        ttk.Button(ollama_frame, text="Refresh Models", 
                  command=self.refresh_models).grid(row=1, column=2, pady=(10, 0))
        
        # API Key
        ttk.Label(ollama_frame, text="API Key:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.api_key_var = tk.StringVar(value="ollama")
        self.api_key_var.trace_add('write', lambda *args: self.auto_save_configuration())
        self.api_key_entry = ttk.Entry(ollama_frame, textvariable=self.api_key_var, width=50, show="*")
        self.api_key_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Show/Hide API key button
        self.show_api_key = False
        self.toggle_api_key_button = ttk.Button(ollama_frame, text="Show", 
                                               command=self.toggle_api_key_visibility, width=8)
        self.toggle_api_key_button.grid(row=2, column=2, pady=(10, 0))
        
        # Connection status
        self.connection_status_var = tk.StringVar(value="Not connected")
        status_label = ttk.Label(ollama_frame, textvariable=self.connection_status_var, 
                               foreground="red")
        status_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # Translation options section
        options_frame = ttk.LabelFrame(main_frame, text="Translation Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Source and target languages
        ttk.Label(options_frame, text="Source Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.source_lang_var = tk.StringVar(value="en")
        self.source_lang_var.trace_add('write', lambda *args: self.auto_save_configuration())
        source_lang_combo = ttk.Combobox(options_frame, textvariable=self.source_lang_var, 
                                        values=["en", "fr", "de", "es", "ja", "ko"], width=10)
        source_lang_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(options_frame, text="Target Language:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.target_lang_var = tk.StringVar(value="zh")
        self.target_lang_var.trace_add('write', lambda *args: self.auto_save_configuration())
        target_lang_combo = ttk.Combobox(options_frame, textvariable=self.target_lang_var, 
                                        values=["zh", "zh-CN", "zh-TW"], width=10)
        target_lang_combo.grid(row=0, column=3, sticky=tk.W)
        
        # QPS setting
        ttk.Label(options_frame, text="Translation Speed (QPS):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.qps_var = tk.StringVar(value="2")
        self.qps_var.trace_add('write', lambda *args: self.auto_save_configuration())
        qps_spinbox = ttk.Spinbox(options_frame, from_=1, to=10, textvariable=self.qps_var, width=10)
        qps_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Output options
        self.dual_output_var = tk.BooleanVar(value=True)
        self.dual_output_var.trace_add('write', lambda *args: self.auto_save_configuration())
        ttk.Checkbutton(options_frame, text="Generate dual-language PDF", 
                       variable=self.dual_output_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.mono_output_var = tk.BooleanVar(value=True)
        self.mono_output_var.trace_add('write', lambda *args: self.auto_save_configuration())
        ttk.Checkbutton(options_frame, text="Generate Chinese-only PDF", 
                       variable=self.mono_output_var).grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Translation section
        translate_frame = ttk.LabelFrame(main_frame, text="Translation", padding="10")
        translate_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        translate_frame.columnconfigure(0, weight=1)
        
        self.translate_button = ttk.Button(translate_frame, text="Start Translation", 
                                          command=self.start_translation)
        self.translate_button.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(translate_frame, variable=self.progress_var, 
                                          maximum=100, length=600)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(translate_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Translation Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(log_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def select_files(self):
        """Select PDF files for translation"""
        filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
        files = filedialog.askopenfilenames(
            title="Select PDF files to translate",
            filetypes=filetypes
        )
        
        if files:
            self.selected_files = list(files)
            if len(files) == 1:
                self.files_var.set(f"Selected: {Path(files[0]).name}")
            else:
                self.files_var.set(f"Selected {len(files)} files: {', '.join([Path(f).name for f in files[:3]])}" + 
                                 (f" and {len(files)-3} more..." if len(files) > 3 else ""))
            self.log_message(f"Selected {len(files)} PDF file(s)")
        
    def handle_dropped_files(self, file_paths):
        """Handle files dropped via drag and drop"""
        try:
            # Filter out non-PDF files and duplicates
            pdf_files = []
            for file_path in file_paths:
                if file_path.lower().endswith('.pdf') and os.path.exists(file_path):
                    pdf_files.append(file_path)
            
            if not pdf_files:
                messagebox.showwarning("No PDF Files", 
                                     "No valid PDF files were found in the dropped items.")
                return
            
            # Add to existing selection or replace
            if hasattr(self, 'selected_files') and self.selected_files:
                # Ask user if they want to add or replace
                response = messagebox.askyesnocancel(
                    "Add Files",
                    f"Found {len(pdf_files)} PDF file(s).\n\n"
                    f"You already have {len(self.selected_files)} file(s) selected.\n\n"
                    f"Yes: Add to existing selection\n"
                    f"No: Replace existing selection\n"
                    f"Cancel: Keep current selection"
                )
                
                if response is None:  # Cancel
                    return
                elif response:  # Yes - add to existing
                    # Remove duplicates
                    existing_files = set(self.selected_files)
                    new_files = [f for f in pdf_files if f not in existing_files]
                    if new_files:
                        self.selected_files.extend(new_files)
                        self.log_message(f"Added {len(new_files)} new PDF file(s)")
                    else:
                        messagebox.showinfo("No New Files", "All dropped files were already selected.")
                        return
                else:  # No - replace existing
                    self.selected_files = pdf_files
                    self.log_message(f"Replaced selection with {len(pdf_files)} PDF file(s)")
            else:
                # No existing selection
                self.selected_files = pdf_files
                self.log_message(f"Added {len(pdf_files)} PDF file(s) via drag and drop")
            
            # Update the display
            if len(self.selected_files) == 1:
                self.files_var.set(f"Selected: {Path(self.selected_files[0]).name}")
            else:
                file_names = [Path(f).name for f in self.selected_files[:3]]
                self.files_var.set(f"Selected {len(self.selected_files)} files: {', '.join(file_names)}" + 
                                 (f" and {len(self.selected_files)-3} more..." if len(self.selected_files) > 3 else ""))
            
            # Provide visual feedback
            self.drop_label.configure(text="✅ Files added successfully!\n"
                                          "Drop more files or use the button above")
            self.root.after(3000, self._reset_drop_label_text)  # Reset after 3 seconds
            
        except Exception as e:
            self.logger.error(f"Error handling dropped files: {e}")
            messagebox.showerror("Error", f"Error processing dropped files: {e}")
    
    def _reset_drop_label_text(self):
        """Reset the drop label text to default"""
        try:
            if hasattr(self, 'drop_label'):
                self.drop_label.configure(text="📄 Drag and drop PDF files here\n"
                                              "or use the 'Select PDF Files' button above\n"
                                              "Supports multiple files and cross-platform drag & drop")
        except:
            pass  # Widget might be destroyed
        
    def select_output_directory(self):
        """Select output directory for translated files"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_directory = directory
            self.output_var.set(f"Output: {directory}")
            self.log_message(f"Output directory set to: {directory}")
            # Save configuration when output directory changes
            self.auto_save_configuration()
        
    def test_ollama_connection(self):
        """Test connection to Ollama server"""
        try:
            url = self.ollama_url_var.get().rstrip('/')
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.connection_status_var.set("✓ Connected to Ollama")
                self.connection_status_var.set("green")
                self.log_message("Successfully connected to Ollama server")
                return True
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            self.connection_status_var.set(f"✗ Connection failed: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to Ollama: {e}")
            self.log_message(f"Failed to connect to Ollama: {e}")
            return False
            
    def refresh_models(self):
        """Refresh available models from Ollama"""
        try:
            url = self.ollama_url_var.get().rstrip('/')
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                if models:
                    # Create a popup to show available models
                    model_window = tk.Toplevel(self.root)
                    model_window.title("Available Models")
                    model_window.geometry("400x300")
                    
                    ttk.Label(model_window, text="Available Ollama Models:", 
                             font=("Arial", 12, "bold")).pack(pady=10)
                    
                    listbox = tk.Listbox(model_window, height=10)
                    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    for model in models:
                        listbox.insert(tk.END, model)
                    
                    def select_model():
                        selection = listbox.curselection()
                        if selection:
                            selected_model = listbox.get(selection[0])
                            self.model_var.set(selected_model)
                            model_window.destroy()
                            self.log_message(f"Selected model: {selected_model}")
                    
                    ttk.Button(model_window, text="Select Model", 
                              command=select_model).pack(pady=10)
                else:
                    messagebox.showinfo("No Models", "No models found on Ollama server")
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch models: {e}")
            
    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def create_translator(self):
        """Create Ollama translator instance"""
        try:
            base_url = self.ollama_url_var.get().rstrip('/') + '/v1'
            model = self.model_var.get()
            api_key = self.api_key_var.get()
            
            self.translator = OllamaTranslator(
                lang_in=self.source_lang_var.get(),
                lang_out=self.target_lang_var.get(),
                model=model,
                base_url=base_url,
                api_key=api_key,
                ignore_cache=False
            )
            
            self.log_message(f"Created translator: {model} ({base_url})")
            return True
        except Exception as e:
            self.log_message(f"Failed to create translator: {e}")
            messagebox.showerror("Translator Error", f"Failed to create translator: {e}")
            return False
            
    def start_translation(self):
        """Start the translation process"""
        if self.is_translating:
            messagebox.showwarning("Translation in Progress", "Translation is already in progress")
            return
            
        # Validate inputs
        if not self.selected_files:
            messagebox.showerror("No Files", "Please select PDF files to translate")
            return
            
        if not self.test_ollama_connection():
            return
            
        if not self.create_translator():
            return
            
        # Start translation in a separate thread
        self.is_translating = True
        self.translate_button.config(text="Translating...", state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Starting translation...")
        
        threading.Thread(target=self.run_translation, daemon=True).start()
        
    def run_translation(self):
        """Run translation in a separate thread"""
        try:
            total_files = len(self.selected_files)
            
            for i, file_path in enumerate(self.selected_files):
                self.root.after(0, lambda f=file_path: self.status_var.set(f"Translating: {Path(f).name}"))
                self.root.after(0, lambda: self.log_message(f"Starting translation of: {Path(file_path).name}"))
                
                # Create translation configuration
                config = TranslationConfig(
                    translator=self.translator,
                    input_file=file_path,
                    lang_in=self.source_lang_var.get(),
                    lang_out=self.target_lang_var.get(),
                    doc_layout_model=DocLayoutModel.load_available(),
                    output_dir=self.output_directory or Path(file_path).parent,
                    qps=int(self.qps_var.get()),
                    no_dual=not self.dual_output_var.get(),
                    no_mono=not self.mono_output_var.get(),
                    debug=False,
                    skip_clean=False,
                    watermark_output_mode="no_watermark"
                )
                
                # Run translation asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    result = loop.run_until_complete(self.translate_file_async(config))
                    
                    # Update progress
                    progress = ((i + 1) / total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                    if result:
                        self.root.after(0, lambda: self.log_message(f"✓ Successfully translated: {Path(file_path).name}"))
                        if result.mono_pdf_path:
                            self.root.after(0, lambda: self.log_message(f"  Chinese PDF: {result.mono_pdf_path}"))
                        if result.dual_pdf_path:
                            self.root.after(0, lambda: self.log_message(f"  Dual-language PDF: {result.dual_pdf_path}"))
                    else:
                        self.root.after(0, lambda: self.log_message(f"✗ Failed to translate: {Path(file_path).name}"))
                        
                finally:
                    loop.close()
                    
            # Translation completed
            self.root.after(0, lambda: self.status_var.set("Translation completed!"))
            self.root.after(0, lambda: self.log_message("All translations completed successfully!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "All PDF files have been translated successfully!"))
            
        except Exception as e:
            error_msg = f"Translation failed: {e}"
            self.root.after(0, lambda: self.log_message(error_msg))
            self.root.after(0, lambda: self.status_var.set("Translation failed"))
            self.root.after(0, lambda: messagebox.showerror("Translation Error", error_msg))
        finally:
            self.is_translating = False
            self.root.after(0, lambda: self.translate_button.config(text="Start Translation", state="normal"))
            
    async def translate_file_async(self, config):
        """Translate a single file asynchronously with progress reporting"""
        try:
            async for event in babeldoc.format.pdf.high_level.async_translate(config):
                if event["type"] == "progress_update":
                    # Update progress (this is per-file progress)
                    stage_progress = event.get("overall_progress", 0)
                    self.root.after(0, lambda p=stage_progress: self.status_var.set(
                        f"Translating {Path(config.input_file).name}: {p:.1f}% ({event.get('stage', 'Processing')})"
                    ))
                elif event["type"] == "finish":
                    return event["translate_result"]
                elif event["type"] == "error":
                    raise Exception(event["error"])
            return None
        except Exception as e:
            self.logger.error(f"Translation error for {config.input_file}: {e}")
            raise


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = PDFTranslatorGUI(root)
    
    # Handle window closing
    def on_closing():
        # Save configuration before closing
        app.save_configuration()
        
        if app.is_translating:
            if messagebox.askokcancel("Quit", "Translation is in progress. Do you want to quit?"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
