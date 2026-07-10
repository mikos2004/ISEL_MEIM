# ==============================================================
# FASE 2 - ABox
# ==============================================================
# Miguel Alcobia - 50746
# Fábio Pestana - 50756

##########
# NOTA: schema.rdf é o RDF com o schema usado pelo https://sparql.dblp.org/sparql
##########


from rdflib import Graph, Namespace, Literal
from rdflib import RDF, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON
import warnings
import re
import unicodedata

# ===============
# CONFIGURAÇÕES
# ===============

# Endpoint SPARQL do DBLP
DBLP_ENDPOINT = "https://sparql.dblp.org/sparql"

# Namespace da ontologia da fase
RPC = Namespace("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#")

# Namespace do DBLP (conforme schema.rdf)
DBLP = Namespace("https://dblp.org/rdf/schema#")

# default
RDF_NS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS_NS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Prefixos
RPC_PREFIX = "rpc"


# ==============================================================
# MAPEAMENTO DE RPC E DBLP (pq metia em Annotations)
# ==============================================================

# Propriedades de objeto (ObjectProperty)
OBJECT_PROPERTIES = {
    RPC["author"]: "ObjectProperty",
    RPC["author_inv"]: "ObjectProperty",
    RPC["affiliation"]: "ObjectProperty",
    RPC["publisher"]: "ObjectProperty",
    RPC["cites"]: "ObjectProperty",
    RPC["coauthor"]: "ObjectProperty",
    RPC["editor"]: "ObjectProperty",
    RPC["at_university"]: "ObjectProperty",
    RPC["chapter_of"]: "ObjectProperty",
    RPC["in_series"]: "ObjectProperty",
    RPC["isIncludedIn"]: "ObjectProperty",
}

# Propriedades de dados (DatatypeProperty)
DATATYPE_PROPERTIES = {
    RPC["name"]: "DatatypeProperty",
    RPC["title"]: "DatatypeProperty",
    RPC["journal_name"]: "DatatypeProperty",
    RPC["book_title"]: "DatatypeProperty",
    RPC["year"]: "DatatypeProperty",
    RPC["month"]: "DatatypeProperty",
    RPC["pages"]: "DatatypeProperty",
    RPC["volume"]: "DatatypeProperty",
    RPC["number"]: "DatatypeProperty",
    RPC["isbn"]: "DatatypeProperty",
    RPC["ee"]: "DatatypeProperty",
    RPC["cdrom"]: "DatatypeProperty",
    RPC["chapter"]: "DatatypeProperty",
    RPC["last_modified_date"]: "DatatypeProperty",
}

# ==============================================================
# FUNÇÕES AUXILIARES PARA NORMALIZAR NOMES
# ==============================================================

def normalizar_para_uri(nome):
    """Normaliza um nome para usar como URI

    - Converte para lowercase
    - Remove acentos
    - Substitui espaços e chars especiais por underscore

    Args:
        nome

    Returns:
        nome normalizado
    """
    nome = nome.lower()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r'[^\w\s-]', '', nome)
    nome = re.sub(r'[\s-]+', '_', nome)
    nome = nome.strip('_')
    return nome


def gerar_uri_pessoa(nome_autor):
    """Gera URI para pessoa no namespace RPC

    Args:
        nome_autor

    Returns:
        RPC[nome_normalizado]: uri no NS do RPC
    """
    nome_normalizado = normalizar_para_uri(nome_autor)
    return RPC[nome_normalizado]


def gerar_uri_publicacao(titulo, ano=None):
    """Gera URI para publicação baseada no título e ano

    Args:
        titulo
        ano

    Returns:
        RPC[uri_str]: uri da Publicação no NS do RPC
    """
    titulo_normalizado = normalizar_para_uri(titulo)

    if ano:
        uri_str = f"{titulo_normalizado}_{ano}"
    else:
        uri_str = titulo_normalizado
    return RPC[uri_str]


def gerar_uri_organizacao(nome_organizacao):
    """Gera URI para organização no namespace RPC

    Args:
        nome_organizacao

    Returns:
        RPC[nome_normalizado]: uri da organização no NS do RPC
    """
    nome_normalizado = normalizar_para_uri(nome_organizacao)
    return RPC[nome_normalizado]


def processar_multiplas_publishers(editora_str):
    """Processa uma string que pode conter múltiplas publishers separadas por vírgulas
    
    Args:
        editora_str: String com nome(s) da(s) publisher(s)
        
    Returns:
        list: Lista de nomes de publishers individuais
    """
    if not editora_str:
        return []
    
    # Divide por vírgula e remove espaços extras
    publishers = [pub.strip() for pub in editora_str.split(',')]
    
    # Remove entradas vazias
    publishers = [pub for pub in publishers if pub]
    
    return publishers


# ================================
# CLASSE PARA ACEDER AO SPARQL DBLP
# ================================

class DBLPClient:
    
    def __init__(self, endpoint=DBLP_ENDPOINT):
        """Construtor"""
        self.endpoint = endpoint
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setTimeout(30)
    
    def consultar(self, query):
        """Consultar dblp

        Args:
            query: Query SPARQL

        Returns:
            resultado da query
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        try:
            return self.sparql.query().convert()
        except Exception as e:
            warnings.warn(f"Erro na consulta: {e}")
            return None
    
    def _processar_resultado(self, resultado):
        """Processar resultado

        Args:
            resultado: resutlado da query

        Returns:
            resultados da query
        """
        if not resultado:
            return None, None
        vars_list = resultado.get('head', {}).get('vars', [])
        bindings = resultado.get('results', {}).get('bindings', [])
        resultados = []
        for binding in bindings:
            linha = {}
            for var in vars_list:
                linha[var] = binding.get(var, {}).get('value', None) if var in binding else None
            resultados.append(linha)
        return vars_list, resultados
    
    def procurar_autores(self, limite=20):
        """Procura autores dinamicamente do DBLP
        
        Args:
            limite: Número máximo de autores a procurar (default: 20)
            
        Returns:
            list: Lista de dicionários com informações dos autores
        """

        query = f"""
        PREFIX dblp: <https://dblp.org/rdf/schema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?autor ?nomeAutor WHERE {{
          ?autor a dblp:Person ;
                 rdfs:label ?nomeAutor .
        }}
        LIMIT {limite}
        """
        
        _, resultados = self._processar_resultado(self.consultar(query))
        
        autores = []
        if resultados:
            for row in resultados:
                autores.append(row.get('nomeAutor', ''))
        
        return autores
    
    def procurar_publicacoes_por_autor(self, nome_autor):
        """Procurar publicações por autor
        Args:
            nome_autor: Nome do autor

        Returns:
            list: Lista de dicionários com as publicações do autor
        """

        nome_clean = nome_autor.replace("'", "\\'").replace('"', '\\"')
        
        query = f"""
        PREFIX dblp: <https://dblp.org/rdf/schema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT DISTINCT ?pub ?titulo ?ano ?tipo ?editora ?journal
        WHERE {{
            # Autor pelo rótulo
            ?autor rdfs:label "{nome_clean}" .
            
            # Publicação que ele assina
            ?pub dblp:authoredBy ?autor .
            
            # Título da publicação
            ?pub dblp:title ?titulo .
            
            # Ano (opcional) - usando yearOfPublication
            OPTIONAL {{ ?pub dblp:yearOfPublication ?ano . }}
            
            # Tipo da publicação
            OPTIONAL {{ ?pub rdf:type ?tipo . }}
            
            # Editora - tentando propriedades mais comuns no schema
            OPTIONAL {{ ?pub dblp:publishedBy ?editora . }}
            
            # Journal - para artigos de journal
            OPTIONAL {{ ?pub dblp:publishedIn ?journal . }}
        }}
        ORDER BY ?ano
        LIMIT 500
        """

        # Executa a query e processa o resultado
        _, resultados = self._processar_resultado(self.consultar(query))

        publicacoes = []

        if resultados:
            for row in resultados:
                # Cria um dicionário com os dados brutos da publicação
                pub = {
                    'uri': row.get('pub'),
                    'titulo': row.get('titulo', ''),
                    'ano': row.get('ano', None),
                    'tipo_dblp': row.get('tipo', None),
                    'editora': row.get('editora', None),
                    'journal': row.get('journal', None)  # Adiciona o campo journal
                }

                # Extrai um nome para o tipo da publicação
                if pub['tipo_dblp']:
                    pub['tipo_nome'] = pub['tipo_dblp'].split('#')[-1] if '#' in pub['tipo_dblp'] else pub['tipo_dblp'].split('/')[-1]
                else:
                    pub['tipo_nome'] = None

                # Extrai um nome para a editora
                if pub['editora']:
                    pub['editora_nome'] = pub['editora'].split('#')[-1] if '#' in pub['editora'] else pub['editora'].split('/')[-1]
                else:
                    pub['editora_nome'] = None
                
                # Extrai o nome do journal
                if pub['journal']:
                    # Se for URI, extrai o nome
                    if pub['journal'].startswith('http'):
                        pub['journal_nome'] = pub['journal'].split('#')[-1] if '#' in pub['journal'] else pub['journal'].split('/')[-1]
                    else:
                        pub['journal_nome'] = pub['journal']
                else:
                    pub['journal_nome'] = None

                publicacoes.append(pub)

        return publicacoes


# ==============================================================
# MAP DE CLASSES DBLP -> RPC
# ==============================================================

# Dict para fazer o map

MAPEAMENTO_STR_RPC = {
    "Article": RPC["Article_in_Journal"],
    "Inproceedings": RPC["Article_in_Proceedings"],
    "Incollection": RPC["Article_in_Proceedings"],
    "Book": RPC["Book"],
    "Editorship": RPC["Document"],
    "Reference": RPC["Document"],
    "Data": RPC["Document"],
    "Informal": RPC["Document"],
}


def mapear_classe_dblp_para_rpc(tipo_dblp):
    """Converte o tipo de publicação DBLP para RPC

    Args:
        tipo_dblp

    Returns:
        tipo RPC
    """

    # Caso 1: tipo_dblp é None, vazio ou inválido: retorna tipo padrão "Document"
    if not tipo_dblp:
        return RPC["Document"]
    
    # Caso 2: tipo_dblp é uma URI completa
    if isinstance(tipo_dblp, str) and tipo_dblp.startswith("http"):
        # Extrai o nome da classe da URI (usa a parte após # ou após a última /)
        nome_classe = tipo_dblp.split('#')[-1] if '#' in tipo_dblp else tipo_dblp.split('/')[-1]

        # Verifica se o nome extraído está no map
        if nome_classe in MAPEAMENTO_STR_RPC:
            return MAPEAMENTO_STR_RPC[nome_classe]
        
    # Caso 3: tipo_dblp já é uma string simples com o nome da classe
    if isinstance(tipo_dblp, str) and tipo_dblp in MAPEAMENTO_STR_RPC:
        return MAPEAMENTO_STR_RPC[tipo_dblp]
    
    # Caso padrão: se nenhum map foi encontrado, retorna tipo "Document"
    return RPC["Document"]


# ============================
# DECLARAR PROPRIEDADES 
# ============================

def declarar_propriedades_se_necessario(g, propriedade, tipo):
    """Declara a propriedade no grafo com o tipo correto (ObjectProperty ou DatatypeProperty)

    Args:
        g: grafo
        propriedade
        tipo
    """
    # Verifica se a propriedade já foi declarada como ObjectProperty
    if (propriedade, RDF.type, OWL_NS["ObjectProperty"]) in g:
        return
    
    # Verifica se a propriedade já foi declarada como DatatypeProperty
    if (propriedade, RDF.type, OWL_NS["DatatypeProperty"]) in g:
        return
    
    # Se a propriedade ainda não foi declarada, declara com o tipo especificado
    if tipo == "ObjectProperty":
        g.add((propriedade, RDF.type, OWL_NS["ObjectProperty"]))
    elif tipo == "DatatypeProperty":
        g.add((propriedade, RDF.type, OWL_NS["DatatypeProperty"]))


# ==============================================================
# FUNÇÃO PARA CRIAR GRAFO INPUT
# ==============================================================

def criar_grafo_input(nome_ficheiro="z01_meu_grafo_INPUT.rdf", limite_autores=20):
    """Cria o grafo de INPUT

    Args:
        nome_ficheiro (str, optional): Nome do ficheiro rdf do grafo.
        limite_autores: Limite na quantidade de autores (default = 20)

    Returns:
        g: grafo
    """

    print("\n" + "="*70)
    print("CRIAÇÃO DO GRAFO INPUT")
    print("="*70)
    
    # cria o grafo
    g = Graph()
    
    # prefixos
    g.bind(RPC_PREFIX, RPC)
    g.bind("rdf", RDF_NS)
    g.bind("rdfs", RDFS_NS)
    g.bind("owl", OWL_NS)
    
    # Declara a propriedade "name" como uma DatatypeProperty
    declarar_propriedades_se_necessario(g, RPC["name"], "DatatypeProperty")
    
    # Lista de autores a serem adicionados ao grafo INPUT
    #  (estes dois primeiros serviram para comparação com a aula prática)
    #  Por esse motivo estão hardcoded
    autores = [
        "Edsger W. Dijkstra",
        "Frederic Brenton Fitch"
    ]

    dblp_client = DBLPClient()
    autores += dblp_client.procurar_autores(limite=limite_autores)
    
    for nome in autores:
        # Gera uma URI única para a pessoa com base no nome
        pessoa_uri = gerar_uri_pessoa(nome)

        # Declara que esta URI é uma instância da classe Person do RPC
        g.add((pessoa_uri, RDF.type, RPC["Person"]))

        # Adiciona o nome da pessoa como uma propriedade literal
        g.add((pessoa_uri, RPC["name"], Literal(nome)))

        print(f"  [pass] Criada URI: {pessoa_uri}")
    
    # Serializa o grafo para um ficheiro RDF/XML
    g.serialize(destination=nome_ficheiro, format="pretty-xml")
    
    print(f"\n[pass] Grafo INPUT guardado em: {nome_ficheiro}")
    print(f"  Autores: {autores}")
    print(f"  Nº de autores: {len(autores)}")
    
    return g


# ================================
# FUNÇÃO PARA CRIAR GRAFO OUTPUT
# ================================

def criar_grafo_output_com_dblp(nome_ficheiro_input="z01_meu_grafo_INPUT.rdf",
                                nome_ficheiro_output="z01_meu_grafo_OUTPUT.rdf"):
    """Cria o ficheiro OUTPUT

    Mapeia dblp:publishedBy -> rpc:publisher (aponta para rpc:Publishing_Organization)

    Returns:
        g_output: grafo output
    """
    
    print("\n" + "="*70)
    print("CRIAÇÃO DO GRAFO OUTPUT")
    print("="*70)
    
    # Carregar o grafo INPUT
    g_input = Graph()
    g_input.parse(nome_ficheiro_input, format="xml")
    
    # Extrair os autores
    query_autores = f"""
    SELECT ?pessoa ?nome WHERE {{
        ?pessoa rdf:type <{RPC}Person> .
        ?pessoa <{RPC}name> ?nome .
    }}
    """
    
    autores = []
    for row in g_input.query(query_autores):
        # extrai o uri e o nome do autor da resposta da query
        pessoa_uri = row[0]
        nome = str(row[1])
        autores.append((pessoa_uri, nome))
    
    print(f"\n.:: Autores encontrados no INPUT:")
    for uri, nome in autores:
        print(f"     {nome} -> {uri}")
    
    # Criar novo grafo para OUTPUT
    g_output = Graph()
    
    # definir namespaces
    g_output.bind(RPC_PREFIX, RPC)
    g_output.bind("rdf", RDF_NS)
    g_output.bind("rdfs", RDFS_NS)
    g_output.bind("owl", OWL_NS)
    
    # ==========================================
    # DECLARAR PROPRIEDADES COM O TIPO CORRETO
    # ==========================================

    for prop in OBJECT_PROPERTIES:
        declarar_propriedades_se_necessario(g_output, prop, "ObjectProperty")
    
    for prop in DATATYPE_PROPERTIES:
        declarar_propriedades_se_necessario(g_output, prop, "DatatypeProperty")
    
    # Declarar classes necessárias
    g_output.add((RPC["Publishing_Organization"], RDF.type, OWL_NS["Class"]))
    g_output.add((RPC["Publishing_Organization"], RDFS.subClassOf, RPC["Organization"]))
    
    # ==========================================================
    # PROCESSAR AUTORES E PUBLICACOES
    # ==========================================================
    
    total_publicacoes = 0
    organizacoes = set()  # Set para evitar duplicados
    publicacoes_processadas = set()  # Set para evitar processar a mesma publicação duas vezes
    
    for pessoa_uri, nome_autor in autores:
        print(f"\n[searching] A processar: {nome_autor}")
        
        # Obtém as publicações do autor
        dblp = DBLPClient()
        publicacoes = dblp.procurar_publicacoes_por_autor(nome_autor)
        if not publicacoes:
            print(f"   [warning] Nenhuma publicação encontrada, usando dados de exemplo")
        else:
            print(f"   [pass] {len(publicacoes)} publicações encontradas no DBLP")
        
        
        # Colocar a pessoa no OUTPUT
        g_output.add((pessoa_uri, RDF.type, RPC["Person"]))
        g_output.add((pessoa_uri, RPC["name"], Literal(nome_autor)))
        
        # Mapear cada publicação
        for pub_info in publicacoes:
            titulo = pub_info.get('titulo', '')
            ano = pub_info.get('ano', None)
            tipo_nome = pub_info.get('tipo_nome', None)
            editora_nome = pub_info.get('editora_nome', None)
            journal_nome = pub_info.get('journal_nome', None)  # Obtém o nome do journal
            
            # Map das classes
            classe_rpc = mapear_classe_dblp_para_rpc(tipo_nome)
            
            # Gerar URI para publicação
            pub_uri = gerar_uri_publicacao(titulo, ano)
            
            # Ligar pessoa à publicação (mesmo que já processada para outro autor)
            g_output.add((pessoa_uri, RPC["author_inv"], pub_uri))

            # Se a publicação já foi processada, não repetir os dados
            if pub_uri in publicacoes_processadas:
                continue
            publicacoes_processadas.add(pub_uri)

            # Adicionar tipos
            g_output.add((pub_uri, RDF.type, RPC["Document"]))
            g_output.add((pub_uri, RDF.type, classe_rpc))
            
            # Adicionar título com propriedade correta
            if classe_rpc == RPC["Article_in_Journal"]:
                journal_value = titulo
                g_output.add((pub_uri, RPC["journal_name"], Literal(journal_value)))
            elif classe_rpc == RPC["Article_in_Proceedings"]:
                g_output.add((pub_uri, RPC["title"], Literal(titulo)))
            elif classe_rpc == RPC["Book"]:
                g_output.add((pub_uri, RPC["book_title"], Literal(titulo)))
            else:
                g_output.add((pub_uri, RPC["title"], Literal(titulo)))
            
            # Adicionar ano
            if ano:
                g_output.add((pub_uri, RPC["year"], Literal(ano)))
            
            # Mapear dblp:publishedBy -> rpc:publisher (aponta para rpc:Publishing_Organization)
            # Suporte para múltiplas publishers separadas por vírgulas
            if editora_nome:
                # Processa múltiplas publishers
                publishers_list = processar_multiplas_publishers(editora_nome)
                
                for pub_nome in publishers_list:
                    # URI para a Org
                    org_uri = gerar_uri_organizacao(pub_nome)
                    if org_uri not in organizacoes:
                        g_output.add((org_uri, RDF.type, RPC["Publishing_Organization"]))
                        g_output.add((org_uri, RDF.type, RPC["Organization"]))
                        organizacoes.add(org_uri)
                        print(f"\n     [org]: {pub_nome} -> {org_uri.split('#')[-1]}\n")
                    g_output.add((pub_uri, RPC["publisher"], org_uri))
            else:
                # Se não tem publisher, associa ao indivídual 'none' da ontologia
                none_uri = RPC["none"]
                g_output.add((pub_uri, RPC["publisher"], none_uri))
                print(f"     [pub] {pub_uri.split('#')[-1]} -> publisher: none (default)")
            
            # Ligar pessoa à publicação (ObjectProperty)
            g_output.add((pessoa_uri, RPC["author_inv"], pub_uri))
            
            total_publicacoes += 1
            
            # Mostra mais informação no log
            if classe_rpc == RPC["Article_in_Journal"] and journal_nome:
                print(f"     [pub] {pub_uri.split('#')[-1]} (journal: {journal_nome})")
            else:
                print(f"     [pub] {pub_uri.split('#')[-1]}")
        
        print(f"   [pass] Adicionadas {len(publicacoes)} publicações via rpc:author_inv")
    
    # Guardar OUTPUT
    g_output.serialize(destination=nome_ficheiro_output, format="pretty-xml")
    
    print("\n" + "="*70)
    print("ESTATÍSTICAS DO OUTPUT")
    print("="*70)
    print(f"[pass] Autores processados: {len(autores)}")
    print(f"[pass] Total de publicações: {total_publicacoes}")
    print(f"[pass] Organizações criadas: {len(organizacoes)}")
    print(f"[pass] Ficheiro guardado: {nome_ficheiro_output}")
    
    return g_output


# ==============================================================
# MAIN
# ==============================================================

def main():
    print("\n" + "="*70)
    print("FASE 2 - CONSTRUÇÃO DA ABox COM ONTOLOGIA RPC")
    print("="*70)

    
    # Criar INPUT
    limite_autores = 20
    criar_grafo_input("z01_meu_grafo_INPUT.rdf", limite_autores = limite_autores)

    # criar grafos
    criar_grafo_output_com_dblp(
        nome_ficheiro_input="z01_meu_grafo_INPUT.rdf",
        nome_ficheiro_output="z01_meu_grafo_OUTPUT.rdf"
    )
    
    print("\n" + "="*70)
    print("[pass] FASE 2 CONCLUÍDA")
    print("     criado: z01_meu_grafo_INPUT.rdf")
    print("     criado: z01_meu_grafo_OUTPUT.rdf")


if __name__ == "__main__":
    main()