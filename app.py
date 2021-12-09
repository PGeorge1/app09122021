from flask import Flask, render_template, send_file, request
import time
import seaborn as sns
import pandas as pd

app = Flask(__name__)

links = {"Download" : "/download", # download the full data
         "Pairplot" : "/pairplot",
         "Fair vs Pclass"  : "/fair_vs_pclass",
         "PClass vs Sex" : "/pclass_vs_sex",
         "View Raw Data" : "/view_data",
         "Survived" : "/survived",
         "Passengers" : "/passengers"}


def render_index (image=None, html_string=None, filters=None,  errors=None, current_filter_value=""):
    return render_template("index.html", links=links, image=image, code=time.time(), html_string=html_string,
                           filters=filters, errors=errors, current_filter_value=current_filter_value)

@app.route('/', methods=['GET'])
def main_page():
    return render_index()

@app.route(links["Download"], methods=['GET'])
def download_data():
    return send_file("data/titanic_train.csv", as_attachment=True)


@app.route(links["Pairplot"], methods=['GET'])
def pairplot():
    data = pd.read_csv ("data/titanic_train.csv")
    sns_plot = sns.pairplot(data, hue="Survived")
    sns_plot.savefig("static/tmp/pairplot.png")
    return render_index(image=("pairplot.png", "pairplot"))


@app.route(links["Fair vs Pclass"], methods=['GET'])
def fair_vs_pclass():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    data = pd.read_csv ("data/titanic_train.csv")
    filtered_data = data.query('Fare < 200')
    sns.boxplot(x='Pclass', y='Fare', data=filtered_data, ax=ax)
    plt.savefig('static/tmp/fair_vs_pclass.png')

    return render_index (image=("fair_vs_pclass.png", "Fair vs Passenger class"))


@app.route(links["PClass vs Sex"], methods=['GET'])
def pclass_vs_sex():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    data = pd.read_csv ("data/titanic_train.csv")
    result = {}
    for (cl, sex), sub_df in data.groupby(['Pclass', 'Sex']):
        result[f"{cl} {sex}"] = sub_df['Age'].mean()

    plt.bar (result.keys(), result.values())
    plt.savefig('static/tmp/pclass_vs_sex.png')
    return render_index (("pclass_vs_sex.png", "Passenger class vs Sex"))


@app.route(links["View Raw Data"], methods=['GET', 'POST'])
def view_data():
    df = pd.read_csv("data/titanic_train.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.query(current_filter)
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    html_string = df.to_html()
    return render_index(html_string=html_string, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Passengers"], methods=['GET', 'POST'])
def passengers():
    df = pd.read_csv("data/titanic_train.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.query(current_filter)
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    passengers = list(df["Name"].unique())
    text = "<br/>".join(passengers)
    return render_index(html_string=text, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Survived"], methods=['GET'])
def survived():
    import plotly.express as px
    import pandas as pd
    data = pd.read_csv('data/titanic_train.csv')
    data["new"] = data["Sex"] + data["Survived"].astype(str)
    f = data["new"].value_counts()
    plot = px.pie(values=f.values, names=f.index)
    return render_index(html_string = plot.to_html(full_html=False, include_plotlyjs='cdn'))


if __name__ == '__main__':
    app.run()