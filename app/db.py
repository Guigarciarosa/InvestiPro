from imports import *

class Database:
    def __init__(self) -> None:
        self.DB_PATH = os.path.join(os.path.dirname(__file__), '..', "db", "database.db")
        self.create_path = os.path.join(os.path.dirname(__file__), '..', "db", "scripts", "create")
        self.select_path = os.path.join(os.path.dirname(__file__), '..', "db", "scripts", "selects")

    def opensql(self, filepath, filename):
        with open(os.path.join(filepath, filename), encoding='utf-8') as file:
            return file.read()
        
    def init_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()

        cur.execute(self.opensql(self.create_path, "users.sql"))
        print('Tabela users criada com sucesso.')
        cur.execute(self.opensql(self.create_path, "carteira.sql"))
        print('Tabela carteira criada com sucesso.')
        cur.execute(self.opensql(self.create_path, "proventos.sql"))
        print('Tabela proventos criada com sucesso.')

        conn.commit()
        conn.close()

    def get_connection(self):
        """Retorna uma nova conexão (uso no login/cadastro)."""
        return sqlite3.connect(self.DB_PATH)
