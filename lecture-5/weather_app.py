import flet as ft
import requests
import json
from datetime import datetime
import os

# 地域リストを取得
def get_area_list():
    url = "http://www.jma.go.jp/bosai/common/const/area.json"
    response = requests.get(url)
    return response.json()

# 天気予報を取得
def get_weather_forecast(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    response = requests.get(url)
    return response.json()

# 天気コードに基づいてアイコンと説明を選択
def get_weather_info(weather_code):
    """気象庁の天気コードに基づいてアイコンパスと天気説明を返す"""
    code = str(weather_code)
    
    # 天気コードマッピングテーブル
    weather_map = {
        "100": ("晴", "clear_day.svg"),
        "101": ("晴時々曇", "partly_cloudy_day.svg"),
        "102": ("晴一時雨", "sunny_with_rain_light.svg"),
        "103": ("晴時々雨", "sunny_with_rain_light.svg"),
        "104": ("晴一時雪", "sunny_with_snow_light.svg"),
        "110": ("晴後曇", "mostly_clear_day.svg"),
        "111": ("晴後雨", "sunny_with_rain_light.svg"),
        "112": ("晴後雪", "sunny_with_snow_light.svg"),
        "200": ("曇", "cloudy.svg"),
        "201": ("曇時々晴", "cloudy_with_sunny_light.svg"),
        "202": ("曇一時雨", "cloudy_with_rain_light.svg"),
        "203": ("曇時々雨", "cloudy_with_rain_light.svg"),
        "204": ("曇一時雪", "cloudy_with_snow_light.svg"),
        "210": ("曇後晴", "cloudy_with_sunny_light.svg"),
        "211": ("曇後雨", "cloudy_with_rain_light.svg"),
        "212": ("曇後雪", "cloudy_with_snow_light.svg"),
        "300": ("雨", "showers_rain.svg"),
        "301": ("雨時々晴", "rain_with_sunny_light.svg"),
        "302": ("雨時々曇", "rain_with_cloudy_light.svg"),
        "303": ("雨時々雪", "rain_with_snow_light.svg"),
        "400": ("雪", "showers_snow.svg"),
        "401": ("雪時々晴", "snow_with_sunny_light.svg"),
        "402": ("雪時々曇", "snow_with_cloudy_light.svg"),
    }
    
    # 天気情報を取得、コードが存在しない場合はデフォルト値を返す
    weather_name, icon_file = weather_map.get(code, ("曇", "cloudy.svg"))
    # 絶対パスを使用
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icons", icon_file)
    
    return weather_name, icon_path

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 20
    page.scroll = "auto"
    
    # ダークモードを設定
    page.theme_mode = ft.ThemeMode.DARK
    
    # アセットディレクトリを設定
    current_dir = os.path.dirname(os.path.abspath(__file__))
    page.assets_dir = current_dir
    
    # グローバル変数
    area_data = None
    current_area_code = "130000"  # 東京の地域コード
    current_area_name = "東京都"
    
    # 天気カードを作成
    def create_weather_card(date_str, weather, temp_max, temp_min, icon_path):
        # Material You ダークモードカラーパレット
        return ft.Container(
            content=ft.Column([
                ft.Text(date_str, size=14, weight=ft.FontWeight.BOLD, color="#E6E1E5"),
                ft.Image(src=icon_path, width=60, height=60),
                ft.Text(weather, size=12, text_align=ft.TextAlign.CENTER, color="#CAC4D0"),
                ft.Text(f"{temp_max}°C", size=14, color="#FFB4AB"),  # Material You Red
                ft.Text(f"{temp_min}°C", size=14, color="#A8C7FA"),  # Material You Blue
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=15,
            border=ft.border.all(1, "#49454F"),  # Material You outline
            border_radius=12,
            bgcolor="#1D1B20",  # Material You surface container
            width=120,
        )
    
    # メインページを表示（天気予報）
    def show_weather_page():
        try:
            # 天気データを取得
            forecast_data = get_weather_forecast(current_area_code)
            
            # 2番目の予報データを使用（週間予報、7日間）
            if len(forecast_data) < 2:
                page.add(ft.Text("週間予報データがありません", color=ft.Colors.RED))
                page.update()
                return
            
            # 今日の気温データを取得（3日間詳細予報から）
            today_temps = {"max": None, "min": None}
            if len(forecast_data) > 0:
                detail_forecast = forecast_data[0]
                if "timeSeries" in detail_forecast and len(detail_forecast["timeSeries"]) > 1:
                    for ts in detail_forecast["timeSeries"]:
                        if "temps" in ts["areas"][0]:
                            temps_list = ts["areas"][0]["temps"]
                            if len(temps_list) >= 2:
                                today_temps["min"] = temps_list[0]
                                today_temps["max"] = temps_list[1]
                            break
            
            week_forecast = forecast_data[1]
            time_series = week_forecast["timeSeries"][0]
            
            # 日付と天気コードを取得
            dates = time_series["timeDefines"]
            weather_codes = time_series["areas"][0]["weatherCodes"]
            
            # 気温データを取得
            temps = []
            if len(week_forecast["timeSeries"]) > 1:
                temp_series = week_forecast["timeSeries"][1]
                if "areas" in temp_series and len(temp_series["areas"]) > 0:
                    area_temps = temp_series["areas"][0]
                    if "tempsMin" in area_temps:
                        temps_min = area_temps["tempsMin"]
                    else:
                        temps_min = []
                    if "tempsMax" in area_temps:
                        temps_max = area_temps["tempsMax"]
                    else:
                        temps_max = []
                    temps = {"min": temps_min, "max": temps_max}
            
            # 天気カードリストを作成
            weather_cards = []
            for i in range(min(7, len(dates))):
                date_obj = datetime.fromisoformat(dates[i].replace('Z', '+00:00'))
                date_str = date_obj.strftime("%m/%d")
                
                # 天気コードを取得して情報に変換
                weather_code = weather_codes[i] if i < len(weather_codes) else "200"
                weather_name, icon_path = get_weather_info(weather_code)
                
                # 気温を取得
                # 今日（最初の日付）の場合、詳細予報の気温を優先的に使用
                if i == 0 and (today_temps["max"] is not None or today_temps["min"] is not None):
                    temp_max = today_temps["max"] if today_temps["max"] is not None else "--"
                    temp_min = today_temps["min"] if today_temps["min"] is not None else "--"
                elif temps:
                    temp_max = temps["max"][i] if i < len(temps["max"]) else "--"
                    temp_min = temps["min"][i] if i < len(temps["min"]) else "--"
                else:
                    temp_max = "--"
                    temp_min = "--"
                
                card = create_weather_card(date_str, weather_name, temp_max, temp_min, icon_path)
                weather_cards.append(card)
            
            # ページ内容を更新
            page.controls.clear()
            page.add(
                # トップバー
                ft.Row([
                    ft.Text(current_area_name, size=24, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.LOCATION_CITY,
                        on_click=lambda _: show_city_list()
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # 天気カードグリッド
                ft.Row(
                    weather_cards,
                    wrap=True,
                    spacing=10,
                    run_spacing=10,
                )
            )
            page.update()
            
        except Exception as e:
            import traceback
            error_msg = f"エラー: {str(e)}\n{traceback.format_exc()}"
            page.controls.clear()
            page.add(ft.Text(error_msg, color=ft.Colors.RED))
            page.update()
    
    # 都市リストページを表示
    def show_city_list():
        nonlocal area_data
        
        if area_data is None:
            area_data = get_area_list()
        
        # 検索ボックスを作成
        search_field = ft.TextField(
            label="都市を検索",
            on_change=lambda e: filter_cities(e.control.value)
        )
        
        # 都市リストを作成
        city_list_view = ft.ListView(spacing=10, padding=20, auto_scroll=False)
        
        def filter_cities(search_text):
            city_list_view.controls.clear()
            
            # すべての地域を走査
            offices = area_data.get("offices", {})
            for code, info in offices.items():
                name = info.get("name", "")
                if search_text == "" or search_text in name:
                    city_list_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(name),
                            on_click=lambda _, c=code, n=name: select_city(c, n)
                        )
                    )
            page.update()
        
        def select_city(code, name):
            nonlocal current_area_code, current_area_name
            current_area_code = code
            current_area_name = name
            show_weather_page()
        
        # 初期表示のすべての都市
        filter_cities("")
        
        # ページを更新
        page.controls.clear()
        page.add(
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda _: show_weather_page()
                ),
                ft.Text("都市を選択", size=24, weight=ft.FontWeight.BOLD),
            ]),
            search_field,
            ft.Divider(),
            ft.Container(
                content=city_list_view,
                expand=True,
            )
        )
        page.update()
    
    # 初期表示の天気ページ
    show_weather_page()

ft.app(target=main)
