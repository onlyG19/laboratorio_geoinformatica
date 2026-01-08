# 🗺️ Laboratorio Integrador - Análisis Geoespacial de San Bernardo

[![GitHub](https://img.shields.io/badge/GitHub-byron_gracia-blue?style=flat&logo=github)](https://github.com/onlyg19)
[![Course](https://img.shields.io/badge/Curso-Geoinformática_2025-green)](https://github.com/franciscoparrao/geoinformatica)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📋 Descripción

Este proyecto constituye la entrega final del curso de **Geoinformática (USACH 2025)**. Consiste en un sistema de análisis territorial integral aplicado a la comuna de **San Bernardo**, Chile. El sistema integra la adquisición automatizada de datos desde OpenStreetMap, almacenamiento en bases de datos espaciales (PostGIS), análisis geoestadístico de patrones de distribución (LISA) y modelación predictiva mediante Machine Learning para entender la oferta de servicios urbanos.

## 👥 Información del Proyecto

| Categoría | Detalle |
|-----------|---------|
| **Autor** | Byron Gracia |
| **Comuna** | San Bernardo, RM, Chile |
| **Institución** | Universidad de Santiago de Chile (USACH) |
| **Stack Principal** | Python, PostGIS, Docker, Streamlit, Scikit-Learn |

---

## 🚀 Instalación y Uso

### 1. Prerrequisitos
- Docker y Docker Compose
- Git LFS (para archivos de datos grandes)

### 2. Despliegue con Docker
El proyecto está completamente contenedorizado para asegurar la reproducibilidad:

```bash
# Iniciar servicios (PostGIS, Jupyter, Streamlit)
docker-compose up -d

# Visualizar la aplicación web
# URL: http://localhost:8501
```

### 3. Ejecución del Pipeline
El flujo de trabajo se divide en los notebooks numerados en la carpeta `notebooks/`. Se deben ejecutar secuencialmente.

---

## � Guía Detallada de Notebooks

El núcleo del análisis se encuentra en cinco etapas fundamentales:

### 1. `01_Data_Acquisition.ipynb`
**Objetivo:** Obtención y estructuración de la infraestructura de datos básica.
- Utiliza **OSMnx** para descargar la red vial, límites administrativos, edificios y equipamiento urbano (amenities) de San Bernardo.
- Realiza la limpieza inicial de geometrías y filtrado de tags irrelevantes.
- Establece la conexión con la base de datos y carga los GeoDataFrames en el esquema `raw_data` de **PostGIS**.

### 2. `02_Exploratory_Analysis.ipynb`
**Objetivo:** Caracterización estadística y visual del territorio.
- Cálculos de superficie, densidad habitacional por cuadrante y diversidad de servicios.
- Identificación de las categorías de servicios más frecuentes (educación, salud, comercio).
- Creación de mapas base de distribución de equipamiento y conectividad vial inicial.

### 3. `03_Geostatistics.ipynb`
**Objetivo:** Análisis de autocorrelación espacial y detección de brechas.
- Implementación de **Indicadores Locales de Asociación Espacial (LISA)** mediante la librería `PySAL`.
- Generación de un mapa de clusters para identificar **Hot Spots** (zonas de alta concentración de servicios) y **Cold Spots** (desiertos de servicios).
- Almacenamiento de los resultados de clustering en la base de datos para consumo de la App.

### 4. `04_Machine_Learning.ipynb`
**Objetivo:** Modelado predictivo de la oferta urbana.
- **Feature Engineering:** Creación de variables espaciales (distancia al centro, densidad de edificios circundante, conectividad vial).
- **Entrenamiento:** Implementación de un modelo **Random Forest Regressor** para predecir la densidad de servicios esperada en función del entorno construido.
- **Evaluación:** Análisis de importancia de variables y cálculo de errores espaciales (RMSE, R²).

### 5. `05_Results_Synthesis.ipynb`
**Objetivo:** Consolidación de hallazgos y cierre.
- Comparación entre la oferta real de servicios y la predicción del modelo para detectar áreas de oportunidad.
- Exportación de los datos finales en formatos interoperables (GeoJSON, CSV) para software SIG externo como QGIS.

---

## 🌐 Aplicación Web (Dashboard)

El sistema incluye un dashboard interactivo desarrollado en **Streamlit** que permite:
- **Visualización Multimodal**: Alternar entre mapas base vectoriales y vistas satelitales de alta resolución.
- **Exploración de Capas**: Visualizar dinámicamente clusters LISA, edificios y equipamiento.
- **Dashboard ML**: Examinar predicciones del modelo en tiempo real con leyendas interpretables para tomadores de decisiones.
- **Métricas Clave**: Resumen automático de indicadores territoriales de la comuna.

---

## �️ Arquitectura Técnica

- **Base de Datos**: PostgreSQL 15 + PostGIS 3.3 para procesamiento topológico.
- **Procesamiento**: Python 3.10 con GeoPandas, PySAL (Libpysal/Esda) y Scikit-Learn.
- **Visualización**: Folium para cartografía dinámica y Plotly para analítica de datos.
- **Infraestructura**: Docker para aislamiento de dependencias y despliegue rápido.

---

## 📄 Screenshots
- **Capturas de la app funcionando desde local**: 

<img width="1845" height="920" alt="imagen" src="https://github.com/user-attachments/assets/08cc5ea6-1bcf-436b-a9d9-add06cf83e43" />

<img width="1845" height="920" alt="imagen" src="https://github.com/user-attachments/assets/9375ddf6-d170-4437-859f-7374ec9f52b5" />

<img width="1845" height="920" alt="imagen" src="https://github.com/user-attachments/assets/06bd5715-c508-4da5-adbe-bcbe6ecc34c1" />

<img width="1845" height="920" alt="imagen" src="https://github.com/user-attachments/assets/f931663f-9962-40ce-9cac-e8034d29e8ee" />

<img width="1845" height="920" alt="imagen" src="https://github.com/user-attachments/assets/dd3b3aa3-6d68-474e-b514-dae88a210e14" />

---

## 📄 Licencia y Contacto

Este repositorio se distribuye bajo la licencia MIT. Para consultas académicas o técnicas, contactar a `byron.gracia@usach.cl`.

---
**Actualizado a:** Enero 2026 | **Curso:** Geoinformática - Facultad de Ingeniería USACH.
