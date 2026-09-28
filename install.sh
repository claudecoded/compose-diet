#!/usr/bin/env bash

# ==============================================================================
# COMMIT-PILOT ACCELERATOR KEYBIND INSTALLER
# Binds the standalone Node executable script as a global profile shortcut.
# ==============================================================================

set -euo pipefail

TARGET_INSTALL_DIR="/usr/local/bin"
BIN_NAME="copilot-commit"
CURRENT_DIR="$(pwd)"

echo -e "\033[0;34m[*] Orchestrating Commit-Pilot global alias deployment...\033[0m"

# Build an executable shell symlink hook wrapper linking paths directly
cat << EOF > "$BIN_NAME"
#!/usr/bin/env bash
node "$CURRENT_DIR/commit_pilot.js" "\$@"
EOF

# Grant absolute local executable rights permissions loops
chmod +x "$BIN_NAME"
chmod +x commit_pilot.js

if [ -w "$TARGET_INSTALL_DIR" ]; then
    mv "$BIN_NAME" "$TARGET_INSTALL_DIR/"
    echo -e "\033[0;32m[SUCCESS] Superpower loaded! You can now type '\033[1mcopilot-commit\033[0;32m' inside ANY git repository folder!\033[0m"
else
    echo -e "\033[0;33m[Permission Required] Sudo authorization required to copy binary into: $TARGET_INSTALL_DIR\033[0m"
    sudo mv "$BIN_NAME" "$TARGET_INSTALL_DIR/"
    echo -e "\033[0;32m[SUCCESS] Superpower loaded! Global terminal keyword active.\033[0m"
fi
