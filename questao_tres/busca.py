import pandas as pd
import ast

movies = pd.read_csv(
    "movies_metadata.csv",
    low_memory=False
)


def extrair_generos(texto):
    if pd.isna(texto):
        return []

    try:
        lista = ast.literal_eval(texto)
        return [g["name"] for g in lista]
    except:
        return []


movies["genres"] = movies["genres"].apply(extrair_generos)

movies["release_date"] = pd.to_datetime(
    movies["release_date"],
    errors="coerce"
)


def buscar_filmes(
    genero=None,
    ano_min=None,
    ano_max=None,
    nota_min=0,
    nota_max=10,
    quantidade=5
):

    resultado = movies.copy()


    # gênero
    if genero:
        resultado = resultado[
            resultado["genres"].apply(
                lambda generos: genero in generos
            )
        ]

    print("Depois do gênero:", len(resultado))

    # ano mínimo
    if ano_min:
        resultado = resultado[
            resultado["release_date"].dt.year >= ano_min
        ]


    # ano máximo
    if ano_max:
        resultado = resultado[
            resultado["release_date"].dt.year <= ano_max
        ]

    print("Depois do ano:", len(resultado))

    # nota mínima
    resultado = resultado[
        resultado["vote_average"] >= nota_min
    ]


    # nota máxima
    resultado = resultado[
        resultado["vote_average"] <= nota_max
    ]

    #print(resultado["vote_average"].describe()) #debug

    # evita filmes com poucas avaliações
    resultado = resultado[
        resultado["vote_count"] >= 50
    ]


    resultado = resultado.sort_values(
        ["vote_average", "vote_count"],
        ascending=False
    )


    return resultado.head(quantidade)
