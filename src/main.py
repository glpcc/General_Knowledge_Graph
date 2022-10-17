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
# hand.create_relation_concept('IS_PET_OF',{'OWNER':'Person','PET':'Animal'})
# hand.create_object('Jorge Lope','Person')
# hand.create_property('Weight','float')
# hand.create_class('Dog',['Height','Weight'],'Animal')

print(hand.get_object('Will Smith'))

hand.close()