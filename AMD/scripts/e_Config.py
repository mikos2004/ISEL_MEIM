# -*- coding: cp1252 -*-
# ===============================
# author: Paulo Trigo Silva (PTS)
# version: v06
# ===============================
# ALTERAÇÕES AO CÓDIGO POR:
# ---------------------------
# Tiago Alcobia - 50521
# Miguel Alcobia - 50746
# Fábio Pestana - 50756



#______________________________________________________________________________
# The modules to import
import os
import sys
from getopt import getopt, error
# The "getopt" module helps scripts to parse the command line arguments in sys.argv.
# It supports the same conventions as the Unix getopt() function
# (including the special meanings of arguments of the form �-� and �--�).




#______________________________________________________________________________
# A class that parses the command line argunmets
# In this example the system has 3 parameters (a, b, c)
# each parameter has a default value that can be redefined as a command line option
class e_Config():
   def __init__( self ):
      """
      Inicializa a configuração padrão.
      """
      # definition of default (option, value) pairs
      # i.e., the defualt values for the system parameters: a, b, c
      self.__optionValue = { \
         ("-f", "--file"): "./_datasets/lenses_3RowHeader.tab" }

  
   def config( self, argv ):
      """
      Analisa e processa os argumentos da linha de comandos.

      Args:
         argv: Lista de argumentos.

      Raises:
         Usage: Caso os argumentos não seguirem o formato esperado.
      """
      try:
         try:
            (argv_optionValue, args) = \
               getopt( argv[1:], \
                       "f:", \
                       ["file="] )
         except error: raise Usage( self.usage() )
      except Usage as incorrect:
         sys.stderr.write( incorrect.msg )
         sys.exit( 2 )
         
      list_optionName = self.__optionValue.keys()
      for (option, value) in argv_optionValue:
         for optionName in list_optionName:
            if option in optionName: self.__optionValue[ optionName ] = value


   def obterOpcaoValor( self ):
      """
      Retorna uma lista com os pares (opção, valor) configurados.

      Returns:
         Uma lista de tuplos (opção, valor).
      """

      resultado = {}
      for parOpcao in self.__optionValue.keys():
         resultado[ parOpcao[ 0 ] ] = self.__optionValue[ parOpcao ]
      return list( resultado.items() )  
      
    
   def get_file_path( self ):
      """
      Retorna o caminho configurado para o ficheiro do dataset.

      Returns:
         Caminho para o ficheiro do dataset.
      """
      for optionName in self.__optionValue.keys():
         return self.__optionValue[ optionName ]
   

   def usage( self ):
      """
      Retorna uma string com as intruções de utilização do programa.

      Returns:
         Mensagem formatada com as opções disponíveis (por padrão). 
      """

      thisFile = os.path.basename( sys.argv[0] )
      aStr = ""
      aStr += "\n"
      aStr += "\n" + "Usage:"
      aStr += "\n" +  "> " + thisFile + " -f dataset_file"
      aStr += "\n" +  "or"
      aStr += "\n" +  "> " + thisFile + " --file dataset_file"
      aStr += "\n"
      aStr += "\n" + "Default: ./_datasets/lenses_3RowHeader.tab"
      aStr += "\n"
      return aStr




#______________________________________________________________________________
# Utility Class
#(explores exceptions and decorators such as "getter" and "setter")
class Usage( Exception ):
   """
   Excepção utilizada para indicar erros de utilização.
   """

   def __init__( self, msg ):
      """
      Inicializa o objeto com uma mensagem de erro.

      Args:
          msg: Mensagem do erro.
      """
      self.msg = msg

   @property
   def msg( self ): return self.__msg

   @msg.setter
   def msg( self, value ):
      assert isinstance( value, str ), "PTS | msg: string expected"
      self.__msg = value
      
   @msg.deleter
   def msg( self ): self.__msg = ""




#______________________________________________________________________________
# The "main" of this module (is case this module is loaded from another module)
if __name__ == "__main__":
   e = e_Config()
   e.config( sys.argv )
   print( e.obterOpcaoValor() )
   





