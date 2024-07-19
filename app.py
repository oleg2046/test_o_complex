import requests
from flask import Flask, render_template, request
from res_meteo import res_meteo

app = Flask(__name__)


def get_coordinates(city):      # Запрос координат определенного города
    url = f'https://nominatim.openstreetmap.org/search?city={city}&format=json&limit=1'
    responce = requests.get(url)
    print(responce)
    if responce.status_code == 200:
        data = responce.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    weather_data_2 = None
    error = {}
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            lat, lon = get_coordinates(city)
            if lat is not None and lon is not None:
                try:
                    weather_data = res_meteo(lat, lon, city.capitalize())
                    weather_data, weather_data_2 = weather_data[0], weather_data[1:]
                except:
                    error = {'Ошибка': 'Данные о погоде не могут быть получены'}
            else:
                error = {'Ошибка': 'Город не определен'}
    return render_template('index.html', weather_data=weather_data, weather_data_2=weather_data_2, error=error)


if __name__ == '__main__':
    app.run(debug=True)
