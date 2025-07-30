#!/bin/bash

# Setup Project-Specific Color Theme for Cursor IDE
# Usage: ./setup_project_theme.sh [theme_name]
# If no theme is provided, it will prompt you to choose from options

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to display header
show_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║        Project Theme Setup Script        ║${NC}"
    echo -e "${PURPLE}║     Set Cursor IDE theme for project     ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
    echo
}

# Available themes with descriptions
declare -A themes=(
    ["Default Dark Modern"]="Modern dark theme with balanced colors"
    ["Default Light Modern"]="Modern light theme with clean appearance"
    ["Dark+ (default dark)"]="VS Code classic dark theme"
    ["Light+ (default light)"]="VS Code classic light theme"
    ["One Dark Pro"]="Popular Atom-inspired dark theme"
    ["Dracula"]="Dark theme with vibrant colors"
    ["Monokai"]="Classic dark theme with high contrast"
    ["Solarized Dark"]="Easy on eyes dark theme"
    ["Solarized Light"]="Easy on eyes light theme"
    ["Abyss"]="Very dark theme for focused coding"
    ["Quiet Light"]="Minimal light theme"
    ["Nord"]="Arctic-inspired blue theme"
    ["Gruvbox Dark Hard"]="Retro dark theme with warm colors"
    ["Material Theme"]="Google Material Design inspired"
    ["Tomorrow Night Blue"]="Blue-tinted dark theme"
)

# Function to display theme options
show_theme_options() {
    echo -e "${YELLOW}Available Color Themes:${NC}"
    echo -e "${YELLOW}═══════════════════════${NC}"
    echo
    
    local counter=1
    for theme in "${!themes[@]}"; do
        echo -e "${BLUE}$counter.${NC} ${GREEN}$theme${NC}"
        echo -e "   ${CYAN}${themes[$theme]}${NC}"
        echo
        ((counter++))
    done
}

# Function to get user choice
get_user_choice() {
    local theme_array=()
    for theme in "${!themes[@]}"; do
        theme_array+=("$theme")
    done
    
    # Sort themes for consistent ordering
    IFS=$'\n' sorted_themes=($(sort <<<"${theme_array[*]}"))
    unset IFS
    
    echo -e "${YELLOW}Enter the number of your preferred theme (1-${#sorted_themes[@]}):${NC}"
    read -p "Choice: " choice
    
    # Validate input
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#sorted_themes[@]}" ]; then
        selected_theme="${sorted_themes[$((choice-1))]}"
        echo -e "${GREEN}Selected: $selected_theme${NC}"
        return 0
    else
        echo -e "${RED}Invalid choice. Please enter a number between 1 and ${#sorted_themes[@]}.${NC}"
        return 1
    fi
}

# Function to create .vscode directory if it doesn't exist
create_vscode_dir() {
    if [ ! -d ".vscode" ]; then
        mkdir -p .vscode
        echo -e "${GREEN}Created .vscode directory${NC}"
    fi
}

# Function to generate settings.json content
generate_settings_json() {
    local theme_name="$1"
    
    cat > .vscode/settings.json << EOF
{
  "workbench.colorTheme": "$theme_name",
  "workbench.preferredDarkColorTheme": "$theme_name",
  "workbench.preferredLightColorTheme": "$theme_name",
  
  // Enhanced syntax highlighting for better code readability
  "editor.tokenColorCustomizations": {
    "comments": "#6A9955",
    "strings": "#CE9178",
    "keywords": "#569CD6",
    "numbers": "#B5CEA8",
    "types": "#4EC9B0",
    "functions": "#DCDCAA",
    "variables": "#9CDCFE"
  },
  
  // Semantic highlighting for better code visualization
  "editor.semanticHighlighting.enabled": true,
  
  // Bracket colorization for better code structure
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": "active",
  
  // Enhanced editor features
  "editor.guides.indentation": true,
  "editor.renderWhitespace": "boundary",
  "editor.renderControlCharacters": false,
  
  // File icon theme
  "workbench.iconTheme": "vs-seti",
  
  // Additional enhancements
  "editor.cursorBlinking": "smooth",
  "editor.fontLigatures": true,
  "editor.minimap.enabled": true,
  "editor.minimap.maxColumn": 120,
  
  // Terminal theming
  "terminal.integrated.fontFamily": "monospace",
  "terminal.integrated.fontSize": 14,
  
  // Workbench enhancements
  "workbench.editor.enablePreview": false,
  "workbench.editor.showTabs": true,
  "workbench.activityBar.visible": true,
  "workbench.statusBar.visible": true
}
EOF
}

# Function to backup existing settings
backup_existing_settings() {
    if [ -f ".vscode/settings.json" ]; then
        cp .vscode/settings.json .vscode/settings.json.backup
        echo -e "${YELLOW}Backed up existing settings to .vscode/settings.json.backup${NC}"
    fi
}

# Function to show completion message
show_completion_message() {
    local theme_name="$1"
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            Setup Complete!               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo
    echo -e "${BLUE}Theme Applied:${NC} ${GREEN}$theme_name${NC}"
    echo -e "${BLUE}Project Directory:${NC} ${GREEN}$(pwd)${NC}"
    echo -e "${BLUE}Settings File:${NC} ${GREEN}.vscode/settings.json${NC}"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "1. ${CYAN}Reload Cursor IDE${NC} (Ctrl+Shift+P → 'Developer: Reload Window')"
    echo -e "2. ${CYAN}The theme will only apply to this project${NC}"
    echo -e "3. ${CYAN}Your global theme settings remain unchanged${NC}"
    echo
    echo -e "${PURPLE}Tip: You can edit .vscode/settings.json to customize further!${NC}"
}

# Main script logic
main() {
    show_header
    
    # Check if theme name was provided as argument
    if [ -n "$1" ]; then
        selected_theme="$1"
        if [[ -n "${themes[$selected_theme]}" ]]; then
            echo -e "${GREEN}Using provided theme: $selected_theme${NC}"
        else
            echo -e "${YELLOW}Theme '$selected_theme' not in predefined list, but will be used anyway.${NC}"
        fi
    else
        # No argument provided, show interactive menu
        show_theme_options
        
        # Get user choice with validation loop
        while true; do
            if get_user_choice; then
                break
            fi
            echo
        done
    fi
    
    # Create .vscode directory
    create_vscode_dir
    
    # Backup existing settings if they exist
    backup_existing_settings
    
    # Generate settings.json
    echo -e "${BLUE}Generating settings.json...${NC}"
    generate_settings_json "$selected_theme"
    
    # Show completion message
    show_completion_message "$selected_theme"
}

# Run main function with all arguments
main "$@" 