import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
import time


class EtlAcoes:
    """
    ETL completo para coletar:
    1. Ranking de ações via Investidor10 (requests + BeautifulSoup)
    2. Dados detalhados de cada ticker via Playwright (gráfico)
    3. Inserção no banco SQLite
    """

    def __init__(self):
        # URLs e headers
        self.base_url = "https://investidor10.com.br/acoes/rankings/maiores-valor-de-mercado/"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.page = 1
        self.all_data = []
        self.df = pd.DataFrame()

        # Banco de dados local
        self.engine = create_engine("sqlite:///../datawarehouse/datawarehouse.sqlite3")

    # =============================
    # 1️⃣ EXTRAÇÃO COM REQUESTS
    # =============================
    def extract_rank(self):
        """
        Extrai todas as páginas de ranking de ações.
        """
        print("Iniciando coleta de ranking...")
        while True:
            url = f"{self.base_url}?page={self.page}"
            print(f"Coletando página {self.page}...")

            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Erro ao acessar página {self.page}: {response.status_code}")
                break

            soup = BeautifulSoup(response.content, "html.parser")
            rows = soup.find_all("tr")

            page_data = []
            for row in rows:
                ticker_span = row.find(
                    "span",
                    class_="font-semibold text-[#14171F] group-hover:text-[#485063]",
                )
                if not ticker_span:
                    continue

                info = {
                    "ticker": ticker_span.get_text(strip=True),
                    "url": f"https://investidor10.com.br/acoes/{ticker_span.get_text(strip=True).lower()}/"
                }

                for td in row.find_all("td", class_="sorting"):
                    nome = td.get("data-name")
                    if nome:
                        valor = td.get_text(strip=True)
                        info[nome] = valor

                page_data.append(info)

            if not page_data:
                print("Paginação finalizada.")
                break

            self.all_data.extend(page_data)
            self.page += 1

        self.df = pd.DataFrame(self.all_data)
        print(f"✅ Total de registros coletados: {len(self.df)}")
        return self.df

    # =============================
    # 2️⃣ EXTRAÇÃO COM PLAYWRIGHT
    # =============================
    def extract_details(self, ticker_urls):
        """
        Usa Playwright (síncrono) para acessar cada ticker e coletar os dados do gráfico.
        """
        detailed_data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for ticker, url in ticker_urls.items():
                try:
                    print(f"🔍 Coletando detalhes de {ticker}...")
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    time.sleep(3)  # pequeno delay para garantir carregamento do gráfico

                    soup = BeautifulSoup(page.content(), "html.parser")
                    items = soup.find_all("div", class_="legend-details")

                    if not items:
                        print(f"⚠️ Nenhum dado de gráfico encontrado para {ticker}")
                        continue

                    for item in items:
                        nome = item.find("p", class_="legend-name").text.strip()
                        receita = item.find("p", class_="legend-revenue").text.strip()

                        detailed_data.append({
                            "ticker": ticker,
                            "nome": nome.text.strip() if nome else None,
                            "receita": receita.text.strip() if receita else None
                        })

                except Exception as e:
                    print(f"⚠️ Erro ao coletar {ticker}: {e}")
                    continue

            browser.close()

        print(f"✅ Coleta de detalhes finalizada ({len(detailed_data)} registros).")
        return pd.DataFrame(detailed_data)

    # =============================
    # 3️⃣ TRATAMENTO DE DADOS
    # =============================
    def clean(self, df):
        """
        Realiza limpeza de colunas monetárias e percentuais.
        """

        def convert_br_number(series: pd.Series) -> pd.Series:
            return (
                series.astype(str)
                .str.replace('%', '', regex=False)
                .str.replace('R$', '', regex=False)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.replace('-', '0', regex=False)
            )

        numeric_cols = ['p_l', 'p_vp', 'current_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = convert_br_number(df[col])

        return df

    # =============================
    # 4️⃣ CARGA NO BANCO
    # =============================
    def load(self, df, table_name="acoes_indicadores"):
        """
        Carrega DataFrame no banco SQLite.
        """
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)
        print(f"💾 Tabela '{table_name}' atualizada com sucesso ({len(df)} registros).")

    # =============================
    # 5️⃣ EXECUÇÃO COMPLETA
    # =============================
    def run(self, limit=None):
        """
        Executa o pipeline completo.
        """
        df_rank = self.extract_rank()

        if limit:
            df_rank = df_rank.head(limit)
            print(f"Executando em modo de teste com {limit} tickers")

        ticker_urls = {row["ticker"]: row["url"] for _, row in df_rank.iterrows()}
        df_details = self.extract_details(ticker_urls)

        if df_details.empty:
            print("⚠️ Nenhum detalhe coletado, pulando merge.")
            df_final = df_rank
        else:
            df_final = df_rank.merge(df_details, on="ticker", how="left")

        df_final = self.clean(df_final)
        self.load(df_final)
        return df_final


# =============================
# EXECUÇÃO DO SCRIPT
# =============================
if __name__ == "__main__":
    etl = EtlAcoes()
    df_final = etl.run(limit=5)
    print(df_final.head())
