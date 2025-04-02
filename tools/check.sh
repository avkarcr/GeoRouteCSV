#!/bin/bash

PORT_NOMINATIM=7070
PORT_ORS=8080

print_message() {
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    NC='\033[0m' # Нет цвета
    if [ "$2" == "success" ]; then
        echo -e "${GREEN}$1${NC}"
    else
        echo -e "${RED}$1${NC}"
    fi
}

# Проверка статуса Nominatim
nominatim_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT_NOMINATIM}/status)
if [ "$nominatim_status" == "200" ]; then
    print_message "Nominatim работает" "success"
else
    print_message "Nominatim не готов" "error"
fi

# Проверка статуса OpenRouteService
ors_status=$(curl -s http://localhost:${PORT_ORS}/ors/v2/health | jq -r .status)
if [ "$ors_status" == "ready" ]; then
    print_message "OpenRouteService работает" "success"
else
    print_message "OpenRouteService не готов" "error"
fi

