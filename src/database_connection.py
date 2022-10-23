from neo4j import GraphDatabase
from neo4j import ManagedTransaction

class KGHandler():
    def __init__(self, uri: str, user: str, password: str) -> None:
        self.__driver = GraphDatabase.driver(uri,auth=(user,password))
    
    def run_query(self,query: str):
        # RUN AT YOUR OWN RISK NO COMPROBATIONS WILL BE MADE
        with self.__driver.session(database='knowledgegraph') as session:
            session.run(query)
            
    def close(self):
        self.__driver.close()

    def instanciate_full_relation(self,relation_name: str, relation_related_objects_names: dict):
        with self.__driver.session(database='knowledgegraph') as session:
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
                            relation_id = session.run('MATCH (r2:RelationConcept { name: $name }) CREATE (r:Relation { name: $name}),(r)-[:INSTANCE_OF]->(r2) RETURN id(r)',name=relation_name).value()[0]
                            for r in relationConcept_relations:
                                session.run(f'MATCH (n:Object {{ name: $objectname}}),(r:Relation {{ name: $relationConceptName}}) WHERE id(r)=$iden CREATE (r)-[:{r}]->(n)',
                                    objectname = relation_related_objects_names[r],
                                    relationConceptName = relation_name,
                                    iden = relation_id
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
        with self.__driver.session(database='knowledgegraph') as session:
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
  
    def create_object(self,object_name: str, object_class: str):
        # TODO add properties
        with self.__driver.session(database='knowledgegraph') as session:
            # Check if class exists
            class_exists = session.run('OPTIONAL MATCH (n:Class:Concept { name: $name }) RETURN n IS NOT NULL AS Predicate', name=object_class).value()[0]
            if class_exists:
                # TODO implement mandatory relations
                # Check if object alredy exists
                object_exists = session.run('OPTIONAL MATCH (n:Object { name: $name }),(c:Class:Concept { name: $className }) WHERE (n)-[:INSTANCE_OF]->(c) RETURN n IS NOT NULL AS Predicate',
                    name = object_name,
                    className = object_class
                ).value()[0]
                if not object_exists:
                    session.run('MATCH (n:Class:Concept { name: $className }) CREATE (o:Object { name: $objName}),(o)-[:INSTANCE_OF]->(n)',
                        className=object_class,
                        objName=object_name
                    )
                else:
                    print(f'The object with name {object_name} instance of {object_class} already exists')
            else:
                print(f'The class given {object_class} doesnt exists in the knowledge graph')

    def create_property(self,property_name: str ,value_type: str):
        with self.__driver.session(database='knowledgegraph') as session:
            # Check if property already exists
            property_exists = session.run('OPTIONAL MATCH (n:Concept:Property { name: $name }) RETURN n IS NOT NULL AS Predicate', name=property_name).value()[0]
            if not property_exists:
                # Check if type is valid
                # TODO add optional types and lists
                if value_type in ['str','int','float','bool']:
                    session.run('CREATE (o:Property:Concept { name: $propName,type: $propType})',
                        propType=value_type,
                        propName=property_name
                    )
                else:
                    print(f"Type given {value_type} is not in the valid types ['str','int','float','bool']")
            else:
                print(f'Property with name {property_name} already exists')
    
    def create_class(self,class_name: str,properties: list[str] ,subclass_of: str | None = None):
        with self.__driver.session(database='knowledgegraph') as session:
            # Check if class already exists
            class_exists = session.run('OPTIONAL MATCH (n:Concept:Class { name: $name }) RETURN n IS NOT NULL AS Predicate', name=class_name).value()[0]
            if not class_exists:
                # Check if properties given exists 
                properties_exists = session.run('MATCH (n:Concept:Property) WHERE n.name IN $properties RETURN count(n)=$numProps', 
                    properties=properties,
                    numProps=len(properties)
                ).value()[0]
                # TODO implement optional and obligatory properties
                if properties_exists:
                    if subclass_of is None:
                        session.run('CREATE (n:Concept:Class { name: $className })',
                            className=class_name
                        )
                        session.run('MATCH (p:Concept:Property),(n:Concept:Class { name: $className }) WHERE p.name IN $properties CREATE (n)-[:HAS_PROPERTY]->(p)',
                            className=class_name,
                            properties=properties
                        )
                    else:
                        # Check if parent class exists
                        parent_class_exists = session.run('OPTIONAL MATCH (n:Concept:Class { name: $name }) RETURN n IS NOT NULL AS Predicate', name=subclass_of).value()[0]
                        if parent_class_exists:
                            session.run('CREATE (n:Concept:Class { name: $className })',
                                className=class_name
                            )
                            session.run(
                                "MATCH (c:Concept:Class { name: 'Animal' }),(n:Concept:Class { name: 'Dog' })\
                                CREATE (n)-[:SUBCLASS_OF]->(c)\
                                WITH n\
                                MATCH (p:Concept:Property)\
                                WHERE p.name IN ['Height','Weight']\
                                CREATE (n)-[:HAS_PROPERTY]->(p)",
                                className=class_name,
                                properties=properties ,
                                parentName=subclass_of
                            )
                        else:
                            print(f'The parent class {subclass_of} doesnt exists in the graph')
                else:
                    print('Not all the properties given exist in the graph')
            else:
                print(f'Class with name {class_name} alredy exists')
    
    def get_object(self,object_name,get_superclasses: bool = True, get_relations: bool = True):
        response = {}
        with self.__driver.session(database='knowledgegraph') as session:
            # Name in this cases is consider to be a universal identifier (it will be changed to be named id later)
            obj = session.run('OPTIONAL MATCH (n:Object { name: $name}) RETURN n',name=object_name).value()[0]
            if obj is not None:
                response['labels'] = list(obj.labels)
                response['properties'] = obj._properties
                response['element_id'] = obj.element_id
                if get_superclasses:
                    super_classes = session.run('MATCH (n:Object { name: $name}),(n)-[:INSTANCE_OF]->(c:Class),(c)-[:SUBCLASS_OF*]->(d) RETURN collect(distinct c.name) + collect(d.name) as superclasses',name=object_name).value()
                    response['instance_of'] = super_classes[0][0]
                    response['super_classes'] = super_classes[0]
                if get_relations:
                    # relations = session.run("MATCH (n:Object { name: $name}) WITH n MATCH (r:Relation)-->(n) with n,r MATCH (r)-[d]->(c) WHERE not type(d)='INSTANCE_OF' RETURN distinct r.name,collect(type(d)),collect(c.name)",name=object_name).data()
                    relations = session.run("MATCH (n:Object { name: $name}) WITH n MATCH (r:Relation)-->(n) RETURN distinct r.name,id(r)",name=object_name).data()
                    response['relations'] = []
                    for relation in relations:
                        response['relations'].append(self.get_relation(relation['r.name'],relation['id(r)']))


                return response
            else:
                print('The object given doesnt exists')
                return response

    def get_relation(self,relation_name: str,relation_node_id: int = -1):
        # If relation Id is not given the function will return all the instances of that relation
        response = {}
        with self.__driver.session(database='knowledgegraph') as session:
            if relation_node_id < 0:
                # If id not given will return a list of the participants in all the instances of the relations
                relation_participants = session.run("MATCH (r:Relation { name: $name }),(r)-[d]->(n) WHERE NOT type(d)='INSTANCE_OF' RETURN id(r),type(d),n.name",name=relation_name).data()
                if len(relation_participants) == 0:
                    print('There Is no relation with that name')
                    return {relation_name:[]}
                response[relation_name] = []
                last_id = -1
                temp = {}
                print(relation_participants)
                for participant in relation_participants:
                    if last_id != participant['id(r)']:
                        if temp != {}:
                            response[relation_name].append(temp)
                        temp = {}
                    temp[participant['type(d)']] = participant['n.name']
                    last_id = participant['id(r)']
                response[relation_name].append(temp)
                return response
            else:
                # If id is given will return the dict with the relation participants
                relation_participants = session.run("MATCH (r:Relation { name:$name }),(r)-[d]->(n) WHERE NOT type(d)='INSTANCE_OF' AND id(r)=$iden RETURN id(r),type(d),n.name",
                    name=relation_name,
                    iden=relation_node_id
                ).data()
                if len(relation_participants) == 0:
                    print('There Is no relation with that name or id')
                    return {relation_name:{}}
                response[relation_name] = {}
                for participant in relation_participants:
                    response[relation_name][participant['type(d)']] = participant['n.name']
                return response

    def get_relation_concept(self,relation_concept_name: str):
        with self.__driver.session(database='knowledgegraph') as session:
            relation_concept = session.run("OPTIONAL MATCH (n:RelationConcept { name:$name }),(n)-[r]->(c) RETURN type(r),c",
                name=relation_concept_name
            ).data()
            if relation_concept[0]['type(r)'] is None:
                print('The relation Concept doesnt exist')
                return None
            return { relation_concept_name: {i['type(r)']:i['c']['name'] for i in relation_concept} }
            
    def get_property_type(self,property_concept_name: str):
        with self.__driver.session(database='knowledgegraph') as session:
            prop_type = session.run('MATCH (n:Property { name: $name }) RETURN n.type',name=property_concept_name).value()
            if len(prop_type) == 0:
                print(f'No property with name "{property_concept_name}"')
                return None
            return prop_type[0]
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


