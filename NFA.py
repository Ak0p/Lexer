from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ""


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        closure = set()
        stack = [state]

        while stack:
            current_state = stack.pop()
            closure.add(current_state)

            epsilon_transitions = self.d.get((current_state, EPSILON), set())
            for next_state in epsilon_transitions:
                if next_state not in closure:
                    stack.append(next_state)

        return frozenset(closure)

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        dfa_states = set()
        dfa_transitions = {}
        dfa_initial_state = self.epsilon_closure(self.q0)
        dfa_final_states = set()

        stack = [dfa_initial_state]
        dfa_states.add(dfa_initial_state)

        while stack:
            current_states = stack.pop()

            for symbol in self.S:
                next_states = set()

                for state in current_states:
                    transitions = self.d.get((state, symbol), set())
                    for transition_state in transitions:
                        next_states |= self.epsilon_closure(transition_state)

                next_states_frozen = frozenset(next_states)

                if next_states_frozen not in dfa_states:
                    stack.append(next_states_frozen)
                    dfa_states.add(next_states_frozen)

                dfa_transitions[(current_states, symbol)] = next_states_frozen

        for state in dfa_states:
            if any(nfa_state in self.F for nfa_state in state):
                dfa_final_states.add(state)

        return DFA(
            S=self.S,
            K=dfa_states,
            q0=dfa_initial_state,
            d=dfa_transitions,
            F=dfa_final_states,
        )

    def remap_states[
        OTHER_STATE
    ](self, f: Callable[[STATE], "OTHER_STATE"]) -> "NFA[OTHER_STATE]":
        remapped_states = {state: f(state) for state in self.K}
        return NFA(
            S=self.S,
            K=set(remapped_states.values()),
            q0=f(self.q0),
            d={
                (remapped_states[q], symbol): {remapped_states[p] for p in p_states}
                for (q, symbol), p_states in self.d.items()
            },
            F={remapped_states[state] for state in self.F},
        )


def unite_nfas(nfas: list[NFA[int]]) -> tuple[NFA[int], dict[int, int]]:
    # Create a new initial state for the united NFA
    # nfa_final_states_list = []
    ####

    nfa_final_states_dict = {}

    new_q0 = 0
    states = set()
    transitions = {}
    offset = 1
    final_states = set()
    states.add(new_q0)
    start_tr: tuple[int, str] = (new_q0, "")
    transitions[start_tr] = set()
    alphabet = set()

    i = 0

    for nfa in nfas:
        # print("nfas: ", nfa)
        
        alphabet = alphabet.union(nfa.S)
        remapped_nfa = nfa.remap_states(lambda state: state + offset)
        states = states.union(remapped_nfa.K)
        transitions[start_tr] |= {remapped_nfa.q0}
        transitions.update(remapped_nfa.d)
        offset += len(remapped_nfa.K)
        # print("before: ", final_states)
        final_states.update(remapped_nfa.F)

        # nfa_final_states_list.append(remapped_nfa.F)
        ####
        for state in remapped_nfa.F:
            nfa_final_states_dict[state] = i
        i += 1

    # print("\n")

    return NFA(
        S=alphabet,
        K=states,
        q0=new_q0,
        d=transitions,
        F=final_states,
        ), nfa_final_states_dict 
