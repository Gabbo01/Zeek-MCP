import argparse  # Module for parsing command-line arguments
import logging   # Module for application logging
import subprocess  # Module for running external commands and subprocesses
import pandas as pd  # Library for tabular data manipulation and analysis
from mcp.server.fastmcp import FastMCP  # Import the FastMCP class from the MCP package
import os        # Module for interacting with the operating system (files, directories)
import glob      # Module for file pattern matching (glob)
import pandas as pd  # (Duplicate) Pandas for DataFrame operations

# Configure module-level logger
logger = logging.getLogger(__name__)
# Create the main FastMCP instance to expose tools as endpoints
mcp = FastMCP("Zeek-MCP")

def parse_zeek_log(path):
    """
    Parse a single Zeek .log file:
      1. Read header lines starting with '#'
      2. Extract fields defined by the '#fields' header line
      3. Build a pandas DataFrame from the tabular data

    Args:
        path (str): Path to the Zeek .log file
    Returns:
        pd.DataFrame: Table with columns corresponding to Zeek fields
    Raises:
        ValueError: If the '#fields' header line is missing
    """
    headers = []     # List to collect header lines
    data_lines = []  # List of lists to collect data row values

    # Open the log file for reading
    with open(path, "r") as f:
        for line in f:
            line = line.strip()  # Remove whitespace and newline
            if line.startswith("#"):  # Zeek header lines start with '#'
                headers.append(line)
            elif line:
                # Split data rows by tab and add to list
                data_lines.append(line.split('\t'))

    # Find the '#fields' header to determine column names
    field_line = next((h for h in headers if h.startswith("#fields")), None)
    if not field_line:
        # Raise an error if '#fields' is missing
        raise ValueError(f"Missing '#fields' header in {path}")

    # Build column list by removing the '#fields\t' prefix
    columns = field_line.replace("#fields\t", "").split('\t')
    # Create a pandas DataFrame with the parsed data
    df = pd.DataFrame(data_lines, columns=columns)
    return df


def parse_all_logs_as_str(directory="."):
    """
    Search for all .log files in the specified directory and return a single
    formatted string containing, for each file:
      - File name enclosed by '=== file_name ==='
      - Table of data (using DataFrame.to_string)
      - Error message if parsing fails

    Args:
        directory (str): Directory to search for .log files (default: current)
    Returns:
        str: Concatenated blocks separated by two blank lines
    """
    # Find and sort all .log files in the directory
    log_files = sorted(glob.glob(os.path.join(directory, "*.log")))
    parts = []  # List of text blocks for each log file

    for log_path in log_files:
        basename = os.path.basename(log_path)
        try:
            # Parse the log file and convert to a string table
            df = parse_zeek_log(log_path)
            table_str = df.to_string(index=False)
            part = f"=== {basename} ===\n\n{table_str}"
        except Exception as e:
            # Include error message if parsing fails
            part = f"[ERR] {basename}: {e}"
        parts.append(part)

    # Join all text blocks with two blank lines as separators
    return "\n\n".join(parts)


# Define an MCP tool using the @mcp.tool() decorator
@mcp.tool()
def execzeek(pcap_path: str) -> str:
    """
    Run Zeek on a specified PCAP file after cleaning existing .log files.

    Args:
        pcap_path (str): Path to the input PCAP file
    Returns:
        str: Comma-separated names of generated log files if successful,
             or "1" in case of an error
    """
    try:
        # Remove all existing .log files in the current directory
        for old in glob.glob("*.log"):
            try:
                os.remove(old)
                print(f"[INFO] Removed file: {old}")
            except Exception as e:
                print(f"[WARN] Could not remove {old}: {e}")

        # Execute the Zeek command on the PCAP file
        res = subprocess.run(["zeek", "-C", "-r", pcap_path], check=False)
        if res.returncode == 0:
            # On success, collect the new .log files
            new_logs = glob.glob("*.log")
            if new_logs:
                logs_str = ", ".join(new_logs)
                print(f"[INFO] Generated log files: {logs_str}")
                return f"Generated the following files:\n{logs_str}"
            else:
                print("[WARN] No .log files found after running Zeek.")
                return ""
        else:
            # If Zeek exits with an error code, return "1"
            print(f"[ERROR] Zeek returned exit code {res.returncode}")
            return "1"
    except Exception as e:
        # Handle unexpected exceptions during Zeek execution
        print(f"[ERROR] Error running Zeek: {e}")
        return "1"


@mcp.tool()
def parselogs(logfile: str):
    """
    MCP tool for parsing a single log file.

    Args:
        logfile (str): Path to the .log file to be parsed
    Returns:
        pd.DataFrame: DataFrame resulting from parse_zeek_log
    """
    return parse_zeek_log(logfile)


def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="MCP server for mcp")
    parser.add_argument("--mcp-host", type=str, default="127.0.0.1",
                        help="Host to run MCP server on (only used for sse), default: 127.0.0.1")
    parser.add_argument("--mcp-port", type=int,
                        help="Port to run MCP server on (only used for sse), default: 8081")
    parser.add_argument("--transport", type=str, default="sse", choices=["stdio", "sse"],
                        help="Transport protocol for MCP, default: sse")
    args = parser.parse_args()

    # Use Server-Sent Events (SSE) transport
    if args.transport == "sse":
        try:
            # Configure basic logging at INFO level
            log_level = logging.INFO
            logging.basicConfig(level=log_level)
            logging.getLogger().setLevel(log_level)

            # Apply FastMCP settings based on arguments
            mcp.settings.log_level = "INFO"
            mcp.settings.host = args.mcp_host or "127.0.0.1"
            mcp.settings.port = args.mcp_port or 8081

            logger.info(f"Starting MCP server on http://{mcp.settings.host}:{mcp.settings.port}/sse")
            logger.info(f"Using transport: {args.transport}")

            # Start the MCP server with SSE transport
            mcp.run(transport="sse")
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        # Run MCP in stdio transport mode
        mcp.run()

# Entry point of the script when executed directly
if __name__ == "__main__":
    main()
