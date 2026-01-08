#!/usr/bin/env python3
"""
Script para realizar análisis espacial (Moran's I y LISA).
Calcula la densidad de amenidades en una cuadrícula y analiza su autocorrelación.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import libpysal
from esda.moran import Moran, Moran_Local
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Configuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection():
    db_url = (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )
    return create_engine(db_url)

def run_spatial_analysis():
    engine = get_db_connection()
    output_dir = Path(__file__).parent.parent / 'data' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 1. Cargar datos
        logger.info("Cargando datos desde PostGIS...")
        boundary = gpd.read_postgis("SELECT geometry FROM raw_data.comuna_boundaries", engine, geom_col='geometry')
        amenities = gpd.read_postgis("SELECT geometry FROM raw_data.osm_amenities", engine, geom_col='geometry')

        if boundary.empty or amenities.empty:
            logger.error("No se encontraron datos suficientes para el análisis.")
            return

        # 2. Crear cuadrícula (Grid) sobre la comuna
        logger.info("Creando cuadrícula de análisis...")
        # Proyectar a UTM para cálculos métricos (UTM 19S para Chile Central)
        boundary_utm = boundary.to_crs(epsg=32719)
        amenities_utm = amenities.to_crs(epsg=32719)

        xmin, ymin, xmax, ymax = boundary_utm.total_bounds
        cell_size = 500  # 500 metros
        cols = int(np.ceil((xmax - xmin) / cell_size))
        rows = int(np.ceil((ymax - ymin) / cell_size))

        grid_cells = []
        for i in range(cols):
            for j in range(rows):
                x1 = xmin + i * cell_size
                x2 = x1 + cell_size
                y1 = ymin + j * cell_size
                y2 = y1 + cell_size
                from shapely.geometry import box
                grid_cells.append(box(x1, y1, x2, y2))

        grid = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs=boundary_utm.crs)
        
        # Filtrar celdas que intersectan con la comuna
        grid = grid[grid.intersects(boundary_utm.unary_union)].copy()
        grid = grid.reset_index(drop=True)

        # 3. Contar puntos por celda
        logger.info("Calculando densidad de amenidades...")
        joined = gpd.sjoin(amenities_utm, grid, how='inner', predicate='within')
        counts = joined.index_right.value_counts()
        grid['count'] = grid.index.map(counts).fillna(0)

        # 4. Análisis de Moran's I
        logger.info("Calculando autocorrelación espacial (Moran's I)...")
        w = libpysal.weights.Queen.from_dataframe(grid)
        w.transform = 'R'

        y = grid['count']
        mi = Moran(y, w)
        logger.info(f"Moran's I Global: {mi.I:.4f} (p-value: {mi.p_sim:.4f})")

        # 5. LISA (Local Indicators of Spatial Association)
        logger.info("Calculando clusters LISA...")
        lisa = Moran_Local(y, w)
        
        # Clasificación LISA
        # 0: no significativo, 1: HH, 2: LL, 3: HL, 4: LH
        grid['lisa_cluster'] = lisa.q
        grid['lisa_p_sim'] = lisa.p_sim
        grid.loc[grid['lisa_p_sim'] > 0.05, 'lisa_cluster'] = 0
        
        cluster_labels = {0: 'NS', 1: 'HH', 2: 'LL', 3: 'HL', 4: 'LH'}
        grid['cluster_type'] = grid['lisa_cluster'].map(cluster_labels)

        # 6. Guardar resultados
        # Volver a WGS84 para visualización web
        grid_wgs84 = grid.to_crs(epsg=4326)
        
        output_file = output_dir / 'spatial_analysis.geojson'
        grid_wgs84.to_file(output_file, driver='GeoJSON')
        logger.info(f"Resultados guardados en {output_file}")
        
        # También guardar en PostGIS
        grid_wgs84.to_postgis('amenity_clusters', engine, schema='raw_data', if_exists='replace')
        logger.info("Resultados guardados en tabla raw_data.amenity_clusters")

    except Exception as e:
        logger.error(f"Error en el análisis espacial: {e}")

if __name__ == '__main__':
    run_spatial_analysis()
