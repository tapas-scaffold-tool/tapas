from rusty_results import Some, Empty

from tapas.params import IntParameter


def get_params():
    return [
        IntParameter(
            "param",
            validator=lambda x: Empty() if x > 0 else Some(f"Param must be greater than zero but was {x}")
        ),
    ]
