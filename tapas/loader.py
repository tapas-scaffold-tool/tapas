from pathlib import Path
from typing import Tuple, Optional, Callable

PARAMS_FUNCTION = "get_params"
POST_INIT_FUNCTION = "post_init"


def load_tapa(tapa_file_path: Path) -> Tuple[Optional[Callable], Optional[Callable]]:
    if not tapa_file_path.exists():
        return None, None

    scope = {}
    exec(tapa_file_path.read_text(encoding="utf-8"), scope)

    ask = scope.get(PARAMS_FUNCTION, None)
    post_init = scope.get(POST_INIT_FUNCTION, None)

    return ask, post_init
