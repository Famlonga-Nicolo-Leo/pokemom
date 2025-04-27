from flask import Flask, session, redirect, url_for, render_template, request
import pandas as pd
import random
import os

# Carichiamo il database di carte
CARDS_FILE = "pokemon (1).csv"
cards_df = pd.read_csv(CARDS_FILE)

app = Flask(__name__)
app.secret_key = 'supersegreta'  # serve per gestire la sessione

# Funzione di inizializzazione della sessione
def initialize():
    session['points'] = 100
    session['collection'] = []

# Funzione per pescare una carta rispettando le probabilità
def pick_card():
    rarita = random.choices(
        ['Comune', 'Non Comune', 'Rara', 'Ultra Rara'],
        weights=[70, 20, 9, 1],
        k=1
    )[0]
    carte_possibili = cards_df[cards_df['Rarità'] == rarita]
    
    if carte_possibili.empty:  # Verifica se il DataFrame è vuoto
        raise ValueError(f"Nessuna carta disponibile per la rarità {rarita}")
    
    carta = carte_possibili.sample(1).iloc[0]
    
    # Converte valori int64 in int per evitare problemi di serializzazione
    carta['Valore_Punti'] = int(carta['Valore_Punti'])  # Converte int64 in int
    return carta

@app.route("/", methods=["GET"])
def home():
    if 'points' not in session:
        initialize()
    return render_template("index.html", punti=session['points'], pack=None, collection=None, message=None)

@app.route("/open_pack", methods=["POST"])
def open_pack():
    if session['points'] < 10:
        return render_template("index.html", punti=session['points'], pack=None, collection=None, message="Non hai abbastanza punti!")
    
    session['points'] -= 10
    pack = []
    
    try:
        for _ in range(5):
            carta = pick_card()
            nome = carta['Nome']
            valore = carta['Valore_Punti']
            pack.append(f"{nome} ({carta['Rarità']}) +{valore} punti")
            
            # Aggiungi carta alla collezione
            session['collection'].append(nome)
            
            # Aggiungi i punti bonus
            session['points'] += valore
    except ValueError as e:
        return render_template("index.html", punti=session['points'], pack=None, collection=None, message=str(e))
    
    return render_template("index.html", punti=session['points'], pack=pack, collection=None, message=None)

@app.route("/show_collection", methods=["POST"])
def show_collection():
    return render_template("index.html", punti=session['points'], pack=None, collection=session['collection'], message=None)

@app.route("/save_collection", methods=["POST"])
def save_collection():
    filename = "collezione_salvata.csv"
    pd.DataFrame(session['collection'], columns=['Nome']).to_csv(filename, index=False)
    return render_template("index.html", punti=session['points'], pack=None, collection=None, message=f"Collezione salvata su {filename}")

@app.route("/exit", methods=["GET"])
def exit_game():
    session.clear()
    return "<h1>Hai terminato la sessione. Ciao!</h1><a href='/'>Torna alla Home</a>"

if __name__ == "__main__":
    app.run(debug=True)
