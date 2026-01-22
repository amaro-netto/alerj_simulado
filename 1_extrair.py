import pdfplumber
import os
from pathlib import Path

# Configuração de Diretórios
PASTA_PDF = Path("pdf")
PASTA_TXT = Path("txt")

# Garante que a pasta de saída existe
PASTA_TXT.mkdir(exist_ok=True)

def pdf_para_txt(caminho_pdf):
    """Lê um PDF e retorna todo o texto cru."""
    texto_completo = []
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"   -> Lendo {len(pdf.pages)} páginas...")
            for page in pdf.pages:
                # layout=False é mais rápido e pega o fluxo de texto cru
                txt = page.extract_text(layout=False)
                if txt:
                    texto_completo.append(txt)
        return "\n".join(texto_completo)
    except Exception as e:
        print(f"   ❌ Erro ao ler {caminho_pdf.name}: {e}")
        return None

def main():
    print("🚀 INICIANDO EXTRAÇÃO EM LOTE (PDF -> TXT)...")
    
    arquivos_pdf = list(PASTA_PDF.glob("*.pdf"))
    
    if not arquivos_pdf:
        print("❌ Nenhum arquivo .pdf encontrado na pasta 'pdf/'.")
        return

    print(f"📂 Encontrados {len(arquivos_pdf)} arquivos para processar.\n")

    for arquivo in arquivos_pdf:
        print(f"📄 Processando: {arquivo.name}")
        
        texto_extraido = pdf_para_txt(arquivo)
        
        if texto_extraido:
            nome_txt = arquivo.stem + ".txt" # Mantém o mesmo nome, troca extensão
            caminho_saida = PASTA_TXT / nome_txt
            
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(texto_extraido)
            print(f"   ✅ Salvo em: {caminho_saida}\n")

    print("🏁 Extração concluída!")

if __name__ == "__main__":
    main()