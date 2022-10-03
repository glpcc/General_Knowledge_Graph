# Graph Model

## Node Categories

### Concepts

The concept nodes will be an abstraction to represent relations and knowledge that can be extrapolated to  objects. The different categories of concepts,that are represented by labels in the nodes, will be:

##### Classes

This will represent classes of objects and it's relations, like for example the class Person  will have a relation IS to the class Animal

##### Properties

This will represent object or concept properties and would help to make relations with other classes to, for example, ensure that some objects of some class have some specified properties, like length.

##### RelationConcept

This concept nodes will represent classes of relations and would help to ensure that only some classes can have some relations to others, to logicaly induce some relations from others,etc...

#### Objects

This category will represent all the objects, with its properties, and the relations with other objects and maybe, if needed with some concepts.

#### Relations

For maximum representation of knowledge, relations in this model will be nodes with the Relation label, one or more subjects of the relations,one or more objects of the relations and optionaly relation properties

#### Logical Nodes

This nodes will be used for complex logical relations between concepts and objects, and will be of the following types.

<details>
  <summary>AND,OR</summary>
  Nodes with two input relations as logical inputs and an output with
  the result of the logical operation
</details>

<details>
  <summary>IF</summary>
  Nodes with two input relations as logical inputs and an output with
  the result of the logical operation
</details>