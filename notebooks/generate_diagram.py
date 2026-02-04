
import base64
import requests
import os

mermaid_code = """
graph TD
    subgraph "Tu Ordenador (Host)"
        DE[Docker Engine]:::engine
        
        subgraph "Imágenes (Recetas - Read Only)"
            I1[Postgres Image]:::image
            I2[Spark Image]:::image
        end
        
        subgraph "Contenedores (Instancias - Running)"
            C1[Contenedor: postgres_db]:::container
            C2[Contenedor: spark_master]:::container
            C3[Contenedor: spark_worker]:::container
        end
    end

    DE -- "Construye & Ejecuta" --> C1
    DE -- "Gestiona" --> C2
    I1 -.->|"Se convierte en"| C1
    I2 -.->|"Se convierte en"| C2
    I2 -.->|"Se convierte en"| C3

    classDef engine fill:#2496ed,stroke:#333,stroke-width:2px,color:white;
    classDef image fill:#e1e4e8,stroke:#333,stroke-width:1px;
    classDef container fill:#28a745,stroke:#333,stroke-width:2px,color:white;
"""

graphbytes = mermaid_code.encode("utf8")
base64_bytes = base64.b64encode(graphbytes)
base64_string = base64_bytes.decode("ascii")

url = "https://mermaid.ink/img/" + base64_string

print(f"Downloading from: {url}")

response = requests.get(url)
if response.status_code == 200:
    output_path = "/home/jovyan/work/notebooks/docker_concept.png"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"Image saved to {output_path}")
else:
    print(f"Error downloading image: {response.status_code}")
