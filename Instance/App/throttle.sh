#!/bin/bash

# Pre-requisitos: stress-ng, bc, procps-ng
# Intentar usar nproc si existe, si no, usar variable de entorno o fallback
if command -v nproc > /dev/null; then
    CORES=$(nproc)
else
    CORES=${NUMBER_OF_PROCESSORS:-2}
fi
GLOBAL_THROTTLE_FILE="/tmp/global_throttle"
echo "0" > "$GLOBAL_THROTTLE_FILE"

run_core_throttle() {
    local core=$1
    local current_load=0
    
    while true; do
        # 30% de probabilidad de tranquilidad total (0% carga por más tiempo)
        if [ $((RANDOM % 10)) -lt 3 ]; then
            local target_base=0
            local duration=$(( (RANDOM % 8) + 10 ))
        else
            local target_base=$(( (RANDOM % 11) * 10 ))
            local duration=$(( (RANDOM % 6) + 3 ))
        fi

        local global_offset=$(cat "$GLOBAL_THROTTLE_FILE" 2>/dev/null || echo "0")
        
        # Aumentamos a 5 pasos de easing para mayor suavidad
        local steps=5
        # Asegurar que el número tenga un 0 inicial para evitar errores en stress-ng
        local step_dur=$(echo "scale=2; $duration / $steps" | bc | sed 's/^\./0./')
        [ "$step_dur" == "0" ] && step_dur="0.5" # Fallback mínimo
        
        local load_diff=$((target_base - current_load))
        
        for s in $(seq 1 $steps); do
            # Cálculo de carga progresiva
            local base_load=$(( current_load + (load_diff * s / steps) ))
            local final_load=$(( base_load + global_offset ))
            
            [ "$final_load" -gt 100 ] && final_load=100
            [ "$final_load" -lt 0 ] && final_load=0
            
            # Limpiar proceso previo del core antes del siguiente paso
            pkill -f "stress-ng.*--taskset $core" 2>/dev/null
            
            if [ "$final_load" -gt 0 ]; then
                stress-ng --cpu 1 --cpu-load "$final_load" --taskset "$core" --timeout "${step_dur}s" --quiet &
            fi
            sleep "$step_dur"
        done
        current_load=$target_base
    done
}

# Lanzar un manejador por cada core (excepto el Core 0)
for i in $(seq 1 $((CORES - 1))); do
    run_core_throttle "$i" &
done

# Mantener el script principal vivo
wait
