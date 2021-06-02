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
	World("012", {"a:0": True, "b:1": True, "c:2": True}),
    World("021", {"a:0": True, "b:2": True, "c:1": True}),
    World("102", {"a:1": True, "b:0": True, "c:2": True}),
    World("120", {"a:1": True, "b:2": True, "c:0": True}),
    World("201", {"a:2": True, "b:0": True, "c:1": True}),
    World("210", {"a:2": True, "b:1": True, "c:0": True}),
]

relations = {
	"a": {("012","021"),("102","120"),("201","210")},
	"b": {("102","201"),("012","210"),("021","120")},
    "c": {("120","210"),("201","021"),("102","012")}
}

relations.update(add_reflexive_edges(worlds, relations))
relations.update(add_symmetric_edges(relations))

ks = KripkeStructure(worlds, relations)

ks = ks.solve(Not(Atom("a:1")))

Kba0 = Box_a("b",Atom("a:0"))
Kba1 = Box_a("b",Atom("a:1"))
Kba2 = Box_a("b",Atom("a:2"))

ks = ks.solve(Not(Or(Kba2, Or(Kba0, Kba1))))

print(ks)