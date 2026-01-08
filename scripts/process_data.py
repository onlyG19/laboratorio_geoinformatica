#!/usr/bin/env python3
"""
Script para procesar y preparar datos para análisis.
Cargo los datos de data/raw a PostGIS.
"""

import geopandas as gpd
import pandas as pd
import osmnx as ox
from pathlib import Path
from sqlalchemy import create_engine, text
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Procesa y prepara datos para análisis."""

    def __init__(self):
        self.engine = self.create_db_connection()
        self.raw_data_path = Path(__file__).parent.parent / 'data' / 'raw'

    def create_db_connection(self):
        """Crea conexión a PostGIS."""
        db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:"
            f"{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
            f"{os.getenv('POSTGRES_PORT', '5432')}/"
            f"{os.getenv('POSTGRES_DB')}"
        )
        return create_engine(db_url)

    def create_schema(self, schema='raw_data'):
        """Crea el esquema si no existe."""
        with self.engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema};"))
            conn.commit()
            logger.info(f"Esquema '{schema}' verificado/creado.")

    def load_to_postgis(self, gdf, table_name, schema='raw_data'):
        """Carga GeoDataFrame a PostGIS."""
        try:
            # Asegurar que el CRS sea el correcto (WGS 84 o el que defina el proyecto)
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            
            gdf.to_postgis(
                table_name,
                self.engine,
                schema=schema,
                if_exists='replace',
                index=False
            )
            logger.info(f"Tabla {schema}.{table_name} creada exitosamente con {len(gdf)} registros.")
            return True
        except Exception as e:
            logger.error(f"Error cargando a PostGIS ({table_name}): {e}")
            return False

    def process_osm_network(self, input_file, schema='raw_data'):
        """Procesa red vial de OSM (GraphML) y carga a PostGIS."""
        try:
            logger.info(f"Procesando red vial desde {input_file}...")
            G = ox.load_graphml(input_file)
            
            # Convertir a GeoDataFrames
            nodes, edges = ox.graph_to_gdfs(G)
            
            # Limpiar columnas de tipo lista/objeto para PostgreSQL
            for df in [nodes, edges]:
                for col in df.columns:
                    if df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)

            self.load_to_postgis(nodes, 'osm_nodes', schema=schema)
            self.load_to_postgis(edges, 'osm_edges', schema=schema)
            return True
        except Exception as e:
            logger.error(f"Error procesando red vial: {e}")
            return False

    def create_spatial_indices(self, schema='raw_data'):
        """Crea índices espaciales en las tablas."""
        tables = ['osm_amenities', 'osm_buildings', 'osm_nodes', 'osm_edges', 'comuna_boundaries']
        try:
            with self.engine.connect() as conn:
                for table in tables:
                    # Verificar si la tabla existe antes de crear índice
                    check_table = conn.execute(text(
                        f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}');"
                    )).scalar()
                    
                    if check_table:
                        index_name = f"idx_{table}_geom"
                        conn.execute(text(f"DROP INDEX IF EXISTS {schema}.{index_name};"))
                        conn.execute(text(f"CREATE INDEX {index_name} ON {schema}.{table} USING GIST (geometry);"))
                        logger.info(f"Índice espacial creado en {schema}.{table}")
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creando índices espaciales: {e}")
            return False

    def run_pipeline(self):
        """Ejecuta todo el proceso de carga."""
        self.create_schema()
        
        # 1. Cargar GeoJSONs simples
        geojson_files = {
            'osm_amenities.geojson': 'osm_amenities',
            'osm_buildings.geojson': 'osm_buildings',
            'comuna_boundaries.geojson': 'comuna_boundaries'
        }
        
        for file_name, table_name in geojson_files.items():
            file_path = self.raw_data_path / file_name
            if file_path.exists():
                logger.info(f"Cargando {file_name}...")
                gdf = gpd.read_file(file_path)
                self.load_to_postgis(gdf, table_name)
            else:
                logger.warning(f"Archivo no encontrado: {file_name}")

        # 2. Cargar Red Vial (GraphML)
        network_file = self.raw_data_path / 'osm_network.graphml'
        if network_file.exists():
            self.process_osm_network(network_file)
        
        # 3. Crear índices
        self.create_spatial_indices()


def main():
    processor = DataProcessor()
    processor.run_pipeline()
    logger.info("¡Procesamiento y carga completados!")


if __name__ == '__main__':
    main()
