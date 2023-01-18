class GameStateManager:
    def __getattr__(self, attr):
        def func(*args, **kwargs):
            new_states = GameStates()
            for state in self:
                new_states |= getattr(state, attr)(*args, **kwargs)
            return new_states

        return func

    def safe_getattr(self, attr):
        if not all(hasattr(x, attr) for x in self):
            return self
        return getattr(self, attr)()

    def report(self):
        assert len(self) > 0
        if len(self) == 1:
            for state in self:
                return state.report()
        # If we have a ton of states but did not converge, let's take a
        # look at the longest one I guess? The most actions to evaluate.
        else:
            longest_notes = ""
            for state in self:
                if len(state.get_notes()) > longest_notes:
                    longest_notes = state.get_notes()
            return longest_notes + f"\nFailed to converge after {N_STATES} states"

    @property
    def performance(self):
        for state in self:
            return state.performance

    @property
    def done(self):
        for state in self:
            return state.done

    @property
    def hand(self):
        for state in self:
            return state.hand

    @property
    def notes(self):
        for state in self:
            return state.notes

    @property
    def overflowed(self):
        for state in self:
            return state.overflowed

    @property
    def turn(self):
        for state in self:
            return state.turn

    def next_turn(self, **kwargs):
        next_states = GameStates()
        for state in self:
            for _state in state.next_turn(**kwargs):
                if _state.overflowed:
                    return GameStates([_state])
                # As soon as we find a solution, bail.
                elif _state.done:
                    return GameStates([_state])
                else:
                    next_states.add(_state)
                # In the event of an overflow, bail. If we've got a solution,
                # report it. Otherwise, dump the longest state we have. That
                # might give us a sense for what's problematic.
                dt = time.time() - START_TIME
                if N_STATES > MAX_STATES or dt > MAX_SECONDS:
                    longest_state = max(next_states, key=len).overflow()
                    print("### OVERFLOW ###")
                    print(longest_state.report())
                    raise TooManyStates
        return next_states
