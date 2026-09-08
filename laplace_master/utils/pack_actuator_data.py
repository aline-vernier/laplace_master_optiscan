


def pack_actuator_data(motor_names, motor_state):
    controls = {}

    for address, names in motor_names.items():
        state = motor_state[address]

        controls[address] = {
            "moving": state["moving"],
            "unit": state["unit"],
            "shot_number": state["shot_number"],
            "motors": [
                {
                    "name": name,
                    "position": position,
                    "shot_position": shot_position,
                }
                for name, position, shot_position
                in zip(names, state["positions"], state["shot_positions"])
            ],
        }

    return controls


if __name__ == "__main__":
    data =  {'positions': [0.0, 0.0], 'moving': False, 'unit': 'a.u.', 'shot_number': -1, 'shot_positions': [0.0, 0.0]}