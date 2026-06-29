from owlready2 import *

# 1. Criação da Ontologia
onto_path.append(".")
onto = get_ontology("http://test.org/filmes.owl")

with onto:

    # CLASSES (Mínimo 10) e HIERARQUIA

    class Genero(Thing): pass
    
    class Pessoa(Thing): pass
    class Ator(Pessoa): pass
    class Diretor(Pessoa): pass
    
    class Usuario(Thing): pass
    
    class Filme(Thing): pass
    class FilmeAcao(Filme): pass
    class FilmeFiccao(Filme): pass
    class FilmeDrama(Filme): pass
    class FilmeComedia(Filme): pass

    # PROPRIEDADES (Mínimo 15: Object e Data Properties)

    # Object Properties (Relacionamentos)
    class temGenero(ObjectProperty): 
        domain = [Filme]; range = [Genero]
    
    class atuouEm(ObjectProperty): 
        domain = [Ator]; range = [Filme]
    class temAtor(ObjectProperty): 
        domain = [Filme]; range = [Ator]
        inverse_property = atuouEm
        
    class dirigiu(ObjectProperty): 
        domain = [Diretor]; range = [Filme]
    class temDiretor(ObjectProperty): 
        domain = [Filme]; range = [Diretor]
        inverse_property = dirigiu
        
    class gostaDeGenero(ObjectProperty): 
        domain = [Usuario]; range = [Genero]
    class gostaDeAtor(ObjectProperty): 
        domain = [Usuario]; range = [Ator]
        
    class assistiu(ObjectProperty): 
        domain = [Usuario]; range = [Filme]
    class recomendadoPara(ObjectProperty): 
        domain = [Usuario]; range = [Filme]

    # Data Properties (Atributos)
    class titulo(DataProperty): 
        domain = [Filme]; range = [str]
    class anoLancamento(DataProperty): 
        domain = [Filme]; range = [int]
    class notaIMDB(DataProperty): 
        domain = [Filme]; range = [float]
    class duracaoMinutos(DataProperty): 
        domain = [Filme]; range = [int]
    class nomeUsuario(DataProperty): 
        domain = [Usuario]; range = [str]
    class idadeUsuario(DataProperty): 
        domain = [Usuario]; range = [int]

    # RESTRIÇÕES E AXIOMAS (Classificação Automática)
    # Axiomas de Equivalência: Um filme é classificado automaticamente
    # pelas suas instâncias de gênero sem precisarmos setar a classe manualmente.
    FilmeAcao.equivalent_to = [Filme & temGenero.some(onto.Genero("Acao"))]
    FilmeFiccao.equivalent_to = [Filme & temGenero.some(onto.Genero("FiccaoCientifica"))]
    
    # Regras SWRL (Semantic Web Rule Language) para o Sistema de Recomendação
    # Regra 1: Se o usuário gosta de um gênero e o filme tem esse gênero -> Recomendar
    regra_genero = Imp()
    regra_genero.set_as_rule("Usuario(?u), Filme(?f), gostaDeGenero(?u, ?g), temGenero(?f, ?g) -> recomendadoPara(?u, ?f)")
    
    # Regra 2: Se o usuário gosta de um ator e o filme tem esse ator -> Recomendar
    regra_ator = Imp()
    regra_ator.set_as_rule("Usuario(?u), Filme(?f), gostaDeAtor(?u, ?a), temAtor(?f, ?a) -> recomendadoPara(?u, ?f)")

    # INDIVÍDUOS (Instâncias da Base de Conhecimento)
 
    # Gêneros
    acao = Genero("Acao")
    ficcao = Genero("FiccaoCientifica")
    drama = Genero("Drama")

    # Pessoas (Atores e Diretores)
    keanu = Ator("Keanu_Reeves")
    dicaprio = Ator("Leonardo_DiCaprio")
    nolan = Diretor("Christopher_Nolan")
    wachowski = Diretor("Lana_Wachowski")

    # Filmes (Note que os instanciamos apenas como "Filme", o Reasoner descobrirá a subclasse)
    matrix = Filme("The_Matrix", titulo=["The Matrix"], anoLancamento=[1999], notaIMDB=[8.7], 
                   temGenero=[acao, ficcao], temAtor=[keanu], temDiretor=[wachowski])
    
    inception = Filme("Inception", titulo=["A Origem"], anoLancamento=[2010], notaIMDB=[8.8], 
                      temGenero=[ficcao, acao], temAtor=[dicaprio], temDiretor=[nolan])
    
    interstellar = Filme("Interstellar", titulo=["Interestelar"], anoLancamento=[2014], notaIMDB=[8.6], 
                         temGenero=[ficcao, drama], temDiretor=[nolan])
    
    john_wick = Filme("John_Wick", titulo=["De Volta ao Jogo"], anoLancamento=[2014], notaIMDB=[7.4], 
                      temGenero=[acao], temAtor=[keanu])

    # Usuário Ativo
    joao = Usuario("Joao_Silva", nomeUsuario=["João da Silva"], idadeUsuario=[25], 
                   gostaDeGenero=[ficcao], gostaDeAtor=[keanu])



# EXECUÇÃO DO REASONER E SISTEMA DE RECOMENDAÇÃO

if __name__ == "__main__":
    print("\n🔍 Executando o Motor de Raciocínio Semântico (Pellet)...")
    # Rodamos o Pellet para classificar instâncias e inferir as Regras SWRL
    with onto:
        sync_reasoner(infer_property_values=True)
    
    print("✔ Inferências automáticas concluídas!\n")
    
    # Salvar a Ontologia (Entregável 1 exigido pelo professor)
    arquivo_owl = "ontologia_filmes.owl"
    onto.save(file=arquivo_owl, format="rdfxml")
    print(f"📁 Ontologia OWL salva no arquivo: {arquivo_owl}\n")


    # RESULTADOS DA RECOMENDAÇÃO

    print("="*60)
    print(f"🎬 SISTEMA DE RECOMENDAÇÃO BASEADO EM ONTOLOGIAS")
    print("="*60)
    print(f"👤 Usuário: {joao.nomeUsuario[0]}")
    print(f"⭐ Interesses Declarados:")
    print(f"   - Gêneros: {[g.name for g in joao.gostaDeGenero]}")
    print(f"   - Atores:  {[a.name for a in joao.gostaDeAtor]}")
    print("-"*60)
    
    print("\n✅ FILMES RECOMENDADOS PELO REASONER (Raciocínio Implícito):")
    if not joao.recomendadoPara:
        print("   Nenhuma recomendação encontrada.")
    else:
        for filme in joao.recomendadoPara:
            print(f" 🍿 {filme.titulo[0]} ({filme.anoLancamento[0]})")
            
            # Justificando a recomendação cruzando dados semânticos:
            motivos = []
            if set(joao.gostaDeGenero).intersection(set(filme.temGenero)):
                motivos.append("Gênero que você gosta")
            if set(joao.gostaDeAtor).intersection(set(filme.temAtor)):
                motivos.append("Ator que você acompanha")
            print(f"    ↳ Justificativa: {', '.join(motivos)}")
            
            # Demonstrando a classificação automática da Hierarquia
            classes_inferidas = [c.name for c in filme.INDIRECT_is_a if c.name not in ["Thing", "Filme", "NamedIndividual"]]
            if classes_inferidas:
                print(f"    ↳ Classificação Semântica Inferida: {', '.join(classes_inferidas)}")
            print()
    print("="*60)