[#!/bin/bash

###############################################################################
# GITHUB CIT REPOSITORY DEEP ANALYSIS SCRIPT v1.0
# Назначение: Детальний аналіз структури GitHub репо для оркестрації
# Репозиторій: github.com/ihorog/cit
# Виконання: Copy-paste ready - БЕЗ ЗМІН
###############################################################################

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

GITHUB_USER="ihorog"
GITHUB_REPO="cit"
ANALYSIS_OUTPUT="$HOME/github_cit_analysis_$(date +%Y%m%d_%H%M%S).json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GITHUB CIT REPOSITORY ANALYSIS${NC}"
echo -e "${BLUE}  $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

###############################################################################
# ФУНКЦІЯ: GitHub API Helper (з fallback на git clone)
###############################################################################
get_repo_data() {
    echo -e "${CYAN}[1] Fetching Repository Metadata...${NC}"
    
    API_URL="https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO"
    
    # Спробуємо отримати дані через API
    REPO_DATA=$(curl -s "$API_URL" 2>/dev/null)
    
    if echo "$REPO_DATA" | grep -q '"message"'; then
        echo -e "${YELLOW}! GitHub API: $(echo "$REPO_DATA" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)${NC}"
    fi
    
    # Виводимо основну інформацію
    echo -e "${YELLOW}Repository Information:${NC}"
    echo "$REPO_DATA" | grep -o '"full_name":"[^"]*"' | head -1
    echo "$REPO_DATA" | grep -o '"description":"[^"]*"' | head -1
    echo "$REPO_DATA" | grep -o '"language":"[^"]*"' | head -1
    echo "$REPO_DATA" | grep -o '"watchers":[0-9]*' | head -1
    echo "$REPO_DATA" | grep -o '"forks":[0-9]*' | head -1
    echo "$REPO_DATA" | grep -o '"open_issues":[0-9]*' | head -1
}

###############################################################################
# ФУНКЦІЯ: Branches Analysis
###############################################################################
get_branches_info() {
    echo -e "\n${CYAN}[2] Analyzing Branches...${NC}"
    
    API_URL="https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/branches"
    
    echo -e "${YELLOW}Branches:${NC}"
    curl -s "$API_URL" 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | head -10 || echo "  (Cannot fetch via API)"
    
    # Якщо є локальний git репо, використовуємо його
    if [ -d "$HOME/cit/.git" ] || [ -d "$HOME/projects/cit/.git" ] 2>/dev/null; then
        CIT_DIR=$(find "$HOME" -maxdepth 3 -name "cit" -type d -path "*/.git" -parent 2>/dev/null | head -1)
        if [ -n "$CIT_DIR" ]; then
            echo -e "${YELLOW}Local Git Branches:${NC}"
            cd "$CIT_DIR" && git branch -a 2>/dev/null | grep -v detached || true
        fi
    fi
}

###############################################################################
# ФУНКЦІЯ: Recent Commits Analysis
###############################################################################
get_commits_info() {
    echo -e "\n${CYAN}[3] Analyzing Recent Commits...${NC}"
    
    API_URL="https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/commits?per_page=10"
    
    echo -e "${YELLOW}Recent 10 Commits:${NC}"
    
    curl -s "$API_URL" 2>/dev/null | grep -o '"message":"[^"]*"' | cut -d'"' -f4 | head -10 || echo "  (Cannot fetch via API)"
    
    # Альтернативно з локального git
    if [ -d "$HOME/cit/.git" ] 2>/dev/null; then
        echo -e "${YELLOW}Local Recent Commits:${NC}"
        cd "$HOME/cit" && git log --oneline -10 2>/dev/null || true
    fi
}

###############################################################################
# ФУНКЦІЯ: Repository Structure Analysis
###############################################################################
analyze_repo_structure() {
    echo -e "\n${CYAN}[4] Repository Structure Analysis...${NC}"
    
    # Пробуємо скопіювати репо тимчасово для аналізу
    TEMP_CLONE="$HOME/temp_cit_analysis_$$"
    
    echo -e "${YELLOW}Cloning repository for analysis...${NC}"
    
    if git clone --depth 1 "https://github.com/$GITHUB_USER/$GITHUB_REPO.git" "$TEMP_CLONE" 2>/dev/null; then
        echo -e "${GREEN}✓ Repository cloned${NC}"
        
        echo -e "\n${YELLOW}Main Directory Structure:${NC}"
        cd "$TEMP_CLONE" && find . -maxdepth 2 -type d | grep -v ".git" | sort
        
        echo -e "\n${YELLOW}Configuration Files:${NC}"
        cd "$TEMP_CLONE" && ls -la | grep -E "(\\.env|\\.config|config|settings|package\\.json|requirements|Dockerfile|docker-compose|setup\\.py)" || echo "  (None found)"
        
        echo -e "\n${YELLOW}Root Files:${NC}"
        cd "$TEMP_CLONE" && ls -1 | head -15
        
        echo -e "\n${YELLOW}Main Code Files:${NC}"
        cd "$TEMP_CLONE" && find . -maxdepth 2 -type f \( -name "*.py" -o -name "*.js" -o -name "*.json" -o -name "*.ts" \) | head -20
        
        echo -e "\n${YELLOW}Documentation:${NC}"
        cd "$TEMP_CLONE" && ls -1 *.md 2>/dev/null || echo "  (No README.md found)"
        
        # Очищаємо тимчасовий клон
        rm -rf "$TEMP_CLONE"
    else
        echo -e "${RED}! Cannot clone repository${NC}"
        echo -e "${YELLOW}Trying to use local cache if available...${NC}"
        
        if [ -d "$HOME/cit" ]; then
            cd "$HOME/cit"
            echo -e "${YELLOW}Local CIT Directory Structure:${NC}"
            find . -maxdepth 2 -type d | grep -v ".git" | sort
            
            echo -e "\n${YELLOW}Configuration Files:${NC}"
            ls -la | grep -E "(\\.env|\\.config|config|settings|package\\.json|requirements)" || echo "  (None found)"
        fi
    fi
}

###############################################################################
# ФУНКЦІЯ: File Types Distribution
###############################################################################
analyze_file_types() {
    echo -e "\n${CYAN}[5] File Types Distribution...${NC}"
    
    if [ -d "$HOME/cit" ]; then
        echo -e "${YELLOW}File Count by Type:${NC}"
        cd "$HOME/cit" && find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15 || echo "  (Cannot analyze)"
        
        echo -e "\n${YELLOW}Python Files:${NC}"
        cd "$HOME/cit" && find . -name "*.py" -type f | wc -l
        echo "  Main: $(find . -maxdepth 1 -name "*.py" -type f | wc -l)"
        echo "  In modules: $(find . -maxdepth 2 -name "*.py" -type f | wc -l)"
        
        echo -e "\n${YELLOW}JavaScript/TypeScript Files:${NC}"
        cd "$HOME/cit" && find . \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) -type f | wc -l
        
        echo -e "\n${YELLOW}Configuration Files:${NC}"
        cd "$HOME/cit" && ls -1 .env* package.json setup.py requirements.txt docker-compose.yml 2>/dev/null || echo "  (Standard config files not found)"
    fi
}

###############################################################################
# ФУНКЦІЯ: Dependencies & Requirements
###############################################################################
extract_dependencies() {
    echo -e "\n${CYAN}[6] Dependencies & Requirements Analysis...${NC}"
    
    if [ -f "$HOME/cit/requirements.txt" ]; then
        echo -e "${YELLOW}Python Dependencies (requirements.txt):${NC}"
        head -20 "$HOME/cit/requirements.txt"
        echo "... and $(wc -l < "$HOME/cit/requirements.txt") total"
    fi
    
    if [ -f "$HOME/cit/package.json" ]; then
        echo -e "\n${YELLOW}Node Dependencies (package.json):${NC}"
        grep -A 20 '"dependencies"' "$HOME/cit/package.json" || echo "  (Cannot parse)"
    fi
    
    if [ -f "$HOME/cit/setup.py" ]; then
        echo -e "\n${YELLOW}Setup.py Configuration:${NC}"
        grep -E "(name=|version=|install_requires)" "$HOME/cit/setup.py" | head -10
    fi
}

###############################################################################
# ФУНКЦІЯ: API Endpoints Discovery
###############################################################################
discover_api_endpoints() {
    echo -e "\n${CYAN}[7] API Endpoints Discovery...${NC}"
    
    if [ -d "$HOME/cit" ]; then
        echo -e "${YELLOW}Searching for API routes (Flask/FastAPI patterns):${NC}"
        
        # Flask routes
        cd "$HOME/cit" && grep -r "@app\\.route\|@router\\.get\|@router\\.post" --include="*.py" 2>/dev/null | head -15 || echo "  (No Flask routes found)"
        
        # FastAPI routes
        cd "$HOME/cit" && grep -r "@.*\\.get(\|@.*\\.post(" --include="*.py" 2>/dev/null | head -15 || echo "  (No FastAPI routes found)"
    fi
}

###############################################################################
# ФУНКЦІЯ: Environment & Configuration Detection
###############################################################################
detect_configuration() {
    echo -e "\n${CYAN}[8] Configuration & Environment Detection...${NC}"
    
    if [ -f "$HOME/cit/.env.example" ]; then
        echo -e "${YELLOW}Required Environment Variables (.env.example):${NC}"
        cat "$HOME/cit/.env.example"
    elif [ -f "$HOME/cit/.env" ]; then
        echo -e "${YELLOW}Environment Variables (.env):${NC}"
        grep -v "^#" "$HOME/cit/.env" | grep -v "^$" | sed 's/=.*/=***/' || echo "  (Cannot read)"
    else
        echo -e "${YELLOW}No .env files found - checking for hardcoded config...${NC}"
        cd "$HOME/cit" && grep -r "API_KEY\|SECRET\|TOKEN\|URL\|HOST\|PORT" --include="*.py" --include="*.js" 2>/dev/null | head -10 || echo "  (None found)"
    fi
}

###############################################################################
# ФУНКЦІЯ: Docker Configuration (якщо є)
###############################################################################
check_docker_setup() {
    echo -e "\n${CYAN}[9] Docker Configuration...${NC}"
    
    if [ -f "$HOME/cit/Dockerfile" ]; then
        echo -e "${YELLOW}Dockerfile found:${NC}"
        head -15 "$HOME/cit/Dockerfile"
    else
        echo -e "${YELLOW}No Dockerfile${NC}"
    fi
    
    if [ -f "$HOME/cit/docker-compose.yml" ]; then
        echo -e "\n${YELLOW}Docker Compose Configuration:${NC}"
        head -20 "$HOME/cit/docker-compose.yml"
    else
        echo -e "${YELLOW}No docker-compose.yml${NC}"
    fi
}

###############################################################################
# ФУНКЦІЯ: Generate Summary JSON
###############################################################################
generate_summary() {
    echo -e "\n${CYAN}[10] Generating Analysis Summary...${NC}"
    
    {
        echo "{"
        echo "  \"analysis_timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
        echo "  \"repository\": {"
        echo "    \"owner\": \"$GITHUB_USER\","
        echo "    \"name\": \"$GITHUB_REPO\","
        echo "    \"url\": \"https://github.com/$GITHUB_USER/$GITHUB_REPO\""
        echo "  },"
        echo "  \"local_paths\": {"
        echo "    \"cit_home\": \"$HOME/cit\","
        echo "    \"temp_clone\": \"$TEMP_CLONE\","
        echo "    \"storage\": \"$HOME/storage/downloads\""
        echo "  },"
        echo "  \"analysis_files\": {"
        echo "    \"diagnostic_report\": \"$ANALYSIS_OUTPUT\""
        echo "  },"
        echo "  \"commands_for_next_step\": ["
        echo "    \"cd $HOME/cit && git pull origin main\","
        echo "    \"cd $HOME/cit && pip3 install -r requirements.txt\","
        echo "    \"python3 $HOME/cit/main.py\","
        echo "    \"curl http://localhost:8790/health\""
        echo "  ]"
        echo "}"
    } > "$ANALYSIS_OUTPUT"
    
    echo -e "${GREEN}✓ Analysis summary saved to: $ANALYSIS_OUTPUT${NC}"
}

###############################################################################
# MAIN EXECUTION
###############################################################################

get_repo_data
get_branches_info
get_commits_info
analyze_repo_structure
analyze_file_types
extract_dependencies
discover_api_endpoints
detect_configuration
check_docker_setup
generate_summary

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ANALYSIS COMPLETE${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next commands:${NC}"
echo "1. View JSON summary: cat $ANALYSIS_OUTPUT"
echo "2. Clone fresh repo: cd $HOME && git clone https://github.com/$GITHUB_USER/$GITHUB_REPO.git"
echo "3. Install deps: pip3 install -r $HOME/cit/requirements.txt"
echo ""]
