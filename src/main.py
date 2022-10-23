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
# hand.instanciate_full_relation('MARRY',{'SUBJECT':'Will Smith','OBJECT': 'Ada Smith'})
# hand.create_relation_concept('IS_PET_OF',{'OWNER':'Person','PET':'Animal'})
# hand.create_object('Peter','Person')
# hand.create_property('Weight','float')
# hand.create_class('Dog',['Height','Weight'],'Animal')
# print(hand.get_relation('M'))
# print(hand.get_relation_concept('MARRY'))
print(hand.get_property_type('Heigh'))



hand.close()