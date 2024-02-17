from .Regex import Regex, parse_regex
from .DFA import DFA
from .NFA import NFA
from .NFA import unite_nfas


class Lexer:
    dfa: DFA[frozenset[int]]
    nfa_final_states_list: list[set[int]]
    sink_states: set[frozenset[int]]
    # dictionar care are cheie o stare finala de nfa si valoare indexul expresiei din spec (sau al nfa-ului asociat)
    nfa_final_states_dict: dict[int, int]
    spec: list[tuple[str, str]]

    def __init__(self, spec: list[tuple[str, str]]) -> None:

        spec_nfas: list[NFA[int]] = []
        for _, regex in spec:
            spec_nfas.append(parse_regex(regex).thompson())

        res = unite_nfas(spec_nfas)
        lexer_nfa: NFA[int] = res[0]
        nfa_final_states_dict: dict[int, int] = res[1]
        lexer_dfa = lexer_nfa.subset_construction()
        sink_states = set()
        for state in lexer_dfa.K:
            if lexer_dfa.is_in_sink_state(state):
                sink_states.add(state)

        self.dfa = lexer_dfa
        self.sink_states = sink_states
        self.spec = spec
        self.nfa_final_states_dict = nfa_final_states_dict

    def select_match(self, dfa_final_state: frozenset[int]) -> str | None:
        indeces = []
        for nfa_state in dfa_final_state:
            if nfa_state in self.nfa_final_states_dict:
                indeces.append(self.nfa_final_states_dict[nfa_state])

        if len(indeces) == 0:
            return None

        return self.spec[min(indeces)][0]

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        line = 0
        line_idx = 0
        start_index = 0
        end_index = 0
        in_sink_state = False
        curr_idx = 0
        tokens = []
        while start_index < len(word):
            in_sink_state = False
            curr_state: frozenset[int] = self.dfa.q0
            token = ""
            longest_accepted = 0
            last_final_state: frozenset[int] = self.dfa.q0
            while end_index < len(word):
                curr_idx = end_index
                end_index += 1
                token = word[start_index:end_index]

                new_state = self.dfa.step(curr_state, token[-1])
                if new_state in self.dfa.F:
                    longest_accepted = end_index - start_index
                    last_final_state = new_state
                    if token[-1] == "\n":
                        line += 1
                        line_idx = end_index
                elif self.dfa.is_in_sink_state(new_state):
                    end_index = start_index + longest_accepted
                    in_sink_state = True
                    break
                curr_state = new_state

            if in_sink_state and last_final_state == self.dfa.q0:
                token = ""
                match = f"No viable alternative at character {curr_idx - line_idx}, line {line}"
                tokens.clear()
                tokens.append((token, match))
                break

            elif not in_sink_state and last_final_state == self.dfa.q0:
                token = ""
                match = f"No viable alternative at character EOF, line {line}"
                tokens.clear()
                tokens.append((token, match))
                break
            else:
                token = word[start_index:end_index]
                match = self.select_match(last_final_state)
                tokens.append((match, token))

            start_index = end_index
            if start_index + 1 == len(word) and longest_accepted == 0:
                break
        return tokens
