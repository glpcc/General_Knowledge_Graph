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
    
    @staticmethod
    def _set_label(tx: ManagedTransaction, object_name: str, labels: list):
        query = f'MATCH (n1 {{name: "{object_name}"}}) SET n1{":"*(len(labels)>0) + ":".join(labels)}'
        tx.run(query)

    @staticmethod
    def _get_object_attributes(tx: ManagedTransaction, object_name: str):
        # Gets the attributes of a SINGLE object
        query = f'MATCH (n1 {{name: "{object_name}"}}) RETURN n1'
        result = tx.run(query)
        return result.data()[0]
    
    @staticmethod
    def _get_object_labels(tx: ManagedTransaction, object_name: str):
        # Gets the lables of a SINGLE object
        query = f'MATCH (n1 {{name: "{object_name}"}}) RETURN labels(n1)'
        result = tx.run(query)
        return result.data()[0]['labels(n1)']

    def create_object(self, object_attributes:dict , labels:list = []):
        with self.driver.session(database='objects') as session:
            session.execute_write(self._create_object,object_attributes,labels)

    def create_relation(self,from_name: str, to_name: str,relation_type: str, relation_attributes: dict):
        with self.driver.session(database='objects') as session:
            session.execute_write(self._create_relation,from_name, to_name, relation_type, relation_attributes)
    
    def create_label_relation(self,from_label_name: str, to_label_name: str,relation_type: str, relation_attributes: dict = {}):
        with self.driver.session(database='labels') as session:
            session.execute_write(self._create_relation,from_label_name, to_label_name, relation_type, relation_attributes)

    def create_label(self, object_attributes:dict , labels:list = []):
        with self.driver.session(database='labels') as session:
            session.execute_write(self._create_object,object_attributes,labels)
    
    def add_labels_to_object(self,object_name: str,labels: list = []):
        with self.driver.session(database='objects') as session:
            session.execute_write(self._set_label,object_name,labels)
    
    def get_object(self,object_name: str):
        with self.driver.session(database='objects') as session:
            attributes = session.execute_read(self._get_object_attributes,object_name)
            lables = session.execute_read(self._get_object_labels,object_name)
        return attributes, lables
      

hand = KGHandler('bolt://localhost:7687', 'neo4j', '123')

result = hand.get_object('test_name')
print(result)
hand.close()
