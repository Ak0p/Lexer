from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        
        current_state = self.q0
        for char in word:
            transition_key = (current_state, char)
            if transition_key in self.d:
                current_state = self.d[transition_key]
            else:
                return False

        return current_state in self.F


    def accept_lex(self, word: str) -> tuple[bool, STATE]:
        
        current_state = self.q0
        for char in word:
            transition_key = (current_state, char)
            if transition_key in self.d:
                current_state = self.d[transition_key]
            else:
                return False, current_state

        return current_state in self.F, current_state

    def remap_states[
        OTHER_STATE
    ](self, f: Callable[[STATE], "OTHER_STATE"]) -> "DFA[OTHER_STATE]":
        
        pass

    def is_in_sink_state(self, state: STATE) -> bool:
        for symbol in self.S:
            if self.d.__contains__((state, symbol)):
                if self.d[(state, symbol)] != state:
                    return False
        if state in self.F:
            return False
        return True
    def has_sink_state(self) -> bool:
        for state in self.K:
            if self.is_in_sink_state(state):
                return True
        return False
    def step(self, state: STATE, symbol: str) -> STATE | None:
        if (state, symbol) in self.d:
            return self.d[(state, symbol)]
        else:
            return None

    def isAccepted(self, state: STATE) -> bool:
        return state in self.F
