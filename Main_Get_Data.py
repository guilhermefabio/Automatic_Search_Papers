from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
from itertools import islice
import matplotlib.pyplot as plt
import os
import numpy as np
import requests

def chunks(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]	

def Get_Raw_Data(URL):
	url = URL
	html = urlopen(url).read()
	soup = BeautifulSoup(html, features="html.parser")
	# DELETA TUDO QUE É ESTILO E SCRIPT DO HTML
	for script in soup(["script", "style"]):
		   script.extract()    #EXTRAI DADOS DO HTML
	text = soup.get_text()#BUSCA TEXTOS DA PAGINA
	lines = (line.strip() for line in text.splitlines()) #VERIFICAR PARA COMENTAR
	chunks = (phrase.strip() for line in lines for phrase in line.split("	"))#retira espaços em branco
	text = '"ENEGEP"'.join(chunk for chunk in chunks if chunk) #INSERE PALAVRA CONTROLE PARA CORTE 
	text = text.split('ENEGEP') # LISTA COM DADOS DE TEXTO DA PAGINA
	a_list = text
	return a_list, text

def Extract_Full_HTML_Page(textfile, a_list):
	for element in a_list:
		textfile.write(str(element) + '\n')
	textfile.close()

def Pre_Process_Data(text,ANOS):
	newdata =[]
	data = []
	y=0
	z=1000000
	
	for i in text:
		if i == '"Resultado da Pesquisa"':
			z=y+1
		if i == '"  ':
			data.append(newdata)
		if i.find('Página (Page) :')==True:
			break
		if y>z:
			newdata.append(i)
		y=y+1
	n=1

	newnewdata=[]
	for i in newdata:
		if i != '"AUTORES:"' and i !='"' and i!= ' ':
			newnewdata.append(i)

	#print(newnewdata)
	titulos = ['0', '1', '2', '3', '4', '5']

	for item in newnewdata:
		x = re.search('enegep', item)
		if x:
			newnewdata.remove(item)

	newnewdata=[newnewdata[i:i + n] for i in range(0, len(newdata), n)]

	newnewdata = [x[:x.index('"')] if '"' in x else x for x in newnewdata] #separa lista pelo item '"'
	newnewdata = [i for i in newnewdata if i] #limpar itens em branco

	data_set=[]
	for i in range(len(newnewdata)):
		nome = ' '.join([str(item) for item in newnewdata[i]])
		if re.search(str(ANOS[a]) + "_T",nome):  #REFERENCIA
			new_list =newnewdata[i:i+5]
			data_set.append(new_list)
	return data_set

#ELEMENTOS DE  BUSCA
#ANOS DA BUSCA
ANOS  = [2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021]
#LOOP DE BUSCAS
range_inicial = 57
df2 = pd.DataFrame()
df3 = pd.DataFrame()

for a in range(len(ANOS)):
	++a
	for key in range(range_inicial,363):
		URL = 'http://www.abepro.org.br/publicacoes/index.asp?pesq=ok&ano=' + str(ANOS[a]) + '&area=' + str(key) + '&pchave=&autor='
		a_list, text = Get_Raw_Data(URL)
		print("\n","Busca de dados da pagina" +  URL + "  Concluida.......")

		textfile = open(r"html_arquivos/dados_pagina"+"_"+str(key)+"_"+str(ANOS[a])+".txt", "w",encoding="utf-8")
		Extract_Full_HTML_Page(textfile,a_list)
		print("\n","HTML Extraido e Salvo.......")

		data_set= Pre_Process_Data(text,ANOS)
		print("\n","Pré processamento executado......")

		
		df = pd.DataFrame(data_set, columns=['ID','TITULO','AREA','AUTORES','PALAVRAS_CHAVE'])
		if len(df)>1:
			df2 = df2.append(df)
			r = requests.get(URL)
			df_list = pd.read_html(r.text) # this parses all the tables in webpages to a list
			df4 = df_list[2]
			df3 = df3.append(df_list[2])
		else:	
			if key-range_inicial>=11 and ANOS[a] != 2019:
				range_inicial = key
				break

print(df2)
print(df3)

df3.to_excel("excel_arquivos/autores_total.xlsx")
df2.to_excel("excel_arquivos/artigos_total.xlsx")
