
"""
Pass'Tranquille - Backend Python
Dakar JOJ 2026 - Systeme d'itineraire multimodal
"""

import os
import math
import random
import numpy as np
import pandas as pd
from datetime import datetime, time, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import heapq
import json

# Database
import psycopg2
from psycopg2.extras import RealDictCursor

# ML
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib

# ============================================================
# CONFIGURATION
# ============================================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'pass_tranquille'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Vitesses en m/s
SPEED_TER = 27.78
SPEED_BRT = 13.89
SPEED_BUS = 5.56
SPEED_WALK = 1.1

MODE_COLORS = {
    'TER': '#e74c3c',
    'BRT': '#3498db',
    'BUS': '#2ecc71',
    'WALK': '#95a5a6'
}

MODE_NAMES = {
    'TER': 'Train Express Regional',
    'BRT': 'Bus Rapide Transit',
    'BUS': 'Bus DDD',
    'WALK': 'A pied'
}

MODE_ICONS = {
    'TER': 'train',
    'BRT': 'bus',
    'BUS': 'bus',
    'WALK': 'male'
}

# ============================================================
# POINTS D'INTERET (JOJ 2026)
# ============================================================

POI_DATA = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"Nom": "Plage Ouakam", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.4921322, 14.7158332]}},
        {"type": "Feature", "properties": {"Nom": "Iba Mar Diop", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.4467278, 14.6794137]}},
        {"type": "Feature", "properties": {"Nom": "Piscine Olympique", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.4618338, 14.6972146]}},
        {"type": "Feature", "properties": {"Nom": "Universite Amadou Makhtar Mbow", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.1971829, 14.733723]}},
        {"type": "Feature", "properties": {"Nom": "Stade Abdoulaye Wade", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.201264, 14.7321326]}},
        {"type": "Feature", "properties": {"Nom": "Dakar Arena", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.2126175, 14.7334502]}},
        {"type": "Feature", "properties": {"Nom": "Dakar Expo Centre", "category": "site_jo"},
         "geometry": {"type": "Point", "coordinates": [-17.2189251, 14.7299676]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Courtyard", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.2064857, 14.7294977]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Radisson Diamniadio", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.1963779, 14.740667]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Noom", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.4719967, 14.6965449]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Terrou Bi", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.467303, 14.6771929]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Azalai", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.4695341, 14.6757039]}},
        {"type": "Feature", "properties": {"Nom": "Place de l'Independance", "category": "monument"},
         "geometry": {"type": "Point", "coordinates": [-17.4321621, 14.6695052]}},
        {"type": "Feature", "properties": {"Nom": "Hotel Pullman", "category": "hotel"},
         "geometry": {"type": "Point", "coordinates": [-17.4311094, 14.6674822]}},
        {"type": "Feature", "properties": {"Nom": "Musee des Civilisations Noires", "category": "musee"},
         "geometry": {"type": "Point", "coordinates": [-17.4353004, 14.6772786]}},
        {"type": "Feature", "properties": {"Nom": "Grand Theatre National", "category": "monument"},
         "geometry": {"type": "Point", "coordinates": [-17.4368194, 14.6793591]}},
        {"type": "Feature", "properties": {"Nom": "Embarcadere Port", "category": "transport"},
         "geometry": {"type": "Point", "coordinates": [-17.4285862, 14.6732412]}},
        {"type": "Feature", "properties": {"Nom": "Goree", "category": "monument"},
         "geometry": {"type": "Point", "coordinates": [-17.3984124, 14.6659085]}},
        {"type": "Feature", "properties": {"Nom": "Musee Theodore Monod", "category": "musee"},
         "geometry": {"type": "Point", "coordinates": [-17.4381979, 14.6634511]}},
    ]
}

POI_CATEGORIES = {
    'site_jo': {'label': 'Sites JOJ', 'color': '#e74c3c', 'icon': 'star', 'marker_color': 'red'},
    'hotel': {'label': 'Hotels', 'color': '#f39c12', 'icon': 'bed', 'marker_color': 'orange'},
    'musee': {'label': 'Musees', 'color': '#9b59b6', 'icon': 'university', 'marker_color': 'purple'},
    'monument': {'label': 'Monuments', 'color': '#1abc9c', 'icon': 'landmark', 'marker_color': 'green'},
    'transport': {'label': 'Transport', 'color': '#34495e', 'icon': 'ship', 'marker_color': 'darkblue'},
}

# ============================================================
# CLASSES DE DONNEES
# ============================================================

@dataclass
class Stop:
    id: int
    name: str
    longitude: float
    latitude: float
    transport_type: str
    zone: str

@dataclass
class RouteStep:
    from_stop: Stop
    to_stop: Stop
    mode: str
    distance_meters: float
    duration_seconds: float
    route_name: Optional[str] = None
    wait_time_seconds: float = 0.0

    @property
    def duration_formatted(self) -> str:
        total = int(self.duration_seconds + self.wait_time_seconds)
        if total < 60:
            return f"{total}s"
        elif total < 3600:
            return f"{total // 60}min {total % 60}s"
        else:
            h = total // 3600
            m = (total % 3600) // 60
            return f"{h}h {m:02d}min"

    @property
    def distance_formatted(self) -> str:
        if self.distance_meters >= 1000:
            return f"{self.distance_meters/1000:.1f} km"
        return f"{self.distance_meters:.0f} m"

@dataclass
class Journey:
    steps: List[RouteStep]
    total_duration: float = 0.0
    total_distance: float = 0.0
    total_transfers: int = 0
    score: float = 0.0

    def __post_init__(self):
        self.total_duration = sum(s.duration_seconds + s.wait_time_seconds for s in self.steps)
        self.total_distance = sum(s.distance_meters for s in self.steps)
        modes = [s.mode for s in self.steps if s.mode != 'WALK']
        self.total_transfers = len(set(modes)) - 1 if modes else 0

# ============================================================
# CONNEXION BASE DE DONNEES
# ============================================================

class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()

    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()

# ============================================================
# GRAPHE ET DIJKSTRA
# ============================================================

class TransportGraph:
    def __init__(self, db: Database):
        self.db = db
        self.nodes = {}
        self.edges = defaultdict(list)
        self._load_graph()

    def _load_graph(self):
        stops_data = self.db.execute("SELECT * FROM stops")
        for row in stops_data:
            self.nodes[row['id']] = Stop(
                id=row['id'],
                name=row['name'],
                longitude=float(row['longitude']),
                latitude=float(row['latitude']),
                transport_type=row['transport_type'],
                zone=row['zone']
            )

        edges_data = self.db.execute("SELECT * FROM edges")
        for row in edges_data:
            self.edges[row['from_stop_id']].append((
                row['to_stop_id'],
                float(row['travel_time']),
                {
                    'distance': float(row['distance']),
                    'mode': row['transport_type'],
                    'route_id': row.get('route_id')
                }
            ))

    def dijkstra(self, start_id: int, end_id: int,
                 departure_time: Optional[datetime] = None) -> List[Tuple[int, float, Dict]]:
        dist = {node: float('inf') for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start_id] = 0

        pq = [(0, start_id)]
        visited = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if u == end_id:
                break

            for v, weight, edge_data in self.edges.get(u, []):
                if v in visited:
                    continue

                wait = 0
                if departure_time and prev[u]:
                    wait = self._calculate_wait_time(
                        u, v, edge_data['mode'],
                        departure_time + timedelta(seconds=dist[u])
                    )

                alt = dist[u] + weight + wait
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = (u, edge_data)
                    heapq.heappush(pq, (alt, v))

        path = []
        curr = end_id
        while curr is not None and prev[curr] is not None:
            prev_node, edge_data = prev[curr]
            path.append((curr, dist[curr], edge_da))
            curr = prev_node

        if curr == start_id:
            path.append((start_id, 0, {}))
            path.reverse()
            return path
        return []

    def _calculate_wait_time(self, from_id: int, to_id: int,
                             mode: str, current_time: datetime) -> float:
        if mode == 'WALK':
            return 0

        query = """
            SELECT t.frequency_minutes, st.departure_time
            FROM stop_times st
            JOIN trips t ON st.trip_id = t.id
            JOIN routes r ON t.route_id = r.id
            WHERE st.stop_id = %s
              AND r.transport_type = %s
              AND st.departure_time >= %s::time
            ORDER BY st.departure_time
            LIMIT 1
        """
        result = self.db.execute_one(query, (from_id, mode, current_time.time()))

        if result:
            next_departure = datetime.combine(current_time.date(), result['departure_time'])
            if next_departure < current_time:
                next_departure += timedelta(days=1)
            wait = (next_departure - current_time).total_seconds()
            return max(0, wait)

        default_freq = {'TER': 1200, 'BRT': 600, 'BUS': 900}
        return default_freq.get(mode, 600)

    def yen_k_shortest_paths(self, start_id: int, end_id: int,
                             k: int = 2,
                             departure_time: Optional[datetime] = None) -> List[List[Tuple[int, float, Dict]]]:
        first_path = self.dijkstra(start_id, end_id, departure_time)
        if not first_path:
            return []

        paths = [first_path]
        candidates = []

        for i in range(k - 1):
            if i >= len(paths):
                break

            current_path = paths[i]

            for spur_node_idx in range(len(current_path) - 1):
                spur_node = current_path[spur_node_idx][0]
                root_path = current_path[:spur_node_idx + 1]

                removed_edges = []

                for p in paths:
                    if len(p) > spur_node_idx and p[:spur_node_idx + 1] == root_path:
                        if spur_node_idx + 1 < len(p):
                            next_node = p[spur_node_idx + 1][0]
                            original_edges = self.edges.get(spur_node, [])
                            self.edges[spur_node] = [
                                e for e in original_edges if e[0] != next_node
                            ]
                            removed_edges.append((spur_node, original_edges))

                spur_path = self.dijkstra(spur_node, end_id, departure_time)

                for node, original in removed_edges:
                    self.edges[node] = original

                if spur_path:
                    total_path = root_path[:-1] + spur_path
                    path_ids = tuple(n[0] for n in total_path)
                    existing = [tuple(n[0] for n in p) for p in paths + candidates]
                    if path_ids not in existing:
                        candidates.append(total_path)

            candidates.sort(key=lambda p: p[-1][1] if p else float('inf'))

            if candidates:
                paths.append(candidates.pop(0))

        return paths[:k]

    def find_nearest_stop(self, lon: float, lat: float,
                          max_distance: float = 2000) -> Optional[Stop]:
        query = """
            SELECT id, name, longitude, latitude, transport_type, zone,
                   ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography) as dist
            FROM stops
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)
            ORDER BY dist
            LIMIT 1
        """
        result = self.db.execute_one(query, (lon, lat, lon, lat, max_distance))
        if result:
            return Stop(
                id=result['id'],
                name=result['name'],
                longitude=float(result['longitude']),
                latitude=float(result['latitude']),
                transport_type=result['transport_type'],
                zone=result['zone']
            )
        return None

    def path_to_journey(self, path: List[Tuple[int, float, Dict]]) -> Journey:
        steps = []
        for i in range(len(path) - 1):
            from_id = path[i][0]
            to_id = path[i + 1][0]
            edge_data = path[i + 1][2]

            from_stop = self.nodes[from_id]
            to_stop = self.nodes[to_id]

            step = RouteStep(
                from_stop=from_stop,
                to_stop=to_stop,
                mode=edge_data.get('mode', 'WALK'),
                distance_meters=edge_data.get('distance', 0),
                duration_seconds=path[i + 1][1] - path[i][1],
                route_name=None,
                wait_time_seconds=0
            )
            steps.append(step)
        return Journey(steps=steps)

    def journey_with_walk(self, from_lon: float, from_lat: float,
                          to_lon: float, to_lat: float,
                          departure_time: Optional[datetime] = None) -> List[Journey]:
        start_stop = self.find_nearest_stop(from_lon, from_lat)
        end_stop = self.find_nearest_stop(to_lon, to_lat)

        if not start_stop or not end_stop:
            return []

        walk_to_start = self._haversine(from_lat, from_lon,
                                         start_stop.latitude, start_stop.longitude)
        walk_from_end = self._haversine(end_stop.latitude, end_stop.longitude,
                                         to_lat, to_lon)

        paths = self.yen_k_shortest_paths(
            start_stop.id, end_stop.id, k=2, departure_time=departure_time
        )

        journeys = []
        for path in paths:
            journey = self.path_to_journey(path)

            if walk_to_start > 50:
                walk_step = RouteStep(
                    from_stop=Stop(0, "Position actuelle", from_lon, from_lat, 'WALK', ''),
                    to_stop=start_stop,
                    mode='WALK',
                    distance_meters=walk_to_start,
                    duration_seconds=walk_to_start / SPEED_WALK
                )
                journey.steps.insert(0, walk_step)

            if walk_from_end > 50:
                walk_step = RouteStep(
                    from_stop=end_stop,
                    to_stop=Stop(0, "Destination", to_lon, to_lat, 'WALK', ''),
                    mode='WALK',
                    distance_meters=walk_from_end,
                    duration_seconds=walk_from_end / SPEED_WALK
                )
                journey.steps.append(walk_step)

            journey.__post_init__()
            journeys.append(journey)

        return journeys

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c


# ============================================================
# MACHINE LEARNING
# ============================================================

class TrafficPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False

    def _extract_features(self, hour: int, day_of_week: int,
                         mode: str, distance: float,
                         is_joj_event: bool = False,
                         weather_condition: str = 'normal') -> np.ndarray:
        is_morning_rush = 1 if 7 <= hour <= 9 else 0
        is_evening_rush = 1 if 17 <= hour <= 20 else 0
        is_night = 1 if 22 <= hour or hour <= 5 else 0
        is_weekend = 1 if day_of_week >= 5 else 0
        joj_multiplier = 1.5 if is_joj_event else 1.0
        weather_map = {'normal': 1.0, 'rain': 1.3, 'heavy_rain': 1.6, 'heat': 1.2}
        weather_factor = weather_map.get(weather_condition, 1.0)

        features = [
            hour, day_of_week, is_morning_rush, is_evening_rush,
            is_night, is_weekend, distance, joj_multiplier, weather_factor,
            1 if mode == 'TER' else 0,
            1 if mode == 'BRT' else 0,
            1 if mode == 'BUS' else 0,
            1 if mode == 'WALK' else 0
        ]
        return np.array(features).reshape(1, -1)

    def train(self, historical_data: pd.DataFrame = None):
        if historical_data is None:
            historical_data = self._generate_training_data()

        X = historical_data[['hour', 'day_of_week', 'is_morning_rush', 'is_evening_rush',
                            'is_night', 'is_weekend', 'distance', 'joj_multiplier',
                            'weather_factor', 'is_ter', 'is_brt', 'is_bus', 'is_walk']]
        y = historical_data['actual_duration']

        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        self.model = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )
        self.model.fit(X_scaled, y)
        self.is_trained = True
        joblib.dump((self.model, self.scaler), 'traffic_model.pkl')

    def _generate_training_data(self, n_samples: int = 10000) -> pd.DataFrame:
        np.random.seed(42)
        data = {
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'distance': np.random.exponential(5000, n_samples),
            'joj_multiplier': np.random.choice([1.0, 1.5, 2.0], n_samples, p=[0.6, 0.3, 0.1]),
            'weather_factor': np.random.choice([1.0, 1.3, 1.6, 1.2], n_samples, p=[0.5, 0.2, 0.1, 0.2]),
            'mode': np.random.choice(['TER', 'BRT', 'BUS', 'WALK'], n_samples)
        }
        df = pd.DataFrame(data)
        df['is_morning_rush'] = ((df['hour'] >= 7) & (df['hour'] <= 9)).astype(int)
        df['is_evening_rush'] = ((df['hour'] >= 17) & (df['hour'] <= 20)).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        speed_map = {'TER': 27.78, 'BRT': 13.89, 'BUS': 5.56, 'WALK': 1.1}
        df['base_speed'] = df['mode'].map(speed_map)
        df['congestion'] = 1.0 + df['is_morning_rush'] * 0.4 + df['is_evening_rush'] * 0.5
        df['congestion'] += df['is_night'] * 0.1 + df['is_weekend'] * (-0.1)
        df['actual_duration'] = (
            df['distance'] / df['base_speed'] *
            df['congestion'] * df['joj_multiplier'] * df['weather_factor'] +
            np.random.normal(0, 30, n_samples)
        )
        df['actual_duration'] = df['actual_duration'].clip(lower=10)
        df['is_ter'] = (df['mode'] == 'TER').astype(int)
        df['is_brt'] = (df['mode'] == 'BRT').astype(int)
        df['is_bus'] = (df['mode'] == 'BUS').astype(int)
        df['is_walk'] = (df['mode'] == 'WALK').astype(int)
        return df

    def predict_duration(self, hour: int, day_of_week: int,
                        mode: str, distance: float,
                        is_joj_event: bool = False,
                        weather_condition: str = 'normal') -> float:
        if not self.is_trained:
            self.train()
        features = self._extract_features(hour, day_of_week, mode, distance, is_joj_event, weather_condition)
        features_scaled = self.scaler.transform(features)
        return max(10, self.model.predict(features_scaled)[0])

    def predict_journey_duration(self, journey: Journey,
                                  departure_time: datetime,
                                  is_joj_event: bool = False) -> float:
        total = 0
        hour = departure_time.hour
        day_of_week = departure_time.weekday()
        for step in journey.steps:
            predicted = self.predict_duration(hour, day_of_week, step.mode, step.distance_meters, is_joj_event)
            total += predicted
            hour = (hour + int(predicted / 3600)) % 24
        return total

    def get_congestion_level(self, hour: int, day_of_week: int) -> str:
        is_rush = (7 <= hour <= 9) or (17 <= hour <= 20)
        is_weekend = day_of_week >= 5
        if is_weekend:
            return "Faible"
        elif is_rush:
            return "Elevee"
        elif 10 <= hour <= 16:
            return "Moderee"
        return "Faible"