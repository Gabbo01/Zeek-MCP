import argparse
import logging
import subprocess
import pandas as pd
from mcp.server.fastmcp import FastMCP
import os
import glob
import pandas as pd

logger = logging.getLogger(__name__)
mcp = FastMCP("Zeek-MCP")


def parse_zeek_log(path):
    """
    Parsing di un singolo file Zeek .log, cattura gli header Zeek e restituisce un DataFrame.
    """
    headers = []
    data_lines = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                headers.append(line)
            elif line:
                data_lines.append(line.split('\t'))

    # Trova la riga #fields e costruisci le colonne
    field_line = next((h for h in headers if h.startswith("#fields")), None)
    if not field_line:
        raise ValueError(f"Header #fields mancante in {path}")

    columns = field_line.replace("#fields\t", "").split('\t')
    df = pd.DataFrame(data_lines, columns=columns)
    return df


def parse_all_logs_as_str(directory="."):
    """
    Cerca tutti i .log nella directory e restituisce un'unica stringa formattata con:
      - nome file
      - blank line
      - header + dati per ciascun log, uno sotto l'altro
    """
    log_files = sorted(glob.glob(os.path.join(directory, "*.log")))
    parts = []

    for log_path in log_files:
        basename = os.path.basename(log_path)
        try:
            df = parse_zeek_log(log_path)
            table_str = df.to_string(index=False)
            part = f"=== {basename} ===\n\n{table_str}"
        except Exception as e:
            part = f"[ERR] {basename}: {e}"
        parts.append(part)

    # Unisce tutti i blocchi con due linee vuote per separazione
    return "\n\n".join(parts)





@mcp.tool()
def execzeek(pcap_path: str) -> str:
    '''
    Funzione che esegue Zeek su un file PCAP specificato.
    Prima dell'esecuzione, elimina tutti i file .log presenti nella directory corrente.
    
    Ritorna:
        stringa con i nomi dei file di log prodotti separati da virgola, se l'esecuzione ha successo
        "1" in caso di errore
    '''
    try:
        # Pulisci la directory dai log esistenti
        for old in glob.glob("*.log"):
            try:
                os.remove(old)
                print(f"[INFO] Rimosso file: {old}")
            except Exception as e:
                print(f"[WARN] Impossibile rimuovere {old}: {e}")

        # Esegui Zeek
        res = subprocess.run(["zeek", "-C", "-r", pcap_path], check=False)
        if res.returncode == 0:
            # Raccogli i nuovi file .log generati
            new_logs = glob.glob("*.log")
            if new_logs:
                logs_str = ", ".join(new_logs)
                print(f"[INFO] File di log prodotti: {logs_str}")
                return f"Sono stati generati i seguenti file:\n{logs_str}"
            else:
                print("[WARN] Nessun file .log trovato dopo l'esecuzione di Zeek.")
                return ""
        else:
            print(f"[ERRORE] Zeek ha restituito il codice di uscita {res.returncode}")
            return "1"
    except Exception as e:
        print(f"[ERRORE] durante l'esecuzione di Zeek: {e}")
        return "1"


@mcp.tool()
def parselogs(logfile: str):
    '''Funzione che permette di eseguire il parsing del file di log indicato in input.
    l'output in caso di successo è il parsing del file di log indicato.'''
    return parse_zeek_log(logfile)



def main():
    parser = argparse.ArgumentParser(description="MCP server for mcp")
    parser.add_argument("--mcp-host", type=str, default="127.0.0.1",
                        help="Host to run MCP server on (only used for sse), default: 127.0.0.1")
    parser.add_argument("--mcp-port", type=int,
                        help="Port to run MCP server on (only used for sse), default: 8081")
    parser.add_argument("--transport", type=str, default="sse", choices=["stdio", "sse"],
                        help="Transport protocol for MCP, default: sse")
    args = parser.parse_args()
    

    
    if args.transport == "sse":
        try:
            # Set up logging
            log_level = logging.INFO
            logging.basicConfig(level=log_level)
            logging.getLogger().setLevel(log_level)

            # Configure MCP settings
            mcp.settings.log_level = "INFO"
            if args.mcp_host:
                mcp.settings.host = args.mcp_host
            else:
                mcp.settings.host = "127.0.0.1"

            if args.mcp_port:
                mcp.settings.port = args.mcp_port
            else:
                mcp.settings.port = 8081

            logger.info(f"Starting MCP server on http://{mcp.settings.host}:{mcp.settings.port}/sse")
            logger.info(f"Using transport: {args.transport}")

            mcp.run(transport="sse")
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        mcp.run()
        
if __name__ == "__main__":
    main()

