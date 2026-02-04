# TF Pipeline BigData con Infraestructura Docker

Este proyecto implementa un pipeline de datos completo (End-to-End) integrando tecnologías de Big Data y Machine Learning en un entorno contenerizado.

## Descripción

El objetivo es simular un flujo de trabajo real de ciencia de datos que incluye:

1.  **Infraestructura**: Despliegue de servicios (JupyterLab, Spark) usando Docker.
2.  **Ingesta**: Carga y procesamiento de datos masivos con Apache Spark.
3.  **Modelado**: Entrenamiento de redes neuronales con TensorFlow.

## Estructura del Proyecto

```
.
├── data/           # Almacenamiento de datasets (volumen Docker)
├── docker/         # Archivos Dockerfile y config
├── notebooks/      # Jupyter Notebooks para exploración
├── src/            # Código fuente Python
│   └── main.py     # Punto de entrada del pipeline
├── docker-compose.yml
└── README.md
```

## Requisitos

- Docker Desktop
- Git

## Ejecución

1.  Asegúrate de que Docker Desktop esté corriendo.
2.  Levanta los servicios:
    ```bash
    docker-compose up --build
    ```
3.  Accede a JupyterLab en `http://localhost:8888`.
