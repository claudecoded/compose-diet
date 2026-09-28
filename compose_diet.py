#!/usr/bin/env python3
import os
import sys
import re
import json

# ==============================================================================
# COMPOSE-DIET: Autonomous Docker-Compose Shrinker & Memory Optimizer
# Analyzes and downscales massive multi-container architectures into micro-setups.
# ==============================================================================

# --- Terminal ANSI Color Schemes ---
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
WHITE = '\033[1;37m'
RESET = '\033[0m'
BOLD = '\033[1'

def log_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")
def log_success(msg): print(f"{GREEN}[SUCCESS]{RESET} {msg}")
def log_warn(msg): print(f"{YELLOW}[WARNING]{RESET} {msg}")
def log_error(msg): print(f"{RED}[ERROR]{RESET} {msg}")

def native_yaml_parse(file_path):
    """Resilient minimalist regex-based YAML block parser avoiding heavy PyYAML weights."""
    if not os.path.exists(file_path):
        log_error(f"Target docker-compose manifest file missing at: {file_path}")
        sys.exit(1)
        
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    services = {}
    current_service = None
    in_services_block = False
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
            
        # Detect core services definition block sequence boundary
        if stripped.startswith('services:'):
            in_services_block = True
            continue
            
        if in_services_block:
            leading_spaces = len(line) - len(line.lstrip())
            
            # Root service keyword definition scanner matching indentation grids
            if leading_spaces == 2 or leading_spaces == 4:
                if stripped.endswith(':'):
                    current_service = stripped[:-1]
                    services[current_service] = {
                        "raw_lines": [],
                        "dependencies": [],
                        "is_essential": False
                    }
                    indent_level = leading_spaces
                    continue
            
            if current_service and leading_spaces > indent_level:
                services[current_service]["raw_lines"].append(line)
                # Heuristic mapping analyzer searching for operational couplings links
                if "depends_on:" in stripped or "links:" in stripped:
                    pass
                elif stripped.startswith('-') and len(services[current_service]["raw_lines"]) > 1:
                    prev_line = services[current_service]["raw_lines"][-2].strip()
                    if "depends_on:" in prev_line or "- " in stripped:
                        dep_name = stripped.replace('-', '').replace(':', '').strip()
                        services[current_service]["dependencies"].append(dep_name)

    return services
def compute_dependency_tree(services, target_node, visited=None):
    """Recursively walks the topological layout map tracking up required downstreams."""
    if visited is None:
        visited = set()
    
    if target_node not in services or target_node in visited:
        return visited
        
    visited.add(target_node)
    services[target_node]["is_essential"] = True
    
    for dependency in services[target_node]["dependencies"]:
        # Clean clean naming anomalies or state configs references mapping values
        clean_dep = dependency.split(':')[0].strip()
        compute_dependency_tree(services, clean_dep, visited)
        
    return visited

def generate_diet_compose(source_path, output_path, services_matrix):
    """Outputs a highly optimized downscaled docker-compose structural manifest."""
    with open(source_path, 'r') as f:
        original_lines = f.readlines()
        
    diet_lines = []
    skip_mode = False
    current_checking_service = None
    in_services_section = False
    
    for line in original_lines:
        stripped = line.strip()
        
        if stripped.startswith('services:'):
            in_services_section = True
            diet_lines.append(line)
            continue
            
        if in_services_section:
            leading_spaces = len(line) - len(line.lstrip())
            
            if leading_spaces == 2 or leading_spaces == 4:
                if stripped.endswith(':'):
                    current_checking_service = stripped[:-1]
                    if current_checking_service in services_matrix:
                        if not services_matrix[current_checking_service]["is_essential"]:
                            skip_mode = True
                            log_warn(f"Placing container on a diet -> Trimmed service: {YELLOW}{current_checking_service}{RESET}")
                        else:
                            skip_mode = False
                            diet_lines.append(line)
                    else:
                        skip_mode = False
                        diet_lines.append(line)
                    continue
            
            if leading_spaces == 0 and stripped and not stripped.startswith('#'):
                in_services_section = False
                skip_mode = False
                
        if not skip_mode:
            if not in_services_section or current_checking_service is None:
                diet_lines.append(line)
            elif in_services_section and current_checking_service and services_matrix.get(current_checking_service, {}).get("is_essential"):
                diet_lines.append(line)

    with open(output_path, 'w') as f:
        f.writelines(diet_lines)
    log_success(f"Optimized diet manifest saved successfully at: {GREEN}{output_path}{RESET}")
def main():
    print(f"{CYAN}======================================================================{RESET}")
    print(f"{WHITE}       COMPOSE-DIET: AUTONOMOUS DOCKER-COMPOSE SHRINKER ENGINE       {RESET}")
    print(f"{CYAN}======================================================================{RESET}\n")
    
    source_file = "docker-compose.yml"
    output_file = "docker-compose.diet.yml"
    
    if not os.path.exists(source_file):
        log_error(f"Root file '{source_file}' not detected in this folder paths location grid.")
        sys.exit(1)
        
    log_info(f"Analyzing configuration schemas inside: {YELLOW}{source_file}{RESET}...")
    services = native_yaml_parse(source_file)
    
    if not services:
        log_error("No valid executable services discovered inside the target structural file.")
        sys.exit(1)
        
    print(f"\n{WHITE}Available services mapped inside your orchestration layout:{RESET}")
    service_keys = list(services.keys())
    for index, s_name in enumerate(service_keys):
        deps_count = len(services[s_name]["dependencies"])
        print(f"  [{CYAN}{index}{RESET}] -> {BOLD}{s_name}{RESET} ({YELLOW}{deps_count} downstreams mapped{RESET})")
        
    print(f"\n{WHITE}Select the index integer of the core service you are working on today:{RESET}")
    try:
        user_choice = int(input(f"{WHITE}compose-diet@cli:~# {RESET}").strip())
        if user_choice < 0 or user_choice >= len(service_keys):
            raise ValueError()
    except (ValueError, KeyboardInterrupt):
        log_error("Invalid parameters integer boundaries selection array indices mapping. Aborting.")
        sys.exit(1)
        
    target_service = service_keys[user_choice]
    log_info(f"Target locked onto focused development workflow environment: {GREEN}{target_service}{RESET}")
    
    # Run structural path calculations dependencies trace pruning
    essential_set = compute_dependency_tree(services, target_service)
    
    log_info(f"Essential runtime context cluster includes: {CYAN}{list(essential_set)}{RESET}")
    generate_diet_compose(source_file, output_file, services)
    
    print(f"\n{GREEN}[✓] PIPELINE ARCHITECTURE COMPLETE{RESET}")
    print(f"To spin up your ultra-light operational infrastructure context layout, run:")
    print(f"👉 {BOLD}docker-compose -f {output_file} up --build{RESET}\n")

if __name__ == '__main__':
    main()
