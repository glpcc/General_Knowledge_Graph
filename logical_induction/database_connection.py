from neo4j import GraphDatabase
from neo4j import ManagedTransaction

class KGHandler():
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri,auth=(user,password))
    
    def close(self):
        self.driver.close()

    @staticmethod
    def _create_object(tx: ManagedTransaction,object_attributes: dict , labels: list = []):
        query = f'CREATE (n{":"*(len(labels)>0) + ":".join(labels)} $attrs)'
        tx.run(query,attrs = object_attributes)
    
    @staticmethod
    def _create_relation(tx: ManagedTransaction ,from_name: str, to_name: str,relation_type: str, relation_attributes: dict):
        query = f'MATCH (n1 {{name: "{from_name}"}}),(n2 {{name: "{to_name}"}}) CREATE (n1)-[r:{relation_type} $attrs]->(n2) '
        tx.run(query,attrs = relation_attributes)

    def create_object(self, object_attributes:dict , labels:list = []):
        with self.driver.session(database='objects') as session:
            session.write_transaction(self._create_object,object_attributes,labels)

    def create_relation(self,from_name: str, to_name: str,relation_type: str, relation_attributes: dict):
        with self.driver.session(database='objects') as session:
            session.write_transaction(self._create_relation,from_name, to_name, relation_type, relation_attributes)
    


hand = KGHandler('bolt://localhost:7687', 'neo4j', '')

hand.create_relation('test name', 'test_name','TEST_RELATION', {'test_attr':'tre'})

hand.close()
