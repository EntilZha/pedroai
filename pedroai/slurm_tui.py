from pathlib import Path
import subprocess
import os

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    LoadingIndicator,
    DataTable,
    TextLog,
    TabbedContent,
    TabPane,
    Button,
    Label,
)


# SQUEUE = "squeue --me --format='%.18i %.9P %.30j %.8T %.10M %.9l %.6D %R'"
SQUEUE = "squeue --me --Format='JobID:|,ArrayJobID:|,ArrayTaskID:|,Partition:|,Name:|,State:|,TimeUsed:|,NumNodes:|,Nodelist:|,STDOUT:|,STDERR:'"
FIELDS = [
    "job_id",
    "array_job_id",
    "array_task_id",
    "partition",
    "name",
    "state",
    "time_used",
    "num_nodes",
    "nodelist",
    "stdout",
    "stderr",
]
DISPLAY_FIELDS = FIELDS[:-2]


def run_squeue(cached: bool = False):
    if cached:
        with open("/private/home/par/slurm_tui.txt") as f:
            lines = f.read().strip().split("\n")
    else:
        proc = subprocess.run(
            SQUEUE, shell=True, capture_output=True, check=True, text=True
        )
        lines = proc.stdout.strip().split("\n")
    table_rows = []
    for idx, l in enumerate(lines):
        if idx == 0:
            continue
        fields = l.strip().split("|")
        if len(fields) != len(FIELDS):
            raise ValueError(
                f"Unequal number of fields: {len(fields)} versus {len(FIELDS)}"
            )
        row = {}
        for i in range(len(fields)):
            curr_field = FIELDS[i]
            value = fields[i]
            row[curr_field] = value

        if "%A" in row["stdout"]:
            row["stdout"] = {
                0: row["stdout"]
                .replace("%A", row["array_job_id"])
                .replace("%a", row["array_task_id"])
            }
            row["stderr"] = {
                0: row["stderr"]
                .replace("%A", row["array_job_id"])
                .replace("%a", row["array_task_id"])
            }
        elif "%n" in row["stdout"]:
            stdout_entries = {}
            stderr_entries = {}
            for node_id in range(int(row["num_nodes"])):
                stdout_entries[node_id] = (
                    row["stdout"]
                    .replace("%j", row["job_id"])
                    .replace("%n", str(node_id))
                )
                stderr_entries[node_id] = (
                    row["stderr"]
                    .replace("%j", row["job_id"])
                    .replace("%n", str(node_id))
                )
            row["stdout"] = stdout_entries
            row["stderr"] = stderr_entries
        elif "%j" in row["stdout"]:
            row["stdout"] = {0: row["stdout"].replace("%j", row["job_id"])}
            row["stderr"] = {0: row["stderr"].replace("%j", row["job_id"])}
        table_rows.append(row)
    lookup_table = {(r["array_job_id"], r["array_task_id"]): r for r in table_rows}
    return table_rows, lookup_table


def read_file(path: Path):
    with open(path) as f:
        return f.readlines()


class SlurmDashboardApp(App):
    BINDINGS = [
        ("r", "refresh_slurm", "Refresh Slurm"),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = "slurm_tui_styles/style.css"

    def _update_slurm(self):
        self.squeue_rows, self.squeue_lookup = run_squeue()
        table = self.query_one(DataTable)
        table.clear()
        for (job_id, task_id), row in self.squeue_lookup.items():
            cells = [row[f] for f in DISPLAY_FIELDS]
            table.add_row(*cells, key=f"{job_id}_{task_id}")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*DISPLAY_FIELDS)
        table.cursor_type = "row"
        self.selected_node = 0
        self.num_nodes = 1
        self.entry = None
        self._update_slurm()
        self.query_one("#stdout").write(
            "No Log File Selected", width=os.get_terminal_size().columns - 2
        )
        self.query_one("#stderr").write(
            "No Log File Selected", width=os.get_terminal_size().columns - 2
        )
        self.query_one("#loading").add_class("hidden")
        self.query_one("#stdout_filename").update("No Job Selected")
        self.query_one("#stderr_filename").update("No Job Selected")

    def _update_log_outputs(self):
        stdout_file = self.entry["stdout"][self.selected_node]
        stderr_file = self.entry["stderr"][self.selected_node]
        self.query_one("#stdout").clear()
        self.query_one("#stderr").clear()
        self.query_one("#stdout_filename").update(f"STDOUT Log File: {stdout_file}")
        self.query_one("#stderr_filename").update(f"STDERR Log File: {stderr_file}")
        if os.path.exists(stdout_file):
            for line in read_file(stdout_file):
                self.query_one("#stdout").write(
                    line.strip(), width=os.get_terminal_size().columns - 2,
                )
        else:
            self.query_one("#stdout").write(f"Path does not exist: {stdout_file}")

        if os.path.exists(stderr_file):
            for line in read_file(stderr_file):
                self.query_one("#stderr").write(
                    line.strip(), width=os.get_terminal_size().columns - 2,
                )
        else:
            self.query_one("#stderr").write(f"Path does not exist: {stderr_file}")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        job_id, task_id = event.row_key.value.split("_")
        key = (job_id, task_id)
        if key in self.squeue_lookup:
            entry = self.squeue_lookup[(job_id, task_id)]
            self.entry = entry
        else:
            raise ValueError(f"Unexpected missing key {key} in:\n{self.squeue_lookup}")
        if self.entry["state"] == "RUNNING":
            self.num_nodes = len(entry["stdout"])
            self.selected_node = 0
            if len(entry["stdout"]) > 1:
                self.query_one("#node_buttons").remove_class("hidden")
            else:
                self.query_one("#node_buttons").add_class("hidden")
            self._update_log_outputs()
        else:
            out = self.query_one("#stdout")
            err = self.query_one("#stderr")
            out.clear()
            err.clear()
            state = self.entry["state"]
            out.write(f"Selected slurm job has not started yet, is in state: {state}")
            err.write(f"Selected slurm job has not started yet, is in state: {state}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next_node":
            self.selected_node = (self.selected_node + 1) % self.num_nodes
            self._update_log_outputs()
        elif event.button.id == "prev_node":
            self.selected_node = (self.selected_node - 1) % self.num_nodes
            self._update_log_outputs()

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator(id="loading")
        yield DataTable(id="queue_table")
        yield Horizontal(
            Button("Previous Node", id="prev_node", classes="node_button"),
            Button("Next Node", id="next_node", classes="node_button"),
            id="node_buttons",
            classes="hidden",
        )
        with TabbedContent(id="logs", classes="green_border"):
            with TabPane("STDOUT"):
                with Vertical(id='stdout_tab'):
                    yield Label(id="stdout_filename", classes="filename_label")
                    yield TextLog(id="stdout", highlight=True, markup=True, wrap=True)
            with TabPane("STDERR"):
                with Vertical(id='stderr_tab'):
                    yield Label(id="stderr_filename", classes="filename_label")
                    yield TextLog(id="stderr", highlight=True, markup=True, wrap=True)
        yield Footer()

    def action_refresh_slurm(self) -> None:
        self._update_slurm()


if __name__ == "__main__":
    app = SlurmDashboardApp()
    app.run()
