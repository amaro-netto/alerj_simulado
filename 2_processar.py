import re
import json
import os
from pathlib import Path

# Configuração de Diretórios
PASTA_TXT = Path("txt")
PASTA_JSON = Path("json")

# Garante que a pasta de saída existe
PASTA_JSON.mkdir(exist_ok=True)

def limpar_linha(linha):
    """Remove sujeira comum (códigos, cabeçalhos)."""
    if re.match(r'^\d{8,}$', linha.strip()): return "" # IDs numéricos
    if "Acessar Lista" in linha or "ALERJ" in linha: return "" # Cabeçalhos
    return linha.strip()

def extrair_gabarito(texto_completo):
    """Busca a tabela de respostas no final do texto."""
    mapa = {}
    
    # Procura 'Respostas:' ou pega o final do arquivo
    match_inicio = re.search(r'Respostas:', texto_completo, re.IGNORECASE)
    if match_inicio:
        texto_fim = texto_completo[match_inicio.start():]
    else:
        texto_fim = texto_completo[-5000:] # Fallback

    # Padrão: Número + Letra (Ex: 1 B)
    matches = re.findall(r'(\d+)\s+([A-E])', texto_fim)
    for num, letra in matches:
        mapa[int(num)] = letra
    
    return mapa

def converter_txt_para_json(conteudo_txt):
    """Núcleo lógico: Transforma texto cru em lista de objetos."""
    
    # 1. Identifica Gabarito
    gabarito_map = extrair_gabarito(conteudo_txt)
    
    # 2. Isola o texto das questões (remove o gabarito do final)
    divisao = re.split(r'Respostas:', conteudo_txt, flags=re.IGNORECASE)
    texto_questoes = divisao[0] if divisao else conteudo_txt
    
    # 3. Quebra por 'Questão X'
    blocos = re.split(r'(Questão\s+\d+)', texto_questoes, flags=re.IGNORECASE)
    
    lista_questoes = []
    
    # Itera blocos (Cabeçalho + Texto)
    for i in range(1, len(blocos)-1, 2):
        cabecalho = blocos[i]
        corpo = blocos[i+1]
        
        # ID da Questão
        match_id = re.search(r'\d+', cabecalho)
        if not match_id: continue
        id_q = int(match_id.group())
        
        # Processamento Linha a Linha (para desembaralhar)
        enunciado_parts = []
        opcoes_map = {}
        
        for linha in corpo.split('\n'):
            linha = limpar_linha(linha)
            if not linha: continue
            
            # É alternativa? (Começa com A, B, C...)
            match_alt = re.match(r'^([A-E])[\s\.\)\-](.*)', linha)
            if match_alt:
                letra = match_alt.group(1)
                texto = match_alt.group(2).strip()
                opcoes_map[letra] = texto
            else:
                # É enunciado (se tiver tamanho relevante)
                if len(linha) > 2:
                    enunciado_parts.append(linha)
        
        # Montagem Final
        enunciado_final = " ".join(enunciado_parts)
        opcoes_ordenadas = []
        for letra in ['A', 'B', 'C', 'D', 'E']:
            # Se não achou a letra, deixa placeholder
            opcoes_ordenadas.append(opcoes_map.get(letra, ""))
            
        # Resposta Correta (Letra)
        resposta = gabarito_map.get(id_q) # Ex: "A" ou None
        
        lista_questoes.append({
            "id": id_q,
            "text": enunciado_final,
            "options": opcoes_ordenadas,
            "correct": resposta,
            "explanation": ""
        })
        
    return lista_questoes

def main():
    print("🚀 INICIANDO PROCESSAMENTO EM LOTE (TXT -> JSON)...")
    
    arquivos_txt = list(PASTA_TXT.glob("*.txt"))
    
    if not arquivos_txt:
        print("❌ Nenhum arquivo .txt encontrado. Rode o script 1_extrair.py primeiro.")
        return

    print(f"📂 Processando {len(arquivos_txt)} arquivos de texto.\n")

    for arquivo in arquivos_txt:
        print(f"⚙️  Convertendo: {arquivo.name}")
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            dados_json = converter_txt_para_json(conteudo)
            
            if dados_json:
                nome_json = arquivo.stem + ".json"
                caminho_saida = PASTA_JSON / nome_json
                
                with open(caminho_saida, 'w', encoding='utf-8') as f:
                    json.dump(dados_json, f, indent=2, ensure_ascii=False)
                
                print(f"   ✅ Gerou {len(dados_json)} questões -> {caminho_saida}")
            else:
                print("   ⚠️  Nenhuma questão identificada neste arquivo.")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar {arquivo.name}: {e}")

    print("\n🏁 Processamento Finalizado! Verifique a pasta 'json/'.")

if __name__ == "__main__":
    main()