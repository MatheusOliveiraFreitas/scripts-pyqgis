from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
# Camada de curvas
camada_entrada = QgsProject.instance().mapLayersByName('Curva_de_nivel_teste')[0]

# se quer a costa das montanhas False se quiser e o Pico True
cota_minima=1
coluna='cota'

# Criar uma Camada de saída (polígonos)
camada_saida = QgsVectorLayer("Polygon?crs=EPSG:4674", "Extrair_Base", "memory")
prov_camada_saida = camada_saida.dataProvider()
#Adicionar as colunas da camada_entrada na Camada de saída
prov_camada_saida.addAttributes(camada_entrada.fields()) 
camada_saida.updateFields()

#Expressao para o filtro
expressao = f'"{coluna}" >={cota_minima}'
# 1. Criar uma "requisição" (um pedido) com a sua expressão de filtro
request = QgsFeatureRequest().setFilterExpression(expressao)

# 2. Pedir as feições usando essa requisição
features_filtradas = camada_entrada.getFeatures(request)

# Itera as feições ordenadas por cota da menor para maior, Se quiser extrair os picos colocar ,reverse=True no final
for feicao in sorted(features_filtradas, key=lambda f:f[coluna], reverse = False): 
    #Extrair o valor das coluna cota
    cota = feicao['cota']
    #Geometria da camada_entrada
    geom = feicao.geometry()
   

    # Trata o caso de linha única ou multilinha
    if geom.isMultipart():
        partes = geom.asMultiPolyline()
    else:
        partes = [geom.asPolyline()]

    for part in partes:
        # Verifica se a linha é fechada se o vertice 0 encontra no vértice -1
        if part[0] == part[-1]:
            #Gerar um poligono
            poly_geom = QgsGeometry.fromPolygonXY([part])

            # Verifica se intersecta algum polígono existente na camada de saída
            intersecta = False
            # Vai percorre as feições da camada de saida
            for f2 in camada_saida.getFeatures():

                #Vai fazer uma intersseção entre as feições da camada de saida e poly_geom
                if poly_geom.intersects(f2.geometry()):                    
                    #Se a feição já esta na camada saida quer dizer que esse poligono não precisa adicionar
                    intersecta = True
                    break
            tem_curva_interna_maior = False
            for f3 in camada_entrada.getFeatures():
                if f3[coluna] > cota and f3.geometry().within(poly_geom):
                    tem_curva_interna_maior = True
                    break
            # Se não intersectar, adiciona na camada
            if not intersecta and tem_curva_interna_maior:
                nova_feicao = QgsFeature()
                nova_feicao.setGeometry(poly_geom)
                nova_feicao.setAttributes(feicao.attributes())
                prov_camada_saida.addFeature(nova_feicao)

# Atualiza e adiciona a camada ao projeto
camada_saida.updateExtents()
QgsProject.instance().addMapLayer(camada_saida)
