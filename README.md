# Zeek-MCP

This repository provides a set of utilities to build an MCP server (Model Context Protocol) that you can use with your chatbot client.

---

## Table of Contents

* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)

  * [1. Clone the repository](#1-clone-the-repository)
  * [2. Install dependencies](#2-install-dependencies)
  * [3. Run the MCP server](#3-run-the-mcp-server)
  * [4. Use the MCP tools](#4-use-the-mcp-tools)
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
> pip install pandas mcp
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


### 4. Use the MCP tools

1. **`execzeek(pcap_path: str) -> str`**

   * **Description:** Runs Zeek on the given PCAP file after deleting existing `.log` files in the working directory.
   * **Returns:** A string listing generated `.log` filenames or `"1"` on error.

2. **`parselogs(logfile: str) -> DataFrame`**

   * **Description:** Parses a single Zeek `.log` file and returns a pandas DataFrame.

3. **`parse_all_logs_as_str(directory: str = '.') -> str`**

   * **Description:** Searches for all `.log` files under `directory`, parses each, and returns a formatted concatenated string.

You can interact with these endpoints via HTTP (if using SSE transport) or by embedding in LLM client (eg: Claude Desktop):

---

## Examples


---

## License

Distributed under the MIT License. See `LICENSE` for more information.
