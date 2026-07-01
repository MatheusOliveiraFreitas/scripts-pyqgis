from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry

# Camada de curvas
camada_entrada = QgsProject.instance().mapLayersByName('Curva_de_nivel_teste')[0]

cota_minima=1
coluna='cota'

# Criar uma Camada de saída (polígonos)
camada_saida = QgsVectorLayer("Polygon?crs=EPSG:4674", "POLIgono_curva", "memory")
prov_camada_saida = camada_saida.dataProvider()
nome_campo='pico_ou_depressao'

novo_campo = QgsField(nome_campo, QVariant.String)
#Adicionar as colunas da camada_entrada na Camada de saída

prov_camada_saida.addAttributes(camada_entrada.fields())

#camada_saida.updateFields()
prov_camada_saida.addAttributes([novo_campo])
camada_saida.updateFields()
idx_coluna = camada_saida.fields().lookupField(nome_campo)
#print(idx_coluna)
expressao = f'"{coluna}" >={cota_minima}'
# 1. Criar uma "requisição" (um pedido) com a sua expressão de filtro
request = QgsFeatureRequest().setFilterExpression(expressao)

# 2. Pedir as feições usando essa requisição
# 'features_filtradas' é um *iterador*, não uma lista. 
# O código ainda não "rodou" o loop.
features_filtradas = camada_entrada.getFeatures(request)
cont=0
conta=0
ele=[]
# Itera as feições ordenadas por cota da menor para maior, Se quiser extrair os picos colocar ,reverse=True no final
for feicao in sorted(features_filtradas, key=lambda f: f['cota'],reverse=True):
    #Extrair o valor das coluna cota
    a=0
    cota = feicao['cota']
    #Geometria da camada_entrada
    geom = feicao.geometry()
    #print(cota)

    # Trata o caso de linha única ou multilinha
    if geom.isMultipart():
        partes = geom.asMultiPolyline()
    else:
        partes = [geom.asPolyline()]

    for part in partes:
        # Verifica se a linha é fechada se o vertice 0 enconta no vertice -1
        if part[0] == part[-1]:
            #Gerar um poligono
            poly_geom = QgsGeometry.fromPolygonXY([part])

            # Verifica se intersecta algum polígono existente na camada de saída
            intersecta = False
            # Vai percorre as feições da camada de saida
            for f2 in camada_saida.getFeatures():
                #print(f2['cota'])
                #print('++++++')
                #print(cota)
                #Vai fazer uma intersseção entre as feições da camada de saida e poly_geom
                if poly_geom.intersects(f2.geometry()):                    
                    #Se a feição já esta na camada saida quer dizer que esse poligono não precisa adicionar
                    
                    if poly_geom.within(f2.geometry()):
                        if not poly_geom.equals(f2.geometry()):
                            #print('oi')
                            print(f2.id())
                            id=f2.id()
                            ele.append(id)
                            a=1
                            #Se a feição já esta na camada saida quer dizer que esse poligono não precisa adicionar
                    intersecta = True
                    break
            # Se não intersectar, adiciona na camada
            if not intersecta or a==1 :
                if a!=1:
                    
                    conta+=1
                    nova_feicao = QgsFeature()
                    novos_atributos = feicao.attributes()

                    # Adicione o novo valor de área no final da lista
                    novos_atributos.append('pico') 
                    nova_feicao.setGeometry(poly_geom)
                    nova_feicao.setAttributes(novos_atributos)
                    
                    prov_camada_saida.addFeature(nova_feicao)
                    
                    
                if a==1:
                    nova_feicao = QgsFeature()
                    novos_atributos = feicao.attributes()
                    novos_atributos.append('Depressao') 
                    nova_feicao.setGeometry(poly_geom)
                    nova_feicao.setAttributes(novos_atributos)
                    prov_camada_saida.addFeature(nova_feicao)                     
                    #print('depressao')

camada_saida.updateExtents()
camada_saida.startEditing()
camada_saida.deleteFeatures(ele)
camada_saida.commitChanges()
QgsProject.instance().addMapLayer(camada_saida)

print(conta)
