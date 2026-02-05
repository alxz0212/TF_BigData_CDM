# Trabajo Final: El "Gran Juego" Post-Soviético

**Alumno:** Daniel Alexis Mendoza Corne  
**Fecha:** 04/02/2026

---

## Orden de trabajo

Completa los archivos en este orden. Cada numero indica la secuencia:

| Orden | Archivo                    | Que haces                                   |
| ----- | -------------------------- | ------------------------------------------- |
| **1** | `README.md` (este archivo) | Defines tu pregunta, paises y variables     |
| **2** | `02_INFRAESTRUCTURA.md`    | Construyes y explicas tu docker-compose.yml |
| **3** | `src/pipeline.py`          | Escribes tu ETL + analisis con Spark        |
| **4** | `03_RESULTADOS.md`         | Presentas graficos e interpretas resultados |
| **5** | `04_REFLEXION_IA.md`       | Documentas tu proceso y pegas tus prompts   |
| **6** | `05_RESPUESTAS.md`         | Respondes 4 preguntas de comprension        |

Los archivos `docker-compose.yml`, `requirements.txt` y `.gitignore` los completas conforme avanzas.

---

## Pregunta de investigacion

"¿Son los factores de 'Poder Duro' (Gasto Militar) o de 'Poder Blando' (Democracia, Control de Corrupción) los que determinan el desarrollo económico en la periferia post-soviética?"

---

## Paises seleccionados (5)

| #   | Pais            | Codigo ISO | Por que lo elegiste                                                            |
| --- | --------------- | ---------- | ------------------------------------------------------------------------------ |
| 1   | **Afghanistan** | AFG        | Actor central histórico y geopolítico en la región ("Cementerio de Imperios"). |
| 2   | **Mongolia**    | MNG        | Estado tapón estratégico y neutral entre las potencias Rusia y China.          |
| 3   | **Azerbaijan**  | AZE        | Pieza clave en la conexión Caspio-Cáucaso y seguridad energética.              |
| 4   | **Georgia**     | GEO        | Referente de aspiraciones democráticas y occidentales en la región.            |
| 5   | **Armenia**     | ARM        | Aliado estratégico tradicional de Rusia en el Cáucaso Sur.                     |

**IMPORTANTE:** No puedes usar los paises del ejemplo del profesor (KAZ, UZB, TKM, KGZ, TJK).

---

## Variables seleccionadas (5 numericas)

| #   | Variable QoG | Que mide              | Por que la elegiste                                                            |
| --- | ------------ | --------------------- | ------------------------------------------------------------------------------ |
| 1   | `gle_cgdpc`  | PIB per cápita real   | **Variable Objetivo (Target):** Indicador estándar de desarrollo económico.    |
| 2   | `wdi_expmil` | Gasto militar (% PIB) | **Poder Duro:** Refleja la priorización de seguridad sobre bienestar.          |
| 3   | `p_polity2`  | Índice de Democracia  | **Poder Blando:** Mide la estabilidad y apertura del régimen político.         |
| 4   | `vdem_corr`  | Índice de Corrupción  | **Calidad Institucional:** Factor clave que afecta la inversión y crecimiento. |
| 5   | `wdi_lifexp` | Esperanza de vida     | **Variable de Control:** Indicador básico de bienestar social y salud.         |

**Tip:** Consulta el codebook de QoG para entender que mide cada variable:
https://www.gu.se/en/quality-government/qog-data

---

## Variable derivada

He creado la variable **`subregion`** para agrupar geográficamente a los países y capturar dinámicas regionales distintas más allá de las fronteras nacionales:

- **Caucasus:** Azerbaiyán, Georgia, Armenia.
- **Central/South:** Afganistán.
- **East:** Mongolia.

---

## Tipo de analisis elegido

- [ ] Clustering (K-Means)
- [ ] Serie temporal (evolucion por pais)
- [x] Comparacion (Regresión Random Forest - Importancia de Factores)

---

## Como ejecutar mi pipeline

```bash
# Paso 1: Levantar infraestructura
docker compose up -d

# Paso 2: Verificar que todo funciona
docker ps

# Paso 3: Ejecutar pipeline ETL (Procesamiento de Datos)
# Nota: Ejecutar desde dentro del contenedor o tener Spark local.
# Si usas Docker (recomendado):
docker exec jupyter_lab python /home/jovyan/work/src/pipeline.py

# Paso 4: Ejecutar Análisis y Generar Gráficos
docker exec jupyter_lab spark-submit /home/jovyan/work/src/analysis.py
```

El análisis generará los gráficos en la carpeta `notebooks/` y el reporte final está en `03_RESULTADOS.md`.
