from .NFA import NFA
from dataclasses import dataclass
from typing import Tuple


class Regex:

    value: str
    children: list["Regex"]
    alphabet: set[str]

    def thompson(self) -> NFA[int]:
        raise NotImplementedError(
            "the thompson method of the Regex class should never be called"
        )

def print_tree(node: Regex, indent: int = 0):
    for child in node.children:
        print_tree(child, indent + 1)
    print("  " * indent + node.__class__.__name__)


def form_alphabet(regex: str) -> set[str]:
    metachars = {"*", "+", "?", "|", "(", ")", "[", "]"}

    alphabet = set("")
    for i, c in enumerate(regex):
        if c == "-":
            if i - 2 >= 0 and i + 2 < len(regex):
                if regex[i - 2] == "[" and regex[i + 2] == "]":
                    continue
        if c == "\\":
            alphabet.add(regex[i + 1])
        elif c == " ":
            continue
        elif c not in metachars:
            alphabet.add(c)
    return alphabet


@dataclass
class Alteration(Regex):
    def __init__(self):
        self.children = []

    def thompson(self) -> NFA[int]:
        offset = 1
        children_nfas = []
        for child in self.children:
            child_nfa = child.thompson()
            child_nfa = child_nfa.remap_states(lambda x: x + offset)
            children_nfas.append(child_nfa)
            offset += len(child_nfa.K)

        final_state = offset

        states = set()
        for child in children_nfas:
            states = states.union(child.K)
        states.add(0)
        states.add(final_state)
        d: dict[tuple[int, str], set[int]] = {}

        for child in children_nfas:
            for k, v in child.d.items():
                d[k] = v
        start_tr: tuple[int, str] = (0, "")
        d[start_tr] = set()
        for child in children_nfas:
            d[start_tr].add(child.q0)
            tr: tuple[int, str] = (child.F.pop(), "")
            d[tr] = {final_state}

        return NFA(children_nfas[0].S, states, 0, d, {final_state})


@dataclass
class Concat(Regex):
    def __init__(self, left: Regex, right: Regex):
        self.children = [left, right]
        self.value = "concat"

    def thompson(self) -> NFA[int]:
        left_nfa = self.children[0].thompson()
        half = len(left_nfa.K)
        right_nfa = self.children[1].thompson()
        right_nfa = right_nfa.remap_states(lambda x: x + half)
        states: set = left_nfa.K.union(right_nfa.K)
        d: dict[tuple[int, str], set[int]] = {}

        for k, v in left_nfa.d.items():
            d[k] = v
        for k, v in right_nfa.d.items():
            d[k] = v

        epsilon_transition: tuple[int, str] = (left_nfa.F.pop(), "")
        d[epsilon_transition] = {half}

        return NFA(right_nfa.S, states, left_nfa.q0, d, right_nfa.F)


@dataclass
class Kleene(Regex):
    def __init__(self):
        self.children = []

    def thompson(self) -> NFA[int]:
        offset = 1
        nfa = self.children[0].thompson()
        nfa = nfa.remap_states(lambda x: x + offset)
        offset += len(nfa.K)
        final_state = offset
        states: set = nfa.K
        states.add(0)
        states.add(final_state)
        d: dict[tuple[int, str], set[int]] = {}

        for k, v in nfa.d.items():
            d[k] = v

        # add the 4 epsilon transitions
        start_tr: tuple[int, str] = (0, "")
        d[start_tr] = {nfa.q0, final_state}
        final_tr: tuple[int, str] = (nfa.F.pop(), "")
        d[final_tr] = {final_state, nfa.q0}

        return NFA(nfa.S, states, 0, d, {final_state})


@dataclass
class Plus(Regex):
    def __init__(self):
        self.children = []

    def thompson(self) -> NFA[int]:
        offset = 1
        nfa = self.children[0].thompson()
        nfa = nfa.remap_states(lambda x: x + offset)
        offset += len(nfa.K)
        final_state = offset
        states: set = nfa.K

        states.add(0)
        states.add(final_state)
        d: dict[tuple[int, str], set[int]] = {}

        for k, v in nfa.d.items():
            d[k] = v

        start_tr: tuple[int, str] = (0, "")
        d[start_tr] = {nfa.q0}
        final_tr: tuple[int, str] = (nfa.F.pop(), "")
        d[final_tr] = {final_state, nfa.q0}

        return NFA(nfa.S, states, 0, d, {final_state})


@dataclass
class Question(Regex):
    def __init__(self):
        self.children = []

    def thompson(self) -> NFA[int]:
        offset = 1
        nfa = self.children[0].thompson()
        nfa = nfa.remap_states(lambda x: x + offset)
        offset += len(nfa.K)
        final_state = offset
        states: set = nfa.K
        states.add(0)
        states.add(final_state)
        d: dict[tuple[int, str], set[int]] = {}

        for k, v in nfa.d.items():
            d[k] = v
        # add the 5 epsilon transitions
        start_tr: tuple[int, str] = (0, "")
        d[start_tr] = {nfa.q0, final_state}
        final_tr: tuple[int, str] = (nfa.F.pop(), "")
        d[final_tr] = {final_state}

        return NFA(nfa.S, states, 0, d, {final_state})


@dataclass
class Category(Regex):
    def __init__(self, value: str, alphabet: set[str]):
        self.value = value
        self.children = []
        self.alphabet = alphabet

    def thompson(self) -> NFA:
        nfa: NFA = NFA(self.alphabet, {0, 1}, 0, {}, {1})
        if self.value == "eps":
            entry: tuple[int, str] = (0, "")
            nfa.d[entry] = {1}
        elif len(self.value) == 1:
            entry: tuple[int, str] = (0, self.value)
            nfa.d[entry] = {1}
        elif len(self.value) == 2:
            cat = self.expand_category(self.value)
            for c in cat:
                nfa.S.add(c)
                entry: tuple[int, str] = (0, c)
                nfa.d[entry] = {1}
        else:
            print("error invalid category")

        return nfa

    def expand_category(self, cat: str) -> set[str]:
        start = ord(cat[0])
        end = ord(cat[1])
        alphabet = set()
        for i in range(start, end + 1):
            alphabet.add(chr(i))
        return alphabet


def parse_regex(regex: str) -> Regex:
    alphabet = form_alphabet(regex)
    (expr, _) = parse_recursive(regex, 0, alphabet)
    expr.alphabet = alphabet

    return expr


def parse_recursive(regex: str, idx: int, alphabet: set[str]) -> Tuple[Regex, int]:
    escaped = False
    stack = []
    ret_idx = idx
    i = idx
    while i < len(regex):
        c = regex[i]
        if escaped:
            stack.append(Category(c, alphabet))
            escaped = False
            i += 1
            continue

        match c:
            case "e":
                if i + 2 < len(regex):
                    if regex[i + 1] == "p" and regex[i + 2] == "s":
                        stack.append(Category("eps", alphabet))
                        i += 2
                    else:
                        stack.append(Category("e", alphabet))
                else:
                    stack.append(Category("e", alphabet))
            case "*":
                stack.append(Kleene())
            case "+":
                stack.append(Plus())
            case "?":
                stack.append(Question())
            case "|":
                stack.append(Alteration())
            case ")":
                if idx == 0:
                    print("right parenthesis")
                else:
                    ret_idx = i
                    break
            case "]":
                print("]")
            case "(":
                (expr, new_idx) = parse_recursive(regex, i + 1, alphabet)
                stack.append(expr)
                i = new_idx
            case "[":
                if i + 4 < len(regex):
                    if regex[i + 2] == "-" and regex[i + 4] == "]":
                        stack.append(Category(regex[i + 1] + regex[i + 3], alphabet))
                        i += 4
            case "\\":
                escaped = True
            case " ":
                i += 1
                continue
            case _:
                stack.append(Category(c, alphabet))
        i += 1
    # pass the stack through the kleene, concat, and alter functions
    stack = kleene_stack(stack)
    stack = concat_stack(stack)
    stack = alter_stack(stack)

    return stack[0], ret_idx

# this function applies the kleene, plus, and question operators and returns a new stack
def kleene_stack(regexes: list[Regex]) -> list[Regex]:
    new_list = []
    i = 0
    while i < len(regexes):
        if isinstance(regexes[i], Kleene) and len(regexes[i].children) == 0:
            if isinstance(regexes[i - 1], Alteration) and len(regexes[i - 1].children) == 0:
                new_list.append(regexes[i])
                i+=1
                continue
            regexes[i].children.append(regexes[i - 1])
            expr = Kleene()
            expr.children = regexes[i].children
            if len(new_list) > 0:
                new_list.pop()
            new_list.append(expr)

        elif isinstance(regexes[i], Plus) and len(regexes[i].children) == 0:
            if isinstance(regexes[i - 1], Alteration) and len(regexes[i - 1].children) == 0:
                new_list.append(regexes[i])
                i+=1
                continue
            regexes[i].children.append(regexes[i - 1])
            expr = Plus()
            expr.children = regexes[i].children
            if len(new_list) > 0:
                new_list.pop()
            new_list.append(expr)

        elif isinstance(regexes[i], Question) and len(regexes[i].children) == 0:
            if isinstance(regexes[i - 1], Alteration) and len(regexes[i - 1].children) == 0:
                new_list.append(regexes[i])
                i+=1
                continue
            regexes[i].children.append(regexes[i - 1])
            expr = Question()
            expr.children = regexes[i].children
            if len(new_list) > 0:
                new_list.pop()
            new_list.append(expr)

        else:
            new_list.append(regexes[i])
        i += 1

    return new_list


# this function applies the concatenation operation on all elements and returns the new stack
def concat_stack(regexes: list[Regex]) -> list[Regex]:
    new_list = []
    i = 0
    while i < len(regexes):
        current_element = regexes[i]

        # Check if the current element is an alternation with no children
        if (
            isinstance(current_element, Alteration)
            and len(current_element.children) == 0
        ):
            new_list.append(current_element)
            i += 1
            continue

            # Check if I can concatenate to the previous element
        if len(new_list) > 0 and not (
            isinstance(new_list[-1], Alteration) and len(new_list[-1].children) == 0
        ):
            prev_el = new_list.pop()
            expr = Concat(prev_el, current_element)
            new_list.append(expr)
            i += 1
            continue

        if i + 1 < len(regexes):
            next_element = regexes[i + 1]

            if not isinstance(next_element, Alteration):
                expr = Concat(current_element, next_element)
                new_list.append(expr)
                i += 1
            else:
                new_list.append(current_element)
        else:
            new_list.append(current_element)
        i += 1

    return new_list


# this function applies the remaining operation of alternation
def alter_stack(regexes: list[Regex]) -> list[Regex]:
    i = 0

    if len(regexes) == 1:
        return regexes
    final_regex = Alteration()
    final_regex.children = []
    # for how many alternations there are form only one top level alternation
    while i < len(regexes):
        if not (isinstance(regexes[i], Alteration) and len(regexes[i].children) == 0):
            final_regex.children.append(regexes[i])
        i += 1

    return [final_regex]
