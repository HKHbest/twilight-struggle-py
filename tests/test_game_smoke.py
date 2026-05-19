import random

import pytest

from game_mechanics import Game


class NullWriter:
    def write(self, _text):
        pass

    def flush(self):
        pass


def drive_random_game(seed: int, max_steps: int = 5000):
    rng = random.Random(seed)
    game = Game()
    history = []

    game.start()

    for step in range(max_steps):
        if game.terminated:
            return game, history

        if game.input_state is None:
            if not game.stage_list:
                raise AssertionError('game stopped without termination')
            game.stage_complete()
            continue

        if game.input_state.complete:
            if not game.stage_list:
                if game.terminated:
                    return game, history
                raise AssertionError('completed input stopped without termination')
            game.stage_complete()
            continue

        options = sorted(game.input_state.available_options, key=repr)
        if game.input_state.option_stop_early:
            options.append(game.input_state.option_stop_early)
        if not options:
            raise AssertionError(
                f'no options for prompt: {game.input_state.prompt}')

        rng.shuffle(options)
        for option in options:
            if game.input_state.recv(option):
                history.append(
                    (game.turn_track, game.ar_track,
                     game.input_state.side, game.input_state.state,
                     game.input_state.prompt, option)
                )
                break
        else:
            raise AssertionError(
                f'all options rejected for prompt: {game.input_state.prompt}')

    raise AssertionError(f'random game did not finish within {max_steps} steps')


@pytest.mark.parametrize('seed', range(5))
def test_random_game_smoke(seed, monkeypatch):
    monkeypatch.setattr('sys.stdout', NullWriter())
    game, history = drive_random_game(seed)

    assert game.terminated
    assert history
