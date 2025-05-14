# Zeek-MCP

This repository provides a set of Python utilities and MCP (Model Context Protocol) tools to:

* **Parse Zeek log files** (`.log`) into pandas DataFrames.
* **Aggregate multiple logs** into a single formatted string.
* **Execute Zeek** on a PCAP file, generate `.log` outputs, and return their names.
* **Expose** these functions as MCP endpoints via FastMCP.

---

## Table of Contents

* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)

  * [1. Clone the repository](#1-clone-the-repository)
  * [2. Install dependencies](#2-install-dependencies)
  * [3. Run the MCP server](#3-run-the-mcp-server)
  * [4. Use the MCP tools](#4-use-the-mcp-tools)
* [Code Overview](#code-overview)
* [Examples](#examples)
* [License](#license)

---

## Prerequisites

* **Python 3.7+**
* **Zeek** installed and available in your `PATH` (for the `execzeek` tool)
* **pip** (for installing Python dependencies)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo.git](https://github.com/Gabbo01/Zeek-MCP
cd Zeek-MCP
```

### 2. Install dependencies

It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

> **Note:** If you don’t have a `requirements.txt`, install directly:
>
> ```bash
> pip install pandas mcp-server
> ```

---

## Usage

The repository exposes three main MCP tools and a command-line entry point:

### 3. Run the MCP server

```bash
python main.py --mcp-host 127.0.0.1 --mcp-port 8081 --transport sse
```

* `--mcp-host`: Host for the MCP server (default: `127.0.0.1`).
* `--mcp-port`: Port for the MCP server (default: `8081`).
* `--transport`: Transport protocol, either `sse` (Server-Sent Events) or `stdio`.

Once running, the server exposes two endpoints:

### 4. Use the MCP tools

1. **`execzeek(pcap_path: str) -> str`**

   * **Description:** Runs Zeek on the given PCAP file after deleting existing `.log` files in the working directory.
   * **Returns:** A string listing generated `.log` filenames or `"1"` on error.

2. **`parselogs(logfile: str) -> DataFrame`**

   * **Description:** Parses a single Zeek `.log` file and returns a pandas DataFrame.

3. **`parse_all_logs_as_str(directory: str = '.') -> str`**

   * **Description:** Searches for all `.log` files under `directory`, parses each, and returns a formatted concatenated string.

You can interact with these endpoints via HTTP (if using SSE transport) or by embedding in your Python code:

```python
from mcp.client import MCPClient

client = MCPClient(transport='sse', host='127.0.0.1', port=8081)

# Execute Zeek
result = client.call('execzeek', pcap_path='capture.pcap')
print(result)

# Parse a log
df = client.call('parselogs', logfile='conn.log')
print(df.head())
```

---

## Code Overview

The main script (`main.py`) implements:

* **`parse_zeek_log(path)`**: Reads Zeek `.log`, extracts headers (`#fields`), constructs a DataFrame.
* **`parse_all_logs_as_str(directory)`**: Aggregates multiple logs into a single string for display.
* **`execzeek(pcap_path)`**: MCP tool to run Zeek on PCAP and report generated files.
* **`parselogs(logfile)`**: MCP tool to parse a single log file.
* **`main()`**: Argument parser and MCP server launcher.

---

## Examples

1. **Run Zeek and parse logs manually**

   ```bash
   # Run Zeek on sample.pcap
   python main.py --transport stdio execzeek sample.pcap

   # Parse the resulting conn.log
   python main.py --transport stdio parselogs conn.log
   ```

2. **Aggregate all logs into a string**

   ```python
   from your_module import parse_all_logs_as_str

   combined = parse_all_logs_as_str('logs/')
   print(combined)
   ```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
