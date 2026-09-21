
from itertools import product


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



def make_position_queue(settings: dict) -> list[dict]:
    """
    Convert scan settings into a queue of motor positions.

    Parameters
    ----------
    settings : dict
        Dictionary of the form:
        {
            address: [
                [motor_name, {
                    'current': float,
                    'start': float,
                    'stop': float,
                    'step': float,
                    'rank': int,
                    'index': int
                }],
                ...
            ],
            ...
        }

    Returns
    -------
    list[dict]
        A list of dictionaries. Each dictionary contains one list of
        motor positions per address.

        Example:
        [
            {
                'address1': [x1, x2],
                'address2': [y1, y2]
            },
            {
                'address1': [x3, x4],
                'address2': [y3, y4]
            },
            ...
        ]
    """

    # Collect all scan dimensions.
    # Each dimension is identified by its rank.
    dimensions = []

    # Also determine how many motors each address has.
    address_motor_count = {}

    for address, motors in settings.items():

        if motors:
            address_motor_count[address] = max(
                motor_settings['index']
                for _, motor_settings in motors
            ) + 1
        else:
            address_motor_count[address] = 0

        for motor_name, motor_settings in motors:
            dimensions.append({
                'address': address,
                'name': motor_name,
                'index': motor_settings['index'],
                'start': motor_settings['start'],
                'stop': motor_settings['stop'],
                'step': motor_settings['step'],
                'rank': motor_settings['rank'],
            })

    # Sort by rank: rank 1 is the outermost loop.
    dimensions.sort(key=lambda d: d['rank'])

    # Generate values for each scan dimension.
    def generate_values(start, stop, step):
        values = []

        value = start

        if step > 0:
            while value <= stop:
                values.append(value)
                value += step

        elif step < 0:
            while value >= stop:
                values.append(value)
                value += step

        else:
            raise ValueError("Step cannot be zero")

        return values

    value_lists = [
        generate_values(
            dimension['start'],
            dimension['stop'],
            dimension['step']
        )
        for dimension in dimensions
    ]

    # product() changes the rightmost dimension fastest,
    # exactly like nested C loops:
    #
    # for rank1:
    #     for rank2:
    #         for rank3:
    #             ...
    combinations = product(*value_lists)

    queue = []

    for combination in combinations:

        # Start every address with None for every motor.
        positions = {
            address: [None] * count
            for address, count in address_motor_count.items()
        }

        # Insert the current value at the appropriate motor index.
        for dimension, value in zip(dimensions, combination):
            address = dimension['address']
            index = dimension['index']

            positions[address][index] = value

        queue.append(positions)

    return queue


if __name__ == "__main__":
    data =  {'positions': [0.0, 0.0], 'moving': False, 'unit': 'a.u.', 'shot_number': -1, 'shot_positions': [0.0, 0.0]}