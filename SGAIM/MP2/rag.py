# SGAIM - RAG pipeline
# author: Fábio Pestana     A50756
# author: Miguel Alcobia    A50746

import os
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
import requests
import json
import re

CORPUS_DIR = "corpus/"
# Diretoria para persistência da coleção ChromaDB
CHROMA_PERSIST_DIR = "./chroma_db"

OLLAMA_URL = "http://localhost:11434"


# SYSTEM_PROMPT = """You are a helpful assistant. Answer the user's question using ONLY the context provided below.
# If the context does not contain enough information, say "I don't have enough information to answer."
# Do not use your own knowledge. Be concise.
# Context:
# {context}"""

SYSTEM_PROMPT = """És um assistente que responde APENAS com base no contexto.

REGRAS:
1. Lê TODO o contexto com atenção.
2. Se a resposta estiver no contexto, indica a resposta, mesmo que seja preciso juntar informação de múltiplos chunks. Sê conciso.
3. Se não estiver, diz: "Não tenho informação suficiente para responder."
4. Não inventes nem adiciones informação.

Contexto:
{context}

Resposta:"""

# ---------------------------------------------
# ---------------- EXERCICIO 1 ----------------
# ---------------------------------------------

def load_corpus(directory):
    """
    Carrega todos os ficheiros .md do diretorio.

    Args:
        directory: Diretoria onde estão os ficheiros .md do corpus.

    Returns:
        Lista de dicionários, composto por "content" (texto do documento) e "source" (nome do ficheiro).
    """
    documents = []
    
    for filename in os.listdir(directory):
    
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), "r", encoding="utf‐8") as f:
                documents.append({
                    "content": f.read(),
                    "source": filename
                })
    
    return documents

def chunk_fixed_size(text, chunk_size=500, overlap=50):
    """
    Divide o texto em chunks de tamanho fixo com overlap.

    Args:
        text: Texto a ser dividido em chunks.
        chunk_size: Tamanho máximo de cada chunk. Valor padrão: 500 caracteres. 
        overlap: Número de caracteres que se sobrepõem entre chunks consecutivos. Valor padrão: 50 caracteres.

    Returns:
        Lista de chunks do texto fornecido.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ---------------------------------------------
# ---------------- EXERCICIO 2 ----------------
# ---------------------------------------------

def cosine_similarity(a, b):
    """
    Calcula a similaridade de cosseno entre dois vetores.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Encoder multilíngue (50+ línguas, inclui PT) — 384 dimensões.
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print(f"Modelo carregado. Dimensão: {model.get_embedding_dimension()}")

# ---------------------------------------------
# ---------------- EXERCICIO 4 ----------------
# ---------------------------------------------

def generate_with_context(query, retrieved_chunks, model_name = "qwen2.5:7b"):
    """
    Gerar resposta utilizando um modelo LLM com os chunks recuperados como contexto.
    O modelo deve estar instalado e o Ollama deve estar a correr.
    
    Args:
        query: Pergunta do utilizador.
        retrieved_chunks: Lista de chunks recuperados para a query.
        model_name: Nome do modelo LLM a ser utilizado. Valor padrão: "qwen2.5:7b".

    Returns:
        Resposta gerada pelo modelo LLM com base nos chunks.
    """
    context = "\n\n---\n\n".join(retrieved_chunks)
    
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
                {"role": "user", "content": query},
            ],
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]



def rag_query(query, collection, llm_model="qwen2.5:7b", k=5, save_chunks=False, query_index=0, chunking_type="fixed"): 
    """
    Pipeline RAG completo: query -> embed -> retrieve -> generate.

    Args:
        query: Pergunta do utilizador. 
        collection: Coleção ChromaDB onde os chunks estão indexados.
        llm_model: Nome do modelo LLM a ser utilizado. Valor padrão: "qwen2.5:7b".
        k: Número de chunks mais relevantes a recuperar. Valor padrão: 5.
        save_chunks: Se True, guarda-se os chunks e a resposta num ficheiro (.txt). Valor padrão: False.
        query_index: Índice da query, utilizado para o nome do ficheiro guardado. Valor padrão: 0.
        chunking_type: Nome da técnica de chunking a ser utilizada. Valor padrão: "fixed".

    Returns:
        Dicionário com a query, chunks recuperados, fontes e resposta gerada.
    """
    # 1. Embeder a query
    query_embedding = model.encode([query])[0]
    
    # 2. Recuperar os k chunks mais relevantes
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k
    )

    # 3. Gerar resposta com contexto
    retrieved_chunks = results["documents"][0]
    sources = results["metadatas"][0]
    answer = generate_with_context(query, retrieved_chunks, llm_model)
    
    if save_chunks:

        # Criar diretória se não existir
        chunks_dir = f"chunks_{chunking_type}"
        os.makedirs(chunks_dir, exist_ok=True)

        filename = os.path.join(chunks_dir, f"q{query_index}_chunks_{chunking_type}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"QUERY: {query}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"RESPOSTA DO MODELO:\n{answer}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"CHUNKS RECUPERADOS ({len(retrieved_chunks)} chunks):\n")
            f.write(f"{'='*80}\n\n")
            
            for i, (chunk, meta) in enumerate(zip(retrieved_chunks, sources)):
                f.write(f"\n--- CHUNK {i+1} ---\n")
                f.write(f"Fonte: {meta['source']}, chunk {meta['chunk_index']}\n")
                f.write(f"{'-'*40}\n")
                f.write(chunk)
                f.write(f"\n{'-'*40}\n")

        print(f" :. Chunks guardados em: {filename}")


    return {
        "query": query,
        "retrieved_chunks": retrieved_chunks,
        "sources": sources,
        "answer": answer
    }

# ---------------------------------------------
# ---------------- EXERCICIO 5 ----------------
# ---------------------------------------------

def chunk_by_sentences(text, max_chunk_size=500, overlap_sentences=1):
    """
    Divide o texto em chunks que respeitam as fronteiras de frases.

    Args:
        text: Texto a ser dividido em chunks.
        max_chunk_size: Tamanho máximo de cada chunk. Valor padrão: 500 caracteres. 
        overlap_sentences: Número de frases que se sobrepõem entre chuncks consecutivos. Valor padrão: 1 frase.

    Returns:
        Lista de chunks do texto fornecido.
    """

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        if current_size + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Overlap: manter as últimas N frases
            current_chunk = current_chunk[-overlap_sentences:]
            current_size = sum(len(s) for s in current_chunk)
        current_chunk.append(sentence)
        current_size += len(sentence)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def build_pipeline(chunking_strategy="fixed", chunk_size=500, overlap=50, recreate_collection=False, overlap_sentences=1):
    """
    Constrói o pipeline completo:
    - Carrega corpus
    - Cria/carrega uma coleção ChromaDB (persistente)
    - Divide em chunks
    - Gera embeddings

    Args:
        chunking_strategy: Nome da técnica de chunking a ser utilizada. Valor padrão: "fixed".
        chunk_size: Tamanho máximo de cada chunk. Valor padrão: 500 caracteres. 
        overlap: Número de caracteres que se sobrepõem entre chunks consecutivos. Valor padrão: 50 caracteres.
        recreate_collection: Se True, remove a coleção existente e cria uma nova. Valor padrão: False.
        overlap_sentences: Número de frases que se sobrepõem entre chuncks consecutivos. Valor padrão: 1 frase.

    Returns:
        docs: Lista de documentos carregados do corpus.
        all_chunks: Lista de todos os chunks segundo os docs.
        collection: Coleção ChromaDB onde os chunks estão indexados (pode ser None se 
            a coleção já existir e recreate_collection = False).
    """
    collection_name = f"corpus_mp2_{chunking_strategy}"

    # chroma_db/fixed ou chroma_db/sentences
    persist_dir = os.path.join(CHROMA_PERSIST_DIR, chunking_strategy) 

    client = chromadb.PersistentClient(path=persist_dir)

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": f"Documentos do CDRAM — chunking {chunking_strategy}"}
    )

    if collection.count() > 0 and not recreate_collection:

        # Coleção já indexada — reutilizar sem fazer collection.add
        print(f"[{chunking_strategy}] Coleção já existente com {collection.count()} chunks — a reutilizar.")
        print("(usa recreate_collection=True para re-indexar)")
        return None, None, collection

    # Primeira execucao ou recreate_collection=True -> indexar
    if recreate_collection and collection.count() > 0:
        client.delete_collection(name=collection_name)
        print(f"[{chunking_strategy}] Coleção anterior removida (recreate_collection=True).")
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Documentos do CDRAM — chunking {chunking_strategy}"}
        )

    
    # Carregar os docs
    docs = load_corpus(CORPUS_DIR)
    print(f"Carregados {len(docs)} documentos")

    for d in docs:
        print(f" {d['source']}: {len(d['content'])} caracteres")


    print(f"\nAplicando chunking ({chunking_strategy})...")

    all_chunks = []

    for doc in docs:
        if chunking_strategy == "fixed":
            chunks = chunk_fixed_size(doc["content"], chunk_size, overlap)
        elif chunking_strategy == "sentences":
            chunks = chunk_by_sentences(doc["content"], chunk_size, overlap_sentences)
        else:
            raise ValueError(f"Estrategia desconhecida: {chunking_strategy}")
          
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": doc["source"],
                "chunk_index": i
            })

    print(f"Total de chunks: {len(all_chunks)}")

    # Fazer embedding de todos os chunks de uma vez, mais eficiente
    embeddings = model.encode([c["text"] for c in all_chunks], show_progress_bar=True)
    print(f"Shape: {embeddings.shape}") # (n_chunks, 384)

    # Adicionar os chunks na coleção ChromaDB
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(all_chunks))],
        documents=[c["text"] for c in all_chunks],
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in all_chunks],
        embeddings=embeddings.tolist()
    )

    print(f"Coleção criada com {collection.count()} documentos")
    
    return docs, all_chunks, collection

def test_queries(collection, queries, save_chunks=True, chunking_type="fixed"):
    """
    Testa a pipeline RAG com um conjunto de queries.

    Args:
        collection: Coleção ChromaDB onde os documentos estão armazenados.
        queries: Lista de perguntas de teste (fáceis, médias e armadilhas).
        save_chunks: Se True, guarda-se para cada query os chunks e a sua resposta num ficheiro (.txt). Valor padrão: True.
        chunking_type: Nome da técnica de chunking a ser utilizada. Valor padrão: "fixed".
    """

    for i in range(len(queries)):
        print(f"----- Pergunta {i+1} -----")
        result = rag_query(queries[i], collection, save_chunks=save_chunks, query_index=i+1, chunking_type=chunking_type)
        print(f"Query: {result['query']}")
        print(f"\nFontes recuperadas:")
        for src in result["sources"]:
            print(f" - {src['source']}, chunk {src['chunk_index']}")
        print(f"\nResposta:\n{result['answer']}")
        print("-"*40 + "\n")


def embed_ollama(texts, model="nomic-embed-text"):
    """
    Função auxiliar para gerar embeddings usando um modelo de embedding do Ollama via API.
    O modelo deve estar instalado e o Ollama deve estar a correr.

    Args:
        texts: Lista de textos.
        model: Nome do modelo de embedding a ser utilizado. Valor padrão: "nomic-embed-text".

    Returns:
        Lista de vetores de embedding correspondentes aos textos fornecidos.
    """

    vectors = []
    for t in texts:
        r = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": t},
            timeout=30,
        )
        r.raise_for_status()
        vectors.append(r.json()["embedding"])
    return vectors



# --------------------------------------
# ---------------- Main ----------------
# --------------------------------------

def main():
    
    print("#"*40)
    print("RAG Pipeline - Aula 07")
    print("#"*40)
    
    queries_faceis = [
        # Queries Faceis - Resposta direta no texto
        
        # Capítulo 1
        "Como se chama a técnica de esgrima que Madalys ensina?",
        
        # Capítulo 2
        "Quantos anos tem Bellya?",
        
        # Capítulo 3: O Louco sem Rosto
        "O que é o Bloco de Gelo?",
        
        # Capítulo 4: Coração de Pai
        "Há quantos anos o filho de Singrek morreu?",
        
        # Capítulo 5: Companhia no Gelo
        "O que acontece a Nelguz durante a tortura?",
        
        # Capítulo 6: O Urso d'Ouro
        "Qual é o nome da estalagem onde o grupo pernoita?",
        
        # Capítulo 7: Uma Mão Amiga
        "Qual é o nome do falcão de Keyla?",
        
        # Capítulo 8: Família e Tradição
        "Qual é o símbolo da família Karkad?",
        
        # Capítulo 9: Ruf Dellitra
        "O que significa 'Ruf dellitra' em anão?",
        
        # Capítulo 10: Tudo Tem Um Fim
        "O que Ardicep faz ao pai após Elprid cair?",
    ]

    queries_medias = [
        # Queries Médias - Requerem sintese de diferentes partes do texto
        "Que tipos de sofrimento e privações Bellya enfrenta durante o seu cativeiro em Isidav?",
        "Que eventos levam à morte de Elprid no final da história?",
        "Qual a relação entre Singrek, a morte dos pais de Keyla e a formação da Resistência?",
        "Que lesões permanentes ou graves sofrem os membros do grupo (Bellya, Nelguz, Salok, Vetalis e Elprid) ao longo da narrativa?"
    ]

    queries_armadilhas = [
        # Queries Armadilhas - Nao tem resposta no contexto do corpus, verifica se o modelo
        # responde que não tem informação ou se alucina uma resposta.
        "Onde fica localizada a cidade de Alovuén?", 
        "Como se chama a esposa de Singrek?", 
        "Que relação familiar existe entre Gardiast e Vetalis?",
        "Onde nasceu Elprid Slival?"
    ]

    queries = queries_faceis + queries_medias + queries_armadilhas

    """    
    # Testar pipeline com fixed-size
    print("#"*40)
    print("\tChunking fixed-size")
    print("#"*40)
    
    docs, all_chunks, collection = build_pipeline("fixed", recreate_collection=False)
    
    test_queries(collection, queries, chunking_type="fixed")
    
    """

    print("#"*40)
    print("\tChunking por frases")
    print("#"*40)

    docs, all_chunks, collection = build_pipeline("sentences", recreate_collection=False)

    test_queries(collection, queries, chunking_type="sentences")

    print("#"*40)
    print("Fim do teste")
    print("#"*40)



if __name__ == "__main__":
    main()


