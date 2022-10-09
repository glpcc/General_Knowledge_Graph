from operator import attrgetter
from typing import List, Tuple
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
    def _get_object_properties(tx: ManagedTransaction, object_name: str):
        # Gets the attributes of a SINGLE object
        query = f'MATCH (n1 {{name: "{object_name}"}}) RETURN n1'
        result = tx.run(query)
        return result.data()[0]['n1']
    
    @staticmethod
    def _get_object_classes(tx: ManagedTransaction, object_name: str):
        # Gets the lables of a SINGLE object
        query = f'MATCH (n1 {{name: "{object_name}"}})-[:SubClassOf*]->(b) RETURN b.name'
        result = tx.run(query)
        return result.value()

    @staticmethod
    def _get_object_labels(tx: ManagedTransaction, object_name: str):
        # Gets the lables of a SINGLE object
        query = f'MATCH (n1 {{name: "{object_name}"}}) RETURN labels(n1)'
        result = tx.run(query)
        return result.data()[0]['labels(n1)']

    def create_object(self, object_attributes:dict , labels:list = []):
        with self.driver.session(database='knowledgegraph') as session:
            session.execute_write(self._create_object,object_attributes,labels)

    def create_objects(self,objects: list[tuple[dict,list]]):
        # TODO Change to a single query later
        for attributes,labels in objects:
            self.create_object(attributes,labels)

    def instanciate_full_relation(self,relation_name: str, related_relation_objects_names: dict):
        with self.driver.session(database='knowledgegraph') as session:
            # Check if the relation class exists
            relation_exists = session.run('OPTIONAL MATCH (n:RelationConcept { name: $name }) RETURN n IS NOT NULL AS Predicate', name=relation_name).value()
            if relation_exists:
                relationConcept_relations = session.run('MATCH (n:RelationConcept { name: $name })-[r]->(c) RETURN r',name=relation_name)
                relationConcept_relations = [i['r'].type for i in relationConcept_relations]
                # Check if all relations of the RelationConcept are in the related_relation_objects_names dict
                # TODO try to implement optional relations
                if all(i in related_relation_objects_names for i in relationConcept_relations):
                    # Check if the objects involved exists
                    objects_exits = session.run(f'MATCH (n:Object) WHERE n.name IN $names RETURN count(n) = $nameCount',
                        names = [related_relation_objects_names[i] for i in relationConcept_relations],
                        nameCount = len(relationConcept_relations)
                    ).value()
                    if objects_exits:
                        session.run('MATCH (r2:RelationConcept { name: $name }) CREATE (r:Relation { name: $name}),(r)-[:INSTANCE_OF]->(r2)',name=relation_name)
                        for r in relationConcept_relations:
                            session.run(f'MATCH (n:Object {{ name: $objectname}}),(r:Relation {{ name: $relationConceptName}}) CREATE (n)-[:{r}]->(r)',
                                objectname = related_relation_objects_names[r],
                                relationConceptName = relation_name,
                            )
                    else:
                        print(f'Not all the objects given exists in the graph')
                else:
                    print(f'Not all relations of the RelationConcept where given, ther relations needed are {relationConcept_relations}')
            else:
                print(f'The Relation {relation_name} doesnt exist as a relation concept, try creating the relaton concept first')

    def create_relation_concept():
        ...

    def create_relation(self,from_name: str, to_name: str,relation_type: str, relation_attributes: dict):
        with self.driver.session(database='knowledgegraph') as session:
            session.execute_write(self._create_relation,from_name, to_name, relation_type, relation_attributes)
    
    def add_labels_to_object(self,object_name: str,labels: list = []):
        with self.driver.session(database='knowledgegraph') as session:
            session.execute_write(self._set_label,object_name,labels)
    
    def get_object(self,object_name: str):
        with self.driver.session(database='knowledgegraph') as session:
            properties = session.execute_read(self._get_object_properties,object_name)
            classes = session.execute_read(self._get_object_classes,object_name)
        obj = {
            "name": object_name,
            "properties": properties,
            "classes": classes
        }
        return obj
      


