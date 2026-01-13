import sqlite3
from datetime import datetime
import os

# データベースファイルのパス
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather.db")


def get_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """データベースとテーブルを初期化"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # areasテーブル（地域マスタ）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS areas (
            area_code TEXT PRIMARY KEY,
            area_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # forecastsテーブル（天気予報データ）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            weather_code TEXT NOT NULL,
            weather_name TEXT NOT NULL,
            temp_max TEXT,
            temp_min TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_code) REFERENCES areas(area_code),
            UNIQUE (area_code, forecast_date)
        )
    """)
    
    # インデックスを作成（検索パフォーマンス向上）
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_forecasts_area_date 
        ON forecasts(area_code, forecast_date)
    """)
    
    conn.commit()
    conn.close()


def save_area(area_code, area_name):
    """地域情報を保存（既存の場合は更新しない）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO areas (area_code, area_name)
            VALUES (?, ?)
        """, (area_code, area_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"地域保存エラー: {e}")
    finally:
        conn.close()


def save_forecasts(area_code, forecasts_data):
    """
    天気予報データを保存（UPSERT）
    
    Args:
        area_code: 地域コード
        forecasts_data: 予報データのリスト
            [
                {
                    'date': '2026-01-13',
                    'weather_code': '100',
                    'weather_name': '晴',
                    'temp_max': '10',
                    'temp_min': '2'
                },
                ...
            ]
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        for forecast in forecasts_data:
            cursor.execute("""
                INSERT INTO forecasts 
                (area_code, forecast_date, weather_code, weather_name, temp_max, temp_min)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(area_code, forecast_date) 
                DO UPDATE SET
                    weather_code = excluded.weather_code,
                    weather_name = excluded.weather_name,
                    temp_max = excluded.temp_max,
                    temp_min = excluded.temp_min,
                    fetched_at = CURRENT_TIMESTAMP
            """, (
                area_code,
                forecast['date'],
                forecast['weather_code'],
                forecast['weather_name'],
                forecast['temp_max'],
                forecast['temp_min']
            ))
        conn.commit()
    except sqlite3.Error as e:
        print(f"予報保存エラー: {e}")
    finally:
        conn.close()


def get_forecasts(area_code, days=7):
    """
    指定地域の天気予報を取得
    
    Args:
        area_code: 地域コード
        days: 取得する日数（デフォルト7日）
    
    Returns:
        予報データのリスト
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT forecast_date, weather_code, weather_name, temp_max, temp_min, fetched_at
            FROM forecasts
            WHERE area_code = ?
            ORDER BY forecast_date
            LIMIT ?
        """, (area_code, days))
        
        rows = cursor.fetchall()
        forecasts = []
        for row in rows:
            forecasts.append({
                'date': row['forecast_date'],
                'weather_code': row['weather_code'],
                'weather_name': row['weather_name'],
                'temp_max': row['temp_max'],
                'temp_min': row['temp_min'],
                'fetched_at': row['fetched_at']
            })
        return forecasts
    except sqlite3.Error as e:
        print(f"予報取得エラー: {e}")
        return []
    finally:
        conn.close()


def get_all_areas():
    """すべての地域情報を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT area_code, area_name
            FROM areas
            ORDER BY area_name
        """)
        
        rows = cursor.fetchall()
        areas = {}
        for row in rows:
            areas[row['area_code']] = row['area_name']
        return areas
    except sqlite3.Error as e:
        print(f"地域取得エラー: {e}")
        return {}
    finally:
        conn.close()


def save_all_areas(areas_dict):
    """すべての地域情報を一括保存"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        for area_code, area_name in areas_dict.items():
            cursor.execute("""
                INSERT OR IGNORE INTO areas (area_code, area_name)
                VALUES (?, ?)
            """, (area_code, area_name))
        conn.commit()
    except sqlite3.Error as e:
        print(f"地域一括保存エラー: {e}")
    finally:
        conn.close()
