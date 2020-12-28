from pathlib import Path
from typing import List, Union

import altair as alt
import altair_saver

from pedroai.io import safe_file


def save_chart(chart: alt.Chart, base_path: Union[Path, str], filetypes: List[str]):
    base_path = str(base_path)
    for t in filetypes:
        path = base_path + "." + t
        altair_saver.save(chart, safe_file(path))
