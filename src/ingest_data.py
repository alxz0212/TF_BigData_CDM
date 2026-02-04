from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os
import sys

# Configuración
POSTGRES_URL = "jdbc:postgresql://postgres_db:5432/qog_data" # 'postgres_db' es el nombre del servicio/contenedor en Docker
POSTGRES_PROPERTIES = {
    "user": "user",
    "password": "password",
    "driver": "org.postgresql.Driver"
}
# Usar ruta relativa compatible con ambos entornos
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "qog_std_ts_jan26.csv")

def main():
    # Inicializar Sesión de Spark
    # Nota: El jar debe ser proporcionado en spark-submit o estar implícito en el entorno
    jar_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jars", "postgresql-42.7.3.jar")
    spark = SparkSession.builder \
        .appName("Ingesta de Datos QoG") \
        .config("spark.jars", jar_path) \
        .getOrCreate()

    print(">>> INICIO SCRIPT >>>", file=sys.stderr)
    print("Sesión de Spark creada.", file=sys.stderr)

    # Leer CSV
    print(f"Leyendo datos desde {DATA_PATH}...", file=sys.stderr)
    df = spark.read.csv(DATA_PATH, header=True, inferSchema=True)

    row_count = df.count()
    col_count = len(df.columns)
    print(f"Datos leídos. Filas: {row_count}, Columnas: {col_count}", file=sys.stderr)

    if row_count == 0:
        print("!!! ALERTA: Dataframe vacio", file=sys.stderr)

    # Limpiar/Renombrar columnas
    # Limpieza simple por si acaso, aunque seleccionaremos por nombre original si es posible
    # Map of original QoG names to our target names (or just keep originals)
    # Lista de variables de interés para Asia Central
    # Identificadores: cname, ccode, year
    # Economía: gle_cgdpc (GDP pc), wdi_gdp (GDP total)
    # Política: bmr_dem (Democracia), fh_ipolity2 (Freedom House)
    # Corrupción: ti_cpi (Transparency Int), wbgi_cce (Control Corruption)
    # Social: wdi_lifexp (Esperanza vida)
    
    target_columns = [
        "cname", "ccode", "year", "ccodecow", 
        "gle_cgdpc", "wdi_gdp", 
        "bmr_dem", "fh_ipolity2", "polity_iv",
        "ti_cpi", "wbgi_cce", "icrg_qog",
        "wdi_lifexp"
    ]
    
    print(f"Seleccionando {len(target_columns)} variables clave para el análisis...", file=sys.stderr)
    
    # Verificar qué columnas existen realmente en el DF
    existing_columns = [c for c in target_columns if c in df.columns]
    missing_columns = [c for c in target_columns if c not in df.columns]
    
    if missing_columns:
        print(f"!!! AVISO: Las siguientes columnas no se encontraron y serán ignoradas: {missing_columns}", file=sys.stderr)
        
    df = df.select(*existing_columns)
    print(f"Esquema final con {len(df.columns)} columnas.", file=sys.stderr)

    # Escribir a PostgreSQL
    print("Escribiendo a PostgreSQL...", file=sys.stderr)
    # Quitar try/except para ver el error real si falla
    df.write.jdbc(url=POSTGRES_URL, table="qog_standard_ts", mode="overwrite", properties=POSTGRES_PROPERTIES)
    print("Datos escritos exitosamente en PostgreSQL.", file=sys.stderr)
    print("<<< FIN SCRIPT <<<", file=sys.stderr)

    spark.stop()

if __name__ == "__main__":
    main()
