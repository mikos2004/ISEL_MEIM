# -*- coding: cp1252 -*-
# ===============================
# author: Paulo Trigo Silva (PTS)
# version: v10
# ===============================


#______________________________________________________________________________
# Importar modulos
from xml.dom import minidom


#_______________________________________________________________________________
# XML para prototipo sobre "minidom"
result = \
"""
<sparql xmlns="http://www.w3.org/2005/sparql-results#">
  <head>
    <variable name="s"/>
    <variable name="pub"/>
    <variable name="title"/>
  </head>
  <results distinct="true" ordered="false">
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-9135e6f93add2de9af9469d47bae893e</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch51</uri></binding>
      <binding name="title"><literal>A Demonstrably Consistent Mathematics - Part II.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-da859cac2cbc500a58c77b83fb83990f</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch81</uri></binding>
      <binding name="title"><literal>The Consistency of System Q.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-7b70f42b63413728b9d876fdc974ead7</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch84</uri></binding>
      <binding name="title"><literal>Correction to a Definition of Negation.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-927c298f70ec74ec82be0e6d2d1858e3</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch44</uri></binding>
      <binding name="title"><literal>Representations of Calculi.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-1e3107fb9e441b7eb55b1fa49e2e1b01</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch44a</uri></binding>
      <binding name="title"><literal>A Minimum Calculus for Logic.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-7d54ae13a8a12be6cd34a1fd8990547c</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch41</uri></binding>
      <binding name="title"><literal>Closure and Quine's *101.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-745c77ae4578abf7472ac70cc84ffbb7</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch80</uri></binding>
      <binding name="title"><literal>A Consistent Combinatory Logic with an Inverse to Equality.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-5babc787b17137fbb29fca51c80b4354</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch48</uri></binding>
      <binding name="title"><literal>Corrections to Two Papers on Modal Logic.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-ed031805254b704db945261b8c04c899</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch48a</uri></binding>
      <binding name="title"><literal>An Extension of Basic Logic.</literal></binding>
    </result>
    <result>
      <binding name="s"><uri>http://dblp.rkbexplorer.com/id/people-7462c358b5385b45c6cdbc1952bd2c48-19e66fb01e1a27f244db77d34d851e63</uri></binding>
      <binding name="pub"><uri>http://dblp.rkbexplorer.com/id/journals/jsyml/Fitch63</uri></binding>
      <binding name="title"><literal>The System C triangle of Combinatory Logic.</literal></binding>
    </result>
  </results>
</sparql>
"""

dom = minidom.parseString( str( result ) )
for node in dom.getElementsByTagName( 'binding'):
  name = node.getAttribute( "name" )
  if name == "title":
    for info in node.childNodes:
      print( info.firstChild.data )
      
      
      
      
      
