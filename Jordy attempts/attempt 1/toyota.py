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


worlds = [
	World("1", {"toyota": True}),
	World("2", {"toyota": False})
]

relations = {
	"a": set(),
	"b": {("2","1")}
}

relations.update(add_reflexive_edges(worlds, relations))
relations.update(add_symmetric_edges(relations))

print(relations)

ks = KripkeStructure(worlds, relations)
print(ks)

model = ks.solve(Not(Box_a("b", Atom("toyota"))))

print(model)

model = ks.solve(Atom("toyota"))

print(model)