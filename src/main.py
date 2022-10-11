from database_connection import KGHandler

hand = KGHandler('bolt://localhost:7687', 'neo4j', '123')

# objects = [
#     ({'name':'Person'},['Label','Concept']),
#     ({'name':'Animal'},['Label','Concept']),
#     ({'name':'Will Smith'},['Object','Person']),
#     ({'name':'Mammal'},['Label','Concept']),
#     ({'name':'BornIn'},['Property','Concept']),
#     ({'name':'Ada Smith'},['Object','Person']),
#     ({'name':'MARRIED_TO'},['RelationConcept','Concept']),
# ]
# result = hand.create_objects(objects)
# hand.instanciate_full_relation('MARRYE',{'SUBJECT':'Will Smith','OBJECT': 'Ada Smith'})
hand.create_relation_concept('IS_PET_OF',{'OWNER':'Person','PET':'Animal'})
hand.close()