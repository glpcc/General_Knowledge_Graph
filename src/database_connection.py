from neo4j import GraphDatabase
from neo4j import ManagedTransaction

class KGHandler():
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver = GraphDatabase.driver(uri,auth=(user,password))
    
    def close(self):
        self.driver.close()

    def instanciate_full_relation(self,relation_name: str, relation_related_objects_names: dict):
        with self.driver.session(database='knowledgegraph') as session:
            # Check if the relation class exists
            relation_exists = session.run('OPTIONAL MATCH (n:RelationConcept { name: $name }) RETURN n IS NOT NULL AS Predicate', name=relation_name).value()[0]
            if relation_exists:
                relationConcept_relations = session.run('MATCH (n:RelationConcept { name: $name })-[r]->(c) RETURN r',name=relation_name)
                relationConcept_relations = [i['r'].type for i in relationConcept_relations]
                # Check if all relations of the RelationConcept are in the related_relation_objects_names dict
                # TODO try to implement optional relations
                if all(i in relation_related_objects_names for i in relationConcept_relations):
                    # Check if the objects involved exists
                    objects_exits = session.run(f'MATCH (n:Object) WHERE n.name IN $names RETURN count(n) = $nameCount',
                        names = [relation_related_objects_names[i] for i in relationConcept_relations],
                        nameCount = len(relationConcept_relations)
                    ).value()[0]
                    if objects_exits:
                        # Check if objects are instances of the needed class
                        valid = True
                        for r in relationConcept_relations:
                            valid = session.run(f'Match (n:Object {{ name: $objectname }}),(r:RelationConcept {{ name: $relationConceptName }}),(r)-[:{r}]->(p),(n)-[:INSTANCE_OF]->(t) RETURN p.name = t.name OR exists((t)-[:SUBCLASS_OF*]->(p))', 
                            objectname = relation_related_objects_names[r],
                            relationConceptName = relation_name
                            ).value()[0]
                            if not valid:
                                print(f'Object with name {relation_related_objects_names[r]} is not an istance of a class or subclass needed')
                                break
                        if valid:
                            session.run('MATCH (r2:RelationConcept { name: $name }) CREATE (r:Relation { name: $name}),(r)-[:INSTANCE_OF]->(r2)',name=relation_name)
                            for r in relationConcept_relations:
                                session.run(f'MATCH (n:Object {{ name: $objectname}}),(r:Relation {{ name: $relationConceptName}}) CREATE (r)-[:{r}]->(n)',
                                    objectname = relation_related_objects_names[r],
                                    relationConceptName = relation_name,
                                )
                        else:
                            print('Some objects given are not of the specified class')
                    else:
                        print(f'Not all the objects given exists in the graph')
                else:
                    print(f'Not all relations of the RelationConcept where given, ther relations needed are {relationConcept_relations}')
            else:
                print(f'The Relation {relation_name} doesnt exist as a relation concept, try creating the relaton concept first')

    def create_relation_concept(self, relation_name: str, relation_related_concepts_names: dict):
        with self.driver.session(database='knowledgegraph') as session:
            # Check if the relation concept already exists
            relation_exists = session.run('OPTIONAL MATCH (n:RelationConcept { name: $name }) RETURN n IS NOT NULL AS Predicate', name=relation_name).value()[0]
            if not relation_exists:
                # Check if the concepts involved exists
                concepts_exits = session.run(f'MATCH (n:Concept) WHERE n.name IN $names RETURN count(n) = $nameCount',
                    names = [relation_related_concepts_names[i] for i in relation_related_concepts_names],
                    nameCount = len(relation_related_concepts_names)
                ).value()[0]
                if concepts_exits:
                    session.run('CREATE (r:RelationConcept:Concept { name:$name })',name=relation_name)
                    for i in relation_related_concepts_names:
                        session.run(f'MATCH (r:RelationConcept {{ name:$name }}),(c:Concept {{name:$conceptName}}) CREATE (r)-[:{i}]->(c)',
                            name=relation_name,
                            conceptName=relation_related_concepts_names[i]
                        )
                else:
                    print('Not all the Concepts given exists')
            else:
                print(f'The relation concept {relation_name} already exists')
  
    # TODO
    def create_object(self):
        ...

    # TODO
    def create_property(self):
        ...

    # TODO
    def create_class(self): ...

    # TODO
    def get_object(self,object_name: str):
        ...

    # TODO
    def get_relation(self): ...

    # TODO
    def get_relation_concept(self): ...

    # TODO
    def get_property(self): ...

    # TODO
    def get_class(self): ...

    # TODO
    def edit_property_value(self):
        ...
    
    # TODO 
    def remove_property(self): ...

    # TODO
    def remove_object(self): ...

    # TODO
    def remove_class(self): ...

    # TODO
    def remove_relation(self): ...

    # TODO
    def remove_relation_concept(self): ...


