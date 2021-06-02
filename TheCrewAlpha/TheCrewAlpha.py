from mlsolver.kripke import World, KripkeStructure
from mlsolver.formula import *
from mlsolver.formula import Atom, And, Not, Or, Box_a, Box_star

def add_symmetric_edges(relations):
    """Routine adds symmetric edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for r in agents_relations:
            x, y = r[1], r[0]
            result_agents.add((x, y))
        result[agent] = result_agents
    return result


def add_reflexive_edges(worlds, relations):
    """Routine adds reflexive edges to Kripke frame
    """
    result = {}
    for agent, agents_relations in relations.items():
        result_agents = agents_relations.copy()
        for world in worlds:
            result_agents.add((world.name, world.name))
            result[agent] = result_agents
    return result

def initialise_worlds(agents, deck):
	"""Generate the starting worlds of the Kripke model based on the agents and deck
	"""
	worlds = [
		World("012", {"a:0": True, "b:1": True, "c:2": True}),
    	World("021", {"a:0": True, "b:2": True, "c:1": True}),
    	World("102", {"a:1": True, "b:0": True, "c:2": True}),
    	World("120", {"a:1": True, "b:2": True, "c:0": True}),
    	World("201", {"a:2": True, "b:0": True, "c:1": True}),
    	World("210", {"a:2": True, "b:1": True, "c:0": True}),
	]
	return worlds

def initialise_relations(agents, deck, worlds):
	"""Generate the starting worlds of the Kripke model based on the starting worlds
	"""

	relations = {
		"a": {("012","021"),("102","120"),("201","210")},
		"b": {("102","201"),("012","210"),("021","120")},
    	"c": {("120","210"),("201","021"),("102","012")}
	}

	relations.update(add_reflexive_edges(worlds, relations))
	relations.update(add_symmetric_edges(relations))

	return relations

def initialise_kripke_model(agents, deck):
	"""Generates the starting kripke model based on the agents and deck used
	"""
	worlds = initialise_worlds(agents, deck)

	relations = initialise_relations(agents, deck, worlds)

	ks = KripkeStructure(worlds, relations)

	return ks

##### MAIN #####
agents = ["a","b","c"]

#Deck contains Blue(1,2), Red(3,4) and Trump(5,6) cards. For the alpha version we will try to keep the deck limited like this.
#	note: Initially considered using a list of strings but eventually decided to use integers as that will make it easier to automate certain things.
#	If unclear I might look into making them strings again later on.
deck = [
	1,2,
	3,4,
	5,6
]

ks = initialise_kripke_model(agents, deck)

print(ks)