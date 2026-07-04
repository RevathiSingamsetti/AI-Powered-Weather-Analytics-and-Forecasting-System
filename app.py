from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# ADD YOUR API KEY
API_KEY = "78ff47d5e97272daff1b78dbb656e667"


def get_history():

    try:

        with open("history.txt", "r") as file:

            return [

                x.strip()

                for x in file.readlines()

            ]

    except:

        return []


def get_temps():

    try:

        with open("temps.txt", "r") as file:

            return [

                float(x.strip())

                for x in file.readlines()

            ]

    except:

        return []


def create_chart():

    temps = get_temps()

    if temps:

        plt.figure(
            figsize=(6, 4)
        )

        plt.plot(

            range(
                1,
                len(temps) + 1
            ),

            temps,

            marker="o"

        )

        plt.xlabel(
            "Search"
        )

        plt.ylabel(
            "Temperature °C"
        )

        plt.title(
            "Temperature Trend"
        )

        plt.grid()

        plt.savefig(
            "static/chart.png"
        )

        plt.close()


@app.route("/")
def home():

    city = request.args.get(
        "city",
        ""
    ).strip()

    aliases = {

        "vizag":
        "Visakhapatnam",

        "rajamundry":
        "Rajamahendravaram"

    }

    if city.lower() in aliases:

        city = aliases[
            city.lower()
        ]

    temp = None
    condition = None
    icon = None

    humidity = None
    wind = None
    feels_like = None

    prediction = None
    insight = None
    confidence = None

    error = None

    if city:

        response = requests.get(

            "https://api.openweathermap.org/data/2.5/weather",

            params={

                "q": city,

                "appid": API_KEY,

                "units": "metric"

            }

        )

        data = response.json()

        if response.status_code == 200:

            temp = data["main"]["temp"]

            condition = data["weather"][0]["main"]

            humidity = data["main"]["humidity"]

            wind = data["wind"]["speed"]

            feels_like = data["main"]["feels_like"]

            icon_code = data["weather"][0]["icon"]

            icon = (

                f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

            )

            X = np.array([

                [1],
                [2],
                [3]

            ])

            y = np.array([

                temp - 2,

                temp - 1,

                temp

            ])

            model = LinearRegression()

            model.fit(
                X,
                y
            )

            prediction = round(

                model.predict(
                    [[4]]
                )[0],

                1

            )

            if prediction > temp:

                insight = (

                    "🌡 Hotter weather expected • Stay hydrated 💧"

                )

            elif prediction < temp:

                insight = (

                    "🌥 Cooler weather expected • Great for outdoor plans 🌳"

                )

            else:

                insight = (

                    "☁ Stable weather • Comfortable conditions"

                )

            confidence = round(

                90 -

                abs(
                    prediction - temp
                ),

                1

            )

            if confidence < 75:

                confidence = 75

            existing = [

                x.lower()

                for x in get_history()

            ]

            if city.lower() not in existing:

                with open(

                    "history.txt",

                    "a"

                ) as file:

                    file.write(

                        city.title()

                        + "\n"

                    )

            with open(

                "temps.txt",

                "a"

            ) as file:

                file.write(

                    str(temp)

                    + "\n"

                )

            create_chart()

        else:

            error = (

                "❌ City not found. Try another city."

            )

    return render_template(

        "index.html",

        city=city,

        temp=temp,

        condition=condition,

        icon=icon,

        humidity=humidity,

        wind=wind,

        feels_like=feels_like,

        prediction=prediction,

        insight=insight,

        confidence=confidence,

        error=error

    )


@app.route("/history")
def history():

    return render_template(

        "history.html",

        history=get_history()

    )


@app.route("/analytics")
def analytics():

    temps = get_temps()

    total = len(
        get_history()
    )

    highest = max(
        temps,
        default=0
    )

    average = round(

        sum(
            temps
        ) /

        len(
            temps
        ),

        1

    ) if temps else 0

    return render_template(

        "analytics.html",

        total=total,

        highest=highest,

        average=average

    )


@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


@app.route("/forecast")
def forecast():

    city = request.args.get(
        "city",
        "Hyderabad"
    )

    forecast = []

    response = requests.get(

        "https://api.openweathermap.org/data/2.5/forecast",

        params={

            "q": city,

            "appid": API_KEY,

            "units": "metric"

        }

    )

    data = response.json()

    if response.status_code == 200:

        for item in data["list"][:5]:

            forecast.append({

                "temp":
                item["main"]["temp"],

                "weather":
                item["weather"][0]["main"],

                "icon":
                f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",

                "time":
                item["dt_txt"]

            })

    return render_template(

        "forecast.html",

        city=city,

        forecast=forecast

    )


if __name__ == "__main__":

    app.run(
        debug=True
    )