#!/usr/bin/env python3
"""
File watcher for live module reload and diagram regeneration.

Monitors the modules directory for changes and automatically regenerates
the diagram and metadata files when YAML modules are modified.
"""

import argparse
import time
import logging
from pathlib import Path
from typing import Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from loader import load_modules
from graph_builder import generate_diagram_file, generate_module_metadata


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModuleWatcher(FileSystemEventHandler):
    """
    File system event handler for module YAML files.
    
    Monitors changes to YAML files and triggers diagram regeneration.
    """
    
    def __init__(self, modules_dir: str, output_dir: str = "static", 
                 debounce_delay: float = 1.0):
        """
        Initialize module watcher.
        
        Args:
            modules_dir: Directory to watch for module changes
            output_dir: Directory to write generated files
            debounce_delay: Delay in seconds to debounce rapid changes
        """
        self.modules_dir = Path(modules_dir)
        self.output_dir = Path(output_dir)
        self.debounce_delay = debounce_delay
        self.pending_changes: Set[str] = set()
        self.last_change_time = 0
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Watching {self.modules_dir} for changes...")
        logger.info(f"Output directory: {self.output_dir}")
    
    def on_modified(self, event):
        """Handle file modification events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_yaml_file(src_path):
            self._handle_change(src_path, "modified")
    
    def on_created(self, event):
        """Handle file creation events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_yaml_file(src_path):
            self._handle_change(src_path, "created")
    
    def on_deleted(self, event):
        """Handle file deletion events."""
        src_path = str(event.src_path)
        if not event.is_directory and self._is_yaml_file(src_path):
            self._handle_change(src_path, "deleted")
    
    def _is_yaml_file(self, file_path: str) -> bool:
        """Check if file is a YAML module file."""
        path = Path(file_path)
        return path.suffix.lower() in ['.yaml', '.yml']
    
    def _handle_change(self, file_path: str, change_type: str):
        """
        Handle file system change with debouncing.
        
        Args:
            file_path: Path to the changed file
            change_type: Type of change (modified, created, deleted)
        """
        current_time = time.time()
        self.last_change_time = current_time
        self.pending_changes.add(file_path)
        
        logger.info(f"File {change_type}: {file_path}")
        
        # Schedule regeneration after debounce delay
        def delayed_regenerate():
            time.sleep(self.debounce_delay)
            if time.time() - self.last_change_time >= self.debounce_delay:
                self._regenerate_files()
        
        import threading
        threading.Thread(target=delayed_regenerate, daemon=True).start()
    
    def _regenerate_files(self):
        """Regenerate diagram and metadata files."""
        if not self.pending_changes:
            return
        
        try:
            logger.info("Regenerating diagram and metadata...")
            
            # Handle invalid module temporarily
            invalid_file = self.modules_dir / "invalid_module.yaml"
            backup_file = self.modules_dir / "invalid_module.yaml.bak"
            invalid_exists = invalid_file.exists()
            
            if invalid_exists:
                invalid_file.rename(backup_file)
            
            try:
                # Load modules
                modules = load_modules(str(self.modules_dir))
                
                if modules:
                    # Generate diagram file
                    diagram_path = self.output_dir / "diagram.mmd"
                    generate_diagram_file(modules, diagram_path)
                    
                    # Generate metadata file
                    metadata_path = self.output_dir / "modules.json"
                    generate_module_metadata(modules, metadata_path)
                    
                    logger.info(f"Successfully regenerated files for {len(modules)} modules")
                    
                    # Log the changed files
                    for file_path in self.pending_changes:
                        logger.info(f"  Processed: {Path(file_path).name}")
                else:
                    logger.warning("No valid modules found")
                    
            finally:
                # Restore invalid module
                if invalid_exists and backup_file.exists():
                    backup_file.rename(invalid_file)
                
        except Exception as e:
            logger.error(f"Error regenerating files: {e}")
        finally:
            self.pending_changes.clear()


class WatcherManager:
    """Manager for the file watching system."""
    
    def __init__(self, modules_dir: str, output_dir: str = "static"):
        """
        Initialize watcher manager.
        
        Args:
            modules_dir: Directory to watch for module changes
            output_dir: Directory to write generated files
        """
        self.modules_dir = modules_dir
        self.output_dir = output_dir
        self.observer = None
        self.event_handler = None
        
        # Log file for tracking changes
        self.log_file = Path("build_logs/phase_4.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start the file watcher."""
        if self.observer and self.observer.is_alive():
            logger.warning("Watcher is already running")
            return
        
        # Create event handler
        self.event_handler = ModuleWatcher(self.modules_dir, self.output_dir)
        
        # Create and configure observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(Path(self.modules_dir).resolve()),
            recursive=False
        )
        
        # Start observer
        self.observer.start()
        logger.info("File watcher started successfully")
        
        # Log to file
        with open(self.log_file, 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Watcher started\n")
        
        # Generate initial files
        self.event_handler._regenerate_files()
    
    def stop(self):
        """Stop the file watcher."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")
            
            # Log to file
            with open(self.log_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Watcher stopped\n")
        else:
            logger.warning("Watcher is not running")
    
    def run_forever(self):
        """Run the watcher in blocking mode."""
        self.start()
        
        try:
            logger.info("Press Ctrl+C to stop the watcher")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()


def main():
    """CLI entry point for the file watcher."""
    parser = argparse.ArgumentParser(
        description="Watch module directory for changes and regenerate diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watcher.py modules/
  python watcher.py modules/ --output static/
  python watcher.py modules/ --quiet
        """
    )
    
    parser.add_argument(
        "modules_dir",
        help="Directory containing YAML module files to watch"
    )
    
    parser.add_argument(
        "--output",
        default="static",
        help="Output directory for generated files (default: static)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce logging output"
    )
    
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Generate files once and exit (don't watch)"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Validate modules directory
    modules_path = Path(args.modules_dir)
    if not modules_path.exists():
        logger.error(f"Modules directory does not exist: {args.modules_dir}")
        return 1
    
    if not modules_path.is_dir():
        logger.error(f"Path is not a directory: {args.modules_dir}")
        return 1
    
    # Create watcher manager
    manager = WatcherManager(args.modules_dir, args.output)
    
    if args.single_run:
        # Generate files once and exit
        logger.info("Running single generation...")
        event_handler = ModuleWatcher(args.modules_dir, args.output)
        event_handler._regenerate_files()
        logger.info("Generation complete")
    else:
        # Run watcher continuously
        manager.run_forever()
    
    return 0


if __name__ == "__main__":
    exit(main()) 