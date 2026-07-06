# Installation Guide
**Get Studioworks Core running in under 10 minutes**

---

## Prerequisites

Before we start, make sure you have:

- [ ] **Ableton Live 11 or newer** (any edition - Intro, Standard, or Suite)
- [ ] **Python 3.10 or higher** ([Download here](https://www.python.org/downloads/))
- [ ] **Git** command-line tool.
- [ ] **Claude Desktop** or **Cursor IDE** ([Claude](https://claude.ai/download) | [Cursor](https://cursor.sh/)) | **Gemini CLI** works, but I've tested it and it's nowhere as good as the previous.
- [ ] **15 minutes** of uninterrupted time
- [ ] **Administrator privileges** on your computer

---

## Installation Steps

The installation process involves three main steps: getting the code, installing the remote script in Ableton, and configuring your AI assistant.

### Step 1: Get the Code

First, clone the repository and install the required Python package.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/mumumedia/studioworks-core.git
    cd studioworks-core
    ```

2.  **Create a Virtual Environment and Install the Package:**

    First create a virtual environment (required on modern macOS; recommended on all platforms):

    **🍎 macOS:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

    **🪟 Windows (PowerShell):**
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -e .
    ```

    **🪟 Windows (Command Prompt):**
    ```cmd
    python -m venv .venv
    .venv\Scripts\activate.bat
    pip install -e .
    ```

    > **Got `externally-managed-environment` error?** This means your system Python requires a virtual environment — use the `python3 -m venv` steps above.

3.  **Verify Installation:**
    Run the following command. A success message indicates the Python component is correctly installed.

    **🍎 macOS:**
    ```bash
    python3 -c "from mcp.server.fastmcp import FastMCP; print('✅ Python package installed successfully!')"
    ```

    **🪟 Windows:**
    ```bash
    python -c "from mcp.server.fastmcp import FastMCP; print('✅ Python package installed successfully!')"
    ```

---

### Step 2: Install the Ableton Remote Script

Ableton Live loads control scripts from a specific user directory.

Your Ableton Remote Scripts location depends on your operating system:

![image](https://github.com/user-attachments/assets/24997e12-8a80-433f-9070-ac72be684a87)

#### 🪟 Windows
```
C:\Users\[YourUsername]\Documents\Ableton\User Library\Remote Scripts\
```
**Quick way to find it:**
1. Open **File Explorer**
2. Paste this in the address bar: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts`
3. Press **Enter**

#### 🍎 macOS

**Use this location first** — it's Ableton's officially documented path for third-party remote scripts, and works across Live 11/12 editions (Standard, Suite, and Lite included):
```
~/Music/Ableton/User Library/Remote Scripts/
```
**Quick way to find it:**
1. Open **Finder**
2. Press **Cmd + Shift + G**
3. Paste: `~/Music/Ableton/User Library/Remote Scripts/`
4. If `Remote Scripts` doesn't exist yet, create it

> ⚠️ Some older guides point to `~/Library/Preferences/Ableton/Live [Version]/User Remote Scripts/` — in testing on Live 12 (Lite), scripts placed there were **not** picked up. Use the User Library path above; only fall back to the Preferences path or `/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/` if AbletonMCP still doesn't appear after a full restart of Live.

### Install the Main Remote Script

1. **Create folder:** In your Remote Scripts directory, create a new folder called `AbletonMCP`
2. **Copy file:** Copy `AbletonMCP_Remote_Script/__init__.py` into the `AbletonMCP` folder

**Your folder structure should look like:**
```
Remote Scripts/
├── AbletonMCP/
│   └── __init__.py
└── (other scripts...)
```

Same would apply if you want to install the UDP version of Ableton MCP server. Create another folder (I called it "AbletonMCP_UDP") and place its corresponding '__init__.py' inside. Both servers can co-exist.

> 💡 **Tip:** Double-check this folder structure - it's the most common source of installation issues.

---

### Step 3: Configure Ableton Live

Enable the Remote Script:

1.  **Open or restart Ableton Live.**
2.  Navigate to **Preferences** (`Ctrl + ,` or `Cmd + ,`).
3.  Go to the **Link, Tempo & MIDI** tab.
4.  In an empty **Control Surface** slot, select **AbletonMCP** from the dropdown menu.
5.  Set the **Input** and **Output** for the `AbletonMCP` surface to **None**.
6.  Close the Preferences window.

When the script is loaded correctly, you will see a message in Ableton's status bar: **"AbletonMCP: Listening for commands on port 9877"**.

---

### Step 4: Connect Your AI Assistant

Choose your preferred AI assistant:

### 🔵 Claude Desktop

1. **Open Claude Desktop**
2. Go to **Claude** → **Settings** → **Developer**
3. Click **"Edit Config"**
4. **Replace the entire content** with the config for your OS:

**🍎 macOS:**
```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python3",
      "args": [
        "/path/to/studioworks-core/MCP_Server/server.py"
      ]
    }
  }
}
```
> If using a virtual environment, replace `python3` with the full venv path: `/path/to/studioworks-core/.venv/bin/python`

**🪟 Windows:**
```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": [
        "C:\\path\\to\\studioworks-core\\MCP_Server\\server.py"
      ]
    }
  }
}
```

5. **Update the path** to your actual installation path
6. **Save** and **restart Claude Desktop**

#### 🔍 Finding Your Installation Path
**Windows:**
```bash
# In your studioworks-core folder, run:
echo %CD%\MCP_Server\server.py
```

**macOS:**
```bash
# In your studioworks-core folder, run:
echo $PWD/MCP_Server/server.py
```

### 🟡 Cursor IDE

1. **Open Cursor**
2. Go to **Settings** → **MCP**
3. **Add new MCP server:**
   - **Paste this**:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "python",
      "args": [
        "C:/path/to/studioworks-core/MCP_Server/server.py"
      ]
    }
  }
}
```

4. **Save settings**

### Verify AI Connection

**For Claude Desktop:**
Look for a **🔨 hammer icon** in the chat interface - this indicates MCP tools are loaded.

**For Cursor:**
You'll see a green dot next to the MCP server icon, and a message saying "50+ tools enabled".

You might have to restart your AI assistant in order for changes to impact.

---

### Step 5: Test Your Installation

To confirm everything is working, try these commands in your AI assistant:

### Basic Tests
1. **"Get information about my current Ableton session"**
   - Should return details about your Ableton project

2. **"Create a new MIDI track"**
   - Should create a new track in Ableton

3. **"What tracks do I currently have?"**
   - Should list your tracks

If all three commands work correctly, congratulations! 🎉 Your installation is complete.

---

### Optional: Advanced Features

<details>
<summary><strong>⚡ High-Performance UDP Server (For Real-Time Control)</strong></summary>

For ultra-low latency parameter control:

1. **Install UDP Remote Script:**
   - Create folder: `Remote Scripts/AbletonMCP_UDP/`
   - Copy: `Ableton-MCP_hybrid-server/AbletonMCP_UDP/__init__.py`

2. **Configure in Ableton:**
   - Add another Control Surface: "AbletonMCP_UDP"
   - Input/Output: "None"

**Perfect for:** Live performance, real-time effects, expressive control.

Note: both remote scripts (TCP and UDP) can co-exist without issues.
</details>

---

## 🛠️ Troubleshooting

### ❌ Common Issues & Solutions

<details>
<summary><strong>🔴 "AbletonMCP not found in Control Surface list"</strong></summary>

**Possible causes:**
- Remote Script not in correct folder (macOS: use `~/Music/Ableton/User Library/Remote Scripts/`, **not** the `~/Library/Preferences/Ableton/...` path — the latter was not picked up in testing on Live 12)
- File permissions issue
- Incorrect folder name

**Solutions:**
1. Verify folder path: `Remote Scripts/AbletonMCP/__init__.py`
2. Check file permissions (should be readable)
3. Fully quit and reopen Ableton Live (Live only scans this folder at startup)
4. Check Ableton's log for error messages
</details>

<details>
<summary><strong>🟡 "No hammer icon in Claude Desktop"</strong></summary>

**Possible causes:**
- Incorrect path in config file
- Python not in system PATH
- MCP server file missing

**Solutions:**
1. Verify Python installation: `python --version`
2. Check absolute path to server.py file
3. Use double backslashes on Windows: `C:\\path\\to\\file`
4. Restart Claude Desktop after config changes
</details>

<details>
<summary><strong>🟠 "Connection refused" or "Socket error"</strong></summary>

**Possible causes:**
- Ableton not running
- Remote Script not loaded
- Firewall blocking connection

**Solutions:**
1. Make sure Ableton Live is running
2. Verify Remote Script is selected in Ableton preferences
3. Check Windows Firewall/macOS firewall settings
4. Try restarting both Ableton and your AI assistant
</details>

<details>
<summary><strong>🔵 "Python not found" error</strong></summary>

**Solutions:**
1. **Install Python:** Download from [python.org](https://python.org)
2. **Add to PATH:** During installation, check "Add Python to PATH"
3. **Verify installation:** Open terminal, type `python --version`
4. **Use full path:** If still issues, use full Python path in config
</details>

<details>
<summary><strong>🔴 "externally-managed-environment" error when running pip</strong></summary>

This error appears on macOS with Homebrew-managed Python or any system Python that prevents global package installation.

**Solution:** Use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then update your MCP config to use the venv Python:
```json
"command": "/path/to/studioworks-core/.venv/bin/python"
```
</details>

<details>
<summary><strong>🟡 MCP server doesn't start on Mac (existing installation)</strong></summary>

If you previously installed the server (as `ableton-mcp-extended` or `studioworks-core`) with `"command": "python"` in your MCP config, it may fail on macOS where the command is `python3`.

**Solution:** Update your Claude Desktop or Cursor MCP config:
```json
"command": "python3"
```

Or if using a virtual environment, use the full path:
```json
"command": "/path/to/studioworks-core/.venv/bin/python"
```

Then restart your AI assistant.
</details>

### 🔧 Advanced Troubleshooting

**Enable Debug Mode:**
1. Set environment variable: `ABLETON_MCP_DEBUG=1`
2. Restart your AI assistant
3. Check console output for detailed logs

**Test Components Individually:**
```bash
# Test Python installation
python --version

# Test MCP server directly
python MCP_Server/server.py

# Test Ableton connection (with Ableton running)
python -c "import socket; s = socket.socket(); s.connect(('localhost', 9877)); print('✅ Connected')"
```

---

## Capabilities Demonstration

📹 **See Studioworks Core in action:** [Link to your capabilities demonstration]

---

## Installation Complete!

**You're now ready to co-create with your AI assistant!**

### 🚀 Next Steps:
1. **[Watch the Demo Video](#-capabilities-demonstration)** - See the amazing possibilities
2. **[Join the Community](https://github.com/mumumedia/studioworks-core/discussions)** - Share your creations

---

## 💬 Need Help?

- **🐛 Found a bug?** [Open an issue](https://github.com/mumumedia/studioworks-core/issues)
- **❓ Have questions?** [Join discussions](https://github.com/mumumedia/studioworks-core/discussions)

---

<div align="center">

**Welcome to the future of music production!**

*Ready to make music through conversation? Let's create something amazing together.*

</div> 
