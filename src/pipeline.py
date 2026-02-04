from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

def main():
    # Inicializar SparkSession
    print("Inicializando SparkSession...")
    spark = SparkSession.builder \
        .appName("GreatGame_ETL") \
        .getOrCreate()

    # Rutas (Absolute paths for Docker)
    input_path = "/home/jovyan/work/data/raw/qog_std_ts_jan26.csv"
    output_path = "/home/jovyan/work/data/processed/qog_great_game.parquet"

    # Leer CSV
    print(f"Leyendo datos desde: {input_path}")
    try:
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        spark.stop()
        return

    # Lista de países de interés (Gran Juego / Periferia Asia Central)
    target_countries = ["Afghanistan", "Mongolia", "Azerbaijan", "Georgia", "Armenia"]

    # Variables de interés
    # gle_cgdpc: GDP per Capita
    # wdi_lifexp: Life Expectancy
    # p_polity2: Polity IV Democracy Index
    # vdem_corr: V-Dem Corruption Index
    # wdi_expmil: Military Expenditure (% GDP)
    # wdi_pop: Population (Control variable)
    
    cols_to_select = [
        "cname", 
        "year", 
        "gle_cgdpc",    
        "wdi_lifexp",   
        "p_polity2",    
        "vdem_corr",    
        "wdi_expmil",
        "wdi_pop"       
    ]

    # Filtrar por países y año (Post-URSS >= 1991)
    print("Filtrando datos por países y año (>= 1991)...")
    df_filtered = df.filter(
        (col("cname").isin(target_countries)) & 
        (col("year") >= 1991)
    )

    # Selección de columnas
    try:
        df_selected = df_filtered.select(*[col(c) for c in cols_to_select])
    except Exception as e:
        print(f"Error al seleccionar columnas. Verifique que existan en el dataset. Detalles: {e}")
        spark.stop()
        return

    # Transformaciones
    print("Aplicando transformaciones...")
    
    # 1. Crear región/subregión
    df_transformed = df_selected.withColumn("subregion", 
        when(col("cname").isin("Azerbaijan", "Georgia", "Armenia"), "Caucasus")
        .when(col("cname") == "Afghanistan", "Central/South")
        .when(col("cname") == "Mongolia", "East")
        .otherwise("Other")
    )

    # 2. Casteo explícito a Double para métricas numéricas
    metric_cols = ["gle_cgdpc", "wdi_lifexp", "p_polity2", "vdem_corr", "wdi_expmil", "wdi_pop"]
    for c in metric_cols:
        df_transformed = df_transformed.withColumn(c, col(c).cast("double"))

    # Mostrar esquema y muestra
    print("\nEsquema de datos transformados:")
    df_transformed.printSchema()
    
    print("\nMuestra de los primeros 20 registros:")
    df_transformed.show(20, truncate=False)

    # Guardar en Parquet
    print(f"\nGuardando datos procesados en: {output_path}")
    try:
        df_transformed.write.mode("overwrite").parquet(output_path)
        print("¡Proceso ETL completado con éxito!")
    except Exception as e:
        print(f"Error al guardar el archivo Parquet: {e}")

    spark.stop()

if __name__ == "__main__":
    main()
