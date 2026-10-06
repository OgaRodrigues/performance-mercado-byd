import os
import re
import pdfplumber
import pandas as pd

# 1. Caminho da pasta
pasta_pdfs = r"C:\Users\Pichau\Desktop\Cursos Thiago\Power BI\BYD_2"
subpasta_destino = os.path.join(pasta_pdfs, "Processados_CSV")

if not os.path.exists(subpasta_destino):
    os.makedirs(subpasta_destino)

dados_consolidados = []
print("Processando os 20 arquivos com a nova máscara de texto...")

# 2. Varre os arquivos na pasta
for nome_arquivo in os.listdir(pasta_pdfs):
    if nome_arquivo.lower().endswith(".pdf"):
        caminho_completo = os.path.join(pasta_pdfs, nome_arquivo)
        
        # Extrai Ano e Mês do nome do arquivo
        partes_nome = nome_arquivo.split("_")
        if len(partes_nome) >= 2:
            ano = partes_nome[0]
            mes_num = partes_nome[1]
            mes_ano_texto = f"{mes_num}/{ano}"
        else:
            mes_ano_texto = "01/2025"

        with pdfplumber.open(caminho_completo) as pdf:
            if len(pdf.pages) >= 6:
                pagina = pdf.pages[5] # Página 6
                texto_pagina = pagina.extract_text()
                
                if texto_pagina:
                    linhas = texto_pagina.split("\n")
                    
                    for linha in linhas:
                        # EXPRESSÃO REGULAR PERFEITA:
                        # Captura: Ranking(1º) + Espaço + Modelo(Texto/Barras) + Espaço + Quantidade(Ponto/Números)
                        match = re.search(r"^\d+º\s+(.+?)\s+([\d.]+)\s+", linha.strip() + " ")
                        
                        if match:
                            modelo = match.group(1).strip()
                            qtd_str = match.group(2).strip()
                            
                            # Transforma a quantidade em número inteiro
                            qtd_limpa = qtd_str.replace(".", "")
                            try:
                                quantidade = int(qtd_limpa)
                                
                                # Garante que descartamos títulos residuais do PDF
                                if modelo.upper() not in ["MODELO", "TOTAL", "SUBTOTAL"]:
                                    dados_consolidados.append({
                                        "Modelo": modelo,
                                        "Quantidade": quantidade,
                                        "Data": mes_ano_texto
                                    })
                            except ValueError:
                                continue

# 3. Cria e salva o arquivo unificado
if dados_consolidados:
    df_final = pd.DataFrame(dados_consolidados)
    df_final = df_final[["Modelo", "Quantidade", "Data"]]
    
    caminho_salvamento = os.path.join(subpasta_destino, "dados_automoveis_consolidados.csv")
    df_final.to_csv(caminho_salvamento, index=False, sep=";", encoding="utf-8-sig")
    
    print("\n========================================================")
    print("✔ PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"Arquivo gerado em: {caminho_salvamento}")
    print(f"Total de linhas de Automóveis extraídas: {len(df_final)}")
    print("========================================================")
else:
    print("\nAviso: Nenhuma linha foi extraída. Verifique se o caractere mudou.")
