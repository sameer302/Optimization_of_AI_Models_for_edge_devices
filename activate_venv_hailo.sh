#!/bin/bash

source /home/sameer/Desktop/optimization_of_ai_models/hailo-apps/venv_hailo_apps/bin/activate

# Add project root to PYTHONPATH (this allows imports from the project in any subdirectory and this change lasts for one terminal session)
export PYTHONPATH="/home/sameer/Desktop/optimization_of_ai_models/hailo-apps:$PYTHONPATH"
# To use this script, run:
#   source activate_venv_hailo.sh