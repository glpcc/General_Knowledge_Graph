from neo4j import GraphDatabase
from neo4j import ManagedTransaction

class KGHandler():
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri,auth=(user,password))
    
    def close(self):
        self.driver.close()

    @staticmethod
    def _create_object(tx: ManagedTransaction, object_attributes: dict , labels: list = []):
        query = f'CREATE (n:{":".join(labels)} {{{",".join([f"{i}:${i}" for i in object_attributes])}}}'
        tx.run(query,object_attributes)

    def create_object(self, object_attributes:dict , labels:list = []):
        with self.driver.session(database='objects') as session:
            session.write_transaction(self._create_object, object_attributes,labels)