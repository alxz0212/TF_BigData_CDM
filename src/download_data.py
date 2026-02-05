import os
import urllib.request
import sys

# Configuración
DATA_URL = "https://www.qogdata.pol.gu.se/data/qog_std_ts_jan26.csv"
OUTPUT_DIR = "/home/jovyan/work/data/raw"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "qog_std_ts_jan26.csv")

def download_file():
    # Crear directorio si no existe
    if not os.path.exists(OUTPUT_DIR):
        print(f"Creating directory: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Starting download from: {DATA_URL}")
    print(f"Target: {OUTPUT_FILE}")
    
    try:
        # Descargar archivo
        urllib.request.urlretrieve(DATA_URL, OUTPUT_FILE)
        print("Dataset downloaded successfully!")
        
        # Verificar tamaño
        file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"File size: {file_size:.2f} MB")
        
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_file()
