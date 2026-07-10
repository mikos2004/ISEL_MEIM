# -*- coding: cp1252 -*-
#______________________________________________________________________________
# author: Paulo Trigo Silva (PTS)
# version: v06
# adaptado de: "c01_combinar_local_e_global_rkbexplorer.py" (cf., aula pratica6)
# contem agora as classes:
# - Grafo
# - GrafoRemoto
# gera ficheiros:
# - z01_meu_grafo_INPUT.rdf,
#   um exemplo de grafo
# - z01_meu_grafo_OUTPUT.rdf,
#   grafo anterior estendido por execucao de varias interrogacoers remotas
#______________________________________________________________________________
# Objectivo:
# construir uma interrogacao remota a partir de informacao local


#______________________________________________________________________________
# Importar modulos
import rdflib
from rdflib import ConjunctiveGraph, Graph
from rdflib  import Namespace
from rdflib import URIRef, Literal, BNode, Namespace, Variable
from rdflib import RDF

from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
from x_util_JSONwithMD import getResultSet, getResultSet_withMetaData
from xml.dom import minidom


#______________________________________________________________________________
# A nocao de Grafo (i.e., estrutura RDF, RDFS, OWL)
# - pode ser lido de ficheiro local
# - pode ser escrito em ficheiro local
# - pode ser estendido por adicao de tripletos
# - pode ser interrogado via SPARQL
class Grafo:
   def __init__( self ):
      self.grafo = Graph()

   def ler( self, nomeFicheiro, formato="xml" ):
      assert nomeFicheiro != "", "PTS | nomeFicheiro indefinido"
      grafo = Graph()
      try: grafo.parse( nomeFicheiro, format=formato )
      except: print( "\n >> ERRO: nao existe grafo em: %s <<\n" % nomeFicheiro )
      self.grafo = grafo
      return self

   def escrever( self, nomeFicheiro, formato="pretty-xml" ):
      assert nomeFicheiro != "" or self.grafo != None, "PTS | nomeFicheiro OU grafo INDEFINIDO"
      f = open( nomeFicheiro, "wb" )
      self.grafo.serialize( f, format=formato )

   def adicionarTripleto( self, sujeito, predicado, objecto ):
      assert self.grafo != None, "PTS | grafo INDEFINIDO"
      self.grafo.add( ( sujeito, predicado, objecto ) )

   def interrogar( self, interrogacao ):
      assert self.grafo != None, "PTS | grafo INDEFINIDO"
      return self.grafo.query( interrogacao )



#______________________________________________________________________________
# A nocao de Grafo Remoto (i.e., uma conexao a uma estrutura RDF, RDFS, OWL)
# - pode ser lido de URL remoto
# - pode ser interrogado via SPARQL
class GrafoRemoto:
   def __init__( self, URL ):
      self.conexao = SPARQLWrapper( URL )

   def interrogar( self, interrogacao, formato ):
      assert self.conexao != None, "PTS | grafo INDEFINIDO"
      q = self.conexao.setQuery( interrogacao )
      self.conexao.setReturnFormat( formato )
      resultado = self.conexao.query().convert()
      return resultado



#______________________________________________________________________________
# Utilitario: apresentar informacao
def apresentarCabecalho( texto ):
   print()
   print( len( texto )*"_" )
   print( texto )



#_______________________________________________________________________________
# Construir um grafo (exemplo)
# (numa versao posterior o grafo nao deve ficar aqui pre-definido)
# (i.e., o grafo que vier a construir nao deve ficar aqui "hard-coded")
def gerarTripletos( grafo, ns_FOAF ):
   s = BNode( "x" )
   
   p = rdflib.RDF.type
   o = ns_FOAF[ "Person" ]
   grafo.adicionarTripleto( s, p, o )

   p = ns_FOAF[ "name" ]
   o = Literal( "Edsger W. Dijkstra" )
   grafo.adicionarTripleto( s, p, o )

   s = BNode( "y" )
   
   p = rdflib.RDF.type
   o = ns_FOAF[ "Person" ]
   grafo.adicionarTripleto( s, p, o )
   
   p = ns_FOAF[ "name" ]
   o = Literal( "Frederic Brenton Fitch" )
   grafo.adicionarTripleto( s, p, o )


def gerarGrafoINPUT( nomeFicheiroGrafoINPUT, ns_FOAF ):
   g = Grafo()
   gerarTripletos( g, ns_FOAF )
   g.escrever( nomeFicheiroGrafoINPUT, formato="pretty-xml" )

  

#______________________________________________________________________________
# Um "main" com a estrutura geral deste exemplo
def main():
   # nomes usados ao longo do programa
   nomeFicheiroGrafoINPUT = "z01_meu_grafo_INPUT.rdf"
   nomeFicheiroGrafoOUTPUT = "z01_meu_grafo_OUTPUT.rdf"
   FOAF = Namespace( "http://xmlns.com/foaf/0.1/" )
   myNS = Namespace( "http://myNS/" )
   #URL = "http://dbpedia.org/sparql"
   #URL = "http://citeseer.rkbexplorer.com/sparql"
   URL = "http://dblp.rkbexplorer.com/sparql"

   # gerar e guardar um grafo (pode ser feito externamente a este programa)
   # (este grafo sera' posteriormente usado como INPUT para varias interrogacoes remotas)
   gerarGrafoINPUT( nomeFicheiroGrafoINPUT, FOAF )

   # interrogar um grafo local
   # (neste exemplo corresponde ao grafo acima gerado)
   grafoLocal = Grafo().ler( nomeFicheiroGrafoINPUT )
   interrogacaoLocal = \
     """
     PREFIX foaf: <""" + str( FOAF ) + """>
     SELECT ?s ?name
     WHERE
     {
     ?s foaf:name ?name .
     }
     """
   resultadoInterrogacaoLocal = grafoLocal.interrogar( interrogacaoLocal )
   apresentarCabecalho( "Resultado da Interrogacao ao Grafo Local" )
   for linha in resultadoInterrogacaoLocal: print( linha )
   print()

   # definir um grafo remoto
   grafoRemoto = GrafoRemoto( URL )
   # usar o resultado da interrogacao do grafo local
   # para construir interrogacoes a grafo(s) remoto(s)
   for ( grafoLocal_sujeito, grafoLocal_nomeCompleto ) in resultadoInterrogacaoLocal:
      interrogacaoRemota = \
        """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX akt: <http://www.aktors.org/ontology/portal#>
        SELECT DISTINCT *
        WHERE
        {
        ?s rdf:type akt:Person .
        ?s akt:full-name \"""" + str( grafoLocal_nomeCompleto ) + """\" .
        ?pub akt:has-author ?s .
        ?pub akt:has-title ?title .
        }
        LIMIT 10
        """
      apresentarCabecalho( "Interrogacao (SPARQL):" )
      print( interrogacaoRemota )
      print()

      # interrogar o grafo remoto
      formato = JSON
      resultadoInterrogacaoRemota = grafoRemoto.interrogar( interrogacaoRemota, formato )
      # aqui pode usar a funcao de "fallback" nos varios formatos que gonstruiu na aula pratica
      (metaDados, resultadoInterrogacaoRemota) = getResultSet_withMetaData( resultadoInterrogacaoRemota )

      apresentarCabecalho( "MetaDados:" )
      print( metaDados )
      apresentarCabecalho( "Resultado da Interrogacao ao Grafo Remoto (em " + formato + "):" )
      print( resultadoInterrogacaoRemota )

      # como o formato de resposta da interrogacao e' JSON
      # podemos usar a estrutura de MetaDados para aceder aos elementos
      apresentarCabecalho( "Resultado da Interrogacao ao Grafo Remoto (em Texto):" )
      print()
     
      idxTitle = metaDados.index( 'title' )
      for row in resultadoInterrogacaoRemota:
         title = row[ idxTitle ]
         print( title )
         # adicionar ao grafo local a informacao obtida nesta interrogacao remota
         #_______________________________________________________________________
         s = grafoLocal_sujeito
         p = myNS[ "temPublicacaoComTitulo" ]
         o = Literal( title )
         grafoLocal.adicionarTripleto( s, p, o )
         ##    g2.add( ( s, p, o ) )
         
      # actualizar o grafo local com a nova informacao  
      grafoLocal.escrever( nomeFicheiroGrafoOUTPUT, formato="pretty-xml" )
      #_______________________________________________________________________

         
##      No caso do resultado ser devolvido em XML pode usar o "minidom" como se segue:
##      dom = minidom.parseString( str( resultadoInterrogacaoRemota ) )
##      for node in dom.getElementsByTagName( 'binding'):
##         name = node.getAttribute( "name" )
##         if name == "title":
##            for item in node.childNodes:
##               title = item.firstChild.data
##               print( title )
##
##               # adicionar ao grafo local a informacao obtida nesta interrogacao remota
##               #_______________________________________________________________________
##               s = grafoLocal_sujeito
##               p = myNS[ "temPublicacaoComTitulo" ]
##               o = Literal( title )
##               grafoLocal.adicionarTripleto( s, p, o )


#______________________________________________________________________________
# O "main" deste modulo (caso o modulo nao seja carregado de outro modulo)
if __name__ == "__main__":
   main()

