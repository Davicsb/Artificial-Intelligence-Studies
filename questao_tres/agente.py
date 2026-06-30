import json
import ollama

from busca import buscar_filmes
from prompts import historico


while True:

    resposta = ollama.chat(
        model="llama3.1",
        messages=historico
    )

    texto = resposta["message"]["content"]

    if "PRONTO" in texto:
        break

    print("Agente:", texto)


    historico.append({
        "role":"assistant",
        "content":texto
    })


    usuario = input("Você: ")

    historico.append({
        "role":"user",
        "content":usuario
    })

schema = {
    "type": "object",
    "properties": {
        "genero": {
            "type":"string"
        },
        "ano_min": {
            "type":"integer"
        },
        "ano_max": {
            "type":"integer"
        },
        "nota_min": {
            "type":"number"
        },
        "nota_max": {
            "type":"number"
        }
    },
    "required":["genero"]
}

extracao = [
    {
        "role":"system",
        "content":"""
Extraia as preferências do usuário da conversa.

Retorne somente JSON.
"""
    },
    {
        "role":"user",
        "content": str(historico)
    }
]

resposta = ollama.chat(
    model="llama3.1",
    messages=extracao,
    format=schema
)


filtros = json.loads(
    resposta["message"]["content"]
)


# print(filtros) #debug

filmes = buscar_filmes(
    genero=filtros["genero"],
    ano_min=filtros.get("ano_min"),
    ano_max=filtros.get("ano_max"),
    nota_min=filtros.get("nota_min", 0),
    nota_max=filtros.get("nota_max", 10)
)

if filmes.empty:
    print("Não encontrei filmes com esses filtros.")
    quit()


lista_filmes = ""

for _, filme in filmes.iterrows():

    lista_filmes += f"""
        Título: {filme['title']}
        Ano: {filme['release_date'].year}
        Nota: {filme['vote_average']}
        Sinopse: {filme['overview']}
    """

"""print(filmes[[
    "title",
    "release_date",
    "vote_average"
]]) # debug""" 

resposta_final = ollama.chat(
    model="llama3.1",
    messages=[
        {
            "role":"system",
            "content":"""
Você é um recomendador de filmes.

Use somente os filmes enviados.

Explique:
- por que combina com os filtros
- o ano
- a nota
- uma breve descrição

Não invente filmes.
"""
        },
        {
            "role":"user",
            "content":lista_filmes
        }
    ]
)


print("\nRecomendação:")
print(resposta_final["message"]["content"])
