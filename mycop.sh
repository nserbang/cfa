#!/bin/bash

# Source and destination directories
SRC_DIR="new"
DEST_DIR="cfa_server"

# List of files to copy
files=(
  "api/admin.py"
  "api/forms/case.py"
  "api/middleware.py"
  "api/mixins.py"
  "api/models.py"
  "api/npr.py"
  "api/otp.py"
  "api/serializers.py"
  "api/templates/_base.html"
  "api/templates/case/case_card.html"
  "api/templates/case/case_history_json.html"
  "api/templates/case/drug.html"
  "api/templates/case/extortion.html"
  "api/templates/case/side_menu.html"
  "api/templates/case/vehicle.html"
  "api/templates/dashboard.html"
  "api/templates/home.html"
  "api/templates/index.html"
  "api/templates/information.html"
  "api/templates/login.html"
  "api/templates/master.html"
  "api/templates/navigation.html"
  "api/templates/register.html"
  "api/viewset/case.py"
  "api/viewset/emergency.py"
  "api/views.py"
  "cfa_server/settings.py"
  "cfa_server/urls.py"
)

for file in "${files[@]}"; do
  src_path="$SRC_DIR/$file"
  dest_path="$DEST_DIR/$file"
  
  # Create destination directory if it doesn't exist
  mkdir -p "$(dirname "$dest_path")"
  
  # Copy the file
  cp "$src_path" "$dest_path"
  
  echo "Copied $src_path to $dest_path"
done
