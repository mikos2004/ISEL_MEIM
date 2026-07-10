# ===============================
# FASE 3 - Interface Web com CherryPy
# ===============================
# Miguel Alcobia - 50746
# Fabio Pestana - 50756
# ===============================

import cherrypy
from rdflib import Graph, Namespace, URIRef, RDF, RDFS
import urllib.parse

# ===============================
# NAMESPACES E MAPEAMENTOS
# ===============================

DBLP = Namespace("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#")

# Lista de classes RDF que representam publicacoes (para identificar publicacoes no grafo)
CLASSES_PUBLICACAO = [
    DBLP.Publication,
    DBLP.Article_in_Journal,
    DBLP.Article_in_Proceedings,
    DBLP.Book,
    DBLP.Document,
    URIRef("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#Publication"),
    URIRef("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#Article_in_Journal"),
    URIRef("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#Article_in_Proceedings"),
    URIRef("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#Book"),
    URIRef("http://swat.cse.lehigh.edu/resources/onto/dblp.owl#Document")
]

# Mapeamento entre nomes internos (usados nas URIs) e nomes legiveis para apresentacao
TIPO_PUBLICACAO_NOMES = {
    "Article_in_Journal": "Article in Journal",
    "Article_in_Proceedings": "Article in Proceedings",
    "Book": "Book",
    "Publication": "Publication",
    "Document": "Document"
}


# ===============================
# FUNCOES DE ACESSO AO GRAFO
# ===============================

def carregar_grafo_local(ficheiro="export.rdf", formato="xml"):
    """
    Carrega o grafo RDF a partir de um ficheiro local.
    
    Args:
        ficheiro: Nome do ficheiro RDF (default: export.rdf)
        formato: Formato do ficheiro (default: xml)
    
    Returns:
        Graph: Objeto rdflib.Graph com os dados carregados, ou None em caso de erro
    """
    g = Graph()
    try:
        g.parse(ficheiro, format=formato)
        print(f"Grafo carregado: {len(g)} tripletos")
        return g
    except Exception as e:
        print(f"Erro ao carregar grafo: {e}")
        return None


def extrair_autores_publicacoes(grafo):
    """
    Extrai do grafo todos os autores e a lista de titulos das suas publicacoes.
    
    Args:
        grafo: Grafo RDF carregado
    
    Returns:
        dict: Dicionario onde cada chave e o nome do autor e o valor e outro dicionario
              com 'nome', 'uri' e lista de 'publicacoes' (titulos)
    """
    
    if grafo is None:
        print("Grafo nao carregado")
        return {}
    
    autores = {}
    
    # Identificar as publicacoes
    todas_publicacoes = set()
    for pub_class in CLASSES_PUBLICACAO:
        for pub in grafo.subjects(RDF.type, pub_class):
            todas_publicacoes.add(pub)
    
    print(f"Total de publicacoes identificadas: {len(todas_publicacoes)}")
    
    # Percorrer todas as pessoas (autores) no grafo
    for person in grafo.subjects(RDF.type, DBLP.Person):
        # Obter o nome do autor (prop DBLP.name)
        nome = None
        for name_obj in grafo.objects(person, DBLP.name):
            nome = str(name_obj).strip()
            break
        
        # Se nao houver nome, tenta extrair da propria URI
        if not nome:
            nome = str(person).split('#')[-1].replace('_', ' ')
            if nome == person:
                continue
        
        # Inicializa entrada do autor se ainda nao existir
        if nome not in autores:
            autores[nome] = {
                "nome": nome,
                "uri": str(person),
                "publicacoes": []
            }
        
        # Obtém publicacoes do autor com a propriedade author_inv
        publicacoes_autor = []
        for pub in grafo.objects(person, DBLP.author_inv):
            if pub in todas_publicacoes:  # Garante que e mesmo uma publicacao
                # Extrai titulo da publicacao
                titulo = None
                for title_obj in grafo.objects(pub, DBLP.title):
                    titulo = str(title_obj).strip()
                    break
                
                # Se nao houver titulo, tenta book_title
                if not titulo:
                    for book_title in grafo.objects(pub, DBLP.book_title):
                        titulo = str(book_title).strip()
                        break
                
                if titulo and titulo not in publicacoes_autor:
                    publicacoes_autor.append(titulo)
        
        autores[nome]["publicacoes"] = publicacoes_autor
    
    print(f"\nTotal de autores encontrados: {len(autores)}")
    
    return autores


def extrair_informacao_detalhada(grafo, autor_uri=None):
    """
    Extrai informacao detalhada sobre publicacoes, incluindo:
      - Titulo
      - Ano
      - Tipo (Article in Journal, Book, etc.)
      - Publishers (suporta multiplos)
      - Journal (para artigos de revista)
    
    Args:
        grafo: Grafo RDF carregado
        autor_uri: (Opcional) URI de um autor especifico. Se fornecido, apenas
                   as publicacoes desse autor sao retornadas.
    
    Returns:
        list: Lista de dicionarios, cada um representando uma publicacao
    """
    
    if grafo is None:
        return []
    
    # Identificar todas as publicacoes
    todas_publicacoes = set()
    for pub_class in CLASSES_PUBLICACAO:
        for pub in grafo.subjects(RDF.type, pub_class):
            todas_publicacoes.add(pub)
    
    # Se for para um autor especifico, filtra apenas as publicacoes dele
    if autor_uri:
        autor = URIRef(autor_uri)
        publicacoes_autor = set()
        for pub in grafo.objects(autor, DBLP.author_inv):
            if pub in todas_publicacoes:
                publicacoes_autor.add(pub)
        todas_publicacoes = publicacoes_autor
    
    # Processar cada publicacao
    publicacoes = []
    
    for pub in todas_publicacoes:
        pub_info = {
            "uri": str(pub),
            "titulo": "",
            "ano": "Ano desconhecido",
            "tipo": "Publicacao",
            "publishers": [],
            "journal": ""
        }
        
        # Titulo
        for title in grafo.objects(pub, DBLP.title):
            pub_info["titulo"] = str(title).strip()
            break
        
        # Se nao houver titulo, tentar book_title
        if not pub_info["titulo"]:
            for book_title in grafo.objects(pub, DBLP.book_title):
                pub_info["titulo"] = str(book_title).strip()
                break
        
        # Fallback: usar parte da URI como titulo
        if not pub_info["titulo"]:
            pub_info["titulo"] = str(pub).split('#')[-1].replace('_', ' ')
        
        # Ano
        for year in grafo.objects(pub, DBLP.year):
            try:
                ano_int = int(str(year))
                pub_info["ano"] = str(ano_int)
            except:
                pub_info["ano"] = str(year)
            break
        
        # Tipo especifico (subclasse de Publication)
        # Prioridade: Article_in_Journal > Article_in_Proceedings > Book > Publication > ...
        TIPOS_PRIORITARIOS = ["Article_in_Journal", "Article_in_Proceedings", "Book"]
        tipos_encontrados = []
        for tipo in grafo.objects(pub, RDF.type):
            tipo_str = str(tipo)
            if '#' in tipo_str:
                tipo_nome = tipo_str.split('#')[-1]
            else:
                tipo_nome = tipo_str.split('/')[-1]
            if tipo_nome in TIPO_PUBLICACAO_NOMES:
                tipos_encontrados.append(tipo_nome)

        # Escolher o tipo mais especifico pela ordem de prioridade
        tipo_escolhido = None
        for t in TIPOS_PRIORITARIOS:
            if t in tipos_encontrados:
                tipo_escolhido = t
                break
        if not tipo_escolhido:
            for t in tipos_encontrados:
                if t != "Publication":
                    tipo_escolhido = t
                    break
        if tipo_escolhido:
            pub_info["tipo"] = TIPO_PUBLICACAO_NOMES.get(tipo_escolhido, tipo_escolhido)
        
        # Journal
        for journal in grafo.objects(pub, DBLP.journal_name):
            pub_info["journal"] = str(journal)
            break
        
        # Publishers (suporta multiplos valores)
        for publisher in grafo.objects(pub, DBLP.publisher):
            pub_str = str(publisher)
            if '#' in pub_str:
                pub_name = pub_str.split('#')[-1]
            elif '/' in pub_str:
                pub_name = pub_str.split('/')[-1]
            else:
                pub_name = pub_str
            
            # Evitar adicionar "none"
            if pub_name not in pub_info["publishers"] and pub_name.lower() != "none":
                pub_info["publishers"].append(pub_name)
        
        publicacoes.append(pub_info)
    
    return publicacoes


# ===============================
# CLASSE PRINCIPAL (CHERRYPY)
# ===============================

class Main(object):
    """
    Classe principal da aplicacao web CherryPy.
    Contem os metodos expostos como rotas HTTP:
      - index: lista de autores
      - publicacoes: publicacoes de um autor especifico
      - todas_publicacoes: listagem completa de todas as publicacoes
    """
    
    def __init__(self, formato="html"):
        """
        Inicializa a aplicacao: carrega o grafo e extrai os autores.
        """
        self.formato = formato
        self.grafo = carregar_grafo_local("export.rdf")
        self.autores = extrair_autores_publicacoes(self.grafo)
    
    @cherrypy.expose
    def index(self):
        """
        Pagina principal.
        Mostra uma lista de todos os autores com links para as suas publicacoes.
        """
        
        html = f"""
        <html>
        <head>
            <title>Autores e Publicacoes - DBLP (Linked Data)</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .autor-lista {{ list-style-type: none; padding: 0; }}
                .autor-lista li {{ 
                    background: #e8f4f8; 
                    margin: 10px 0; 
                    padding: 15px; 
                    border-radius: 8px;
                    border-left: 5px solid #0088cc;
                }}
                .autor-lista li a {{
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #0088cc;
                    text-decoration: none;
                }}
                .autor-lista li a:hover {{ text-decoration: underline; }}
                .stats {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
                .header-info {{
                    background: #f0f0f0;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .nav-links a {{
                    margin-right: 15px;
                    color: #0088cc;
                }}
            </style>
        </head>
        <body>
            <h1>RPC - Trabalho Final</h1>
            
            <div class="header-info">
                <strong>Fonte de dados:</strong> export.rdf<br>
            </div>
            
            <div class="nav-links">
                <a href="/"> Autores</a>
                <a href="/todas_publicacoes"> Todas as Publicacoes</a>
            </div>
            <hr>            
            <h2> Autores no grafo</h2>
            <p><strong>Total de autores:</strong> {len(self.autores)}</p>
        """
        
        if self.autores:
            html += '<ul class="autor-lista">'
            for nome, info in sorted(self.autores.items()):
                nome_encoded = urllib.parse.quote(nome)
                num_pubs = len(info["publicacoes"])
                html += f"""
                <li>
                    <a href="/publicacoes?nome={nome_encoded}">{nome}</a>
                    <div class="stats">
                         {num_pubs} publicacoes
                    </div>
                </li>
                """
            html += '</ul>'
        else:
            html += '<p> Nenhum autor encontrado no grafo.</p>'
        
        html += """
        </body>
        </html>
        """
        return html
    
    @cherrypy.expose
    def publicacoes(self, nome=None):
        """
        Pagina que mostra as publicacoes de um autor especifico.
        
        Args:
            nome: Nome do autor (passado como parametro GET)
        """
        
        if not nome:
            return self.index()
        
        nome = urllib.parse.unquote(nome)
        
        if nome not in self.autores:
            html = f"""
            <html>
            <head><title>Autor nao encontrado</title></head>
            <body>
                <div class="nav-links">
                    <a href="/"> Autores</a>
                    <a href="/todas_publicacoes"> Todas as Publicacoes</a>
                </div>
                <h2> Autor nao encontrado: "{nome}"</h2>
                <p><a href="/"> Voltar</a></p>
            </body>
            </html>
            """
            return html
        
        autor = self.autores[nome]
        autor_uri = autor["uri"]
        
        publicacoes = extrair_informacao_detalhada(self.grafo, autor_uri)
        
        publicacoes_unicas = {}
        for pub in publicacoes:
            key = pub['titulo']
            if key not in publicacoes_unicas:
                publicacoes_unicas[key] = pub
        
        publicacoes_lista = list(publicacoes_unicas.values())
        
        def get_ano(pub):
            try:
                return int(pub['ano']) if pub['ano'] != "Ano desconhecido" else 0
            except:
                return 0
        
        publicacoes_lista.sort(key=get_ano, reverse=True)
        
        html = f"""
        <html>
        <head>
            <title>Publicacoes de {autor['nome']}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .pub-item {{ 
                    background: #f5f5f5; 
                    margin: 8px 0; 
                    padding: 12px; 
                    border-radius: 5px;
                    border-left: 4px solid #0088cc;
                }}
                .pub-titulo {{ font-weight: bold; }}
                .pub-info {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
                .nav-links a {{ margin-right: 15px; color: #0088cc; }}
                a {{ color: #0088cc; }}
            </style>
        </head>
        <body>
            <div class="nav-links">
                <a href="/"> Autores</a>
                <a href="/todas_publicacoes"> Todas as Publicacoes</a>
            </div>
            
            <h1> Publicacoes de {autor['nome']}</h1>
            
            <h2>Lista de publicacoes</h2>
        """
        
        if publicacoes_lista:
            for i, pub in enumerate(publicacoes_lista, 1):
                if pub['publishers']:
                    pubs_str = ", ".join(pub['publishers'])
                else:
                    pubs_str = "Unpublished"

                html += f"""
                <div class="pub-item">
                    <div class="pub-titulo">{i}. {pub['titulo']}</div>
                    <div class="pub-info">
                        Ano: <strong>{pub['ano']}</strong> | 
                        Tipo: <strong>{pub['tipo']}</strong> | 
                        Publisher(s): <strong>{pubs_str}</strong>
                    </div>
                </div>
                """
            html += f'<p><strong>Total:</strong> {len(publicacoes_lista)} publicacao(oes)</p>'
        else:
            html += "<p> Nenhuma publicacao encontrada.</p>"
        
        html += f"""
            <p><a href="/"> Voltar a lista de autores</a></p>
        </body>
        </html>
        """
        return html
    
    @cherrypy.expose
    def todas_publicacoes(self):
        """
        Pagina que mostra todas as publicacoes presentes no grafo (sem filtro por autor).
        """
        
        if not self.grafo:
            return "<h1>Erro: Grafo nao carregado</h1>"
        
        publicacoes = extrair_informacao_detalhada(self.grafo)
        
        publicacoes_unicas = {}
        for pub in publicacoes:
            key = pub['titulo']
            if key not in publicacoes_unicas:
                publicacoes_unicas[key] = pub
        
        publicacoes_lista = list(publicacoes_unicas.values())
        
        def get_ano(pub):
            try:
                return int(pub['ano']) if pub['ano'] != "Ano desconhecido" else 0
            except:
                return 0
        
        publicacoes_lista.sort(key=get_ano, reverse=True)
        
        html = f"""
        <html>
        <head>
            <title>Todas as Publicacoes - DBLP</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .pub-item {{ 
                    background: #f5f5f5; 
                    margin: 8px 0; 
                    padding: 12px; 
                    border-radius: 5px;
                    border-left: 4px solid #0088cc;
                }}
                .pub-titulo {{ font-weight: bold; }}
                .pub-info {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
                .nav-links a {{ margin-right: 15px; color: #0088cc; }}
            </style>
        </head>
        <body>
            <div class="nav-links">
                <a href="/"> Autores</a>
                <a href="/todas_publicacoes"> Todas as Publicacoes</a>
            </div>
            
            <h1> Todas as Publicacoes</h1>
            <p><strong>Total:</strong> {len(publicacoes_lista)} publicacoes</p>
        """
        
        for i, pub in enumerate(publicacoes_lista, 1):
            if pub['publishers']:
                pubs_str = ", ".join(pub['publishers'])
            else:
                pubs_str = "Unpublished"
            
            html += f"""
            <div class="pub-item">
                <div class="pub-titulo">{i}. {pub['titulo']}</div>
                <div class="pub-info">
                    Ano: <strong>{pub['ano']}</strong> | 
                    Tipo: <strong>{pub['tipo']}</strong> | 
                    Publisher(s): <strong>{pubs_str}</strong>
                </div>
            </div>
            """
        
        html += """
            <p><a href="/"> Voltar</a></p>
        </body>
        </html>
        """
        return html


# ===============================
# MAIN
# ===============================

if __name__ == '__main__':
    cherrypy_conf = {
        'global': {
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 8080,
        }
    }
    
    print("=" * 50)
    print("Iniciando servidor CherryPy...")
    print("Aceda em: http://127.0.0.1:8080")
    print("=" * 50)
    
    cherrypy.quickstart(Main(), config=cherrypy_conf)