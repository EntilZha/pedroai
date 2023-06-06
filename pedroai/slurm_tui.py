from pathlib import Path
import subprocess
import os

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, LoadingIndicator, DataTable, TextLog, TabbedContent, TabPane, Markdown, Pretty, Static
from rich.text import Text


#SQUEUE = "squeue --me --format='%.18i %.9P %.30j %.8T %.10M %.9l %.6D %R'"
SQUEUE = "squeue --me --Format='JobID:|,ArrayJobID:|,ArrayTaskID:|,Partition:|,Name:|,State:|,TimeUsed:|,NumNodes:|,Nodelist:|,STDOUT:|,STDERR:'"
FIELDS = [
    'job_id',
    'array_job_id',
    'array_task_id',
    'partition',
    'name',
    'state',
    'time_used',
    'num_nodes',
    'nodelist',
    'stdout',
    'stderr'
]
DISPLAY_FIELDS = FIELDS[:-2]


def run_squeue():
    proc = subprocess.run(SQUEUE, shell=True, capture_output=True, check=True, text=True)
    lines = proc.stdout.strip().split('\n')
    table_rows = []
    for idx, l in enumerate(lines):
        if idx == 0:
            continue
        fields = l.strip().split('|')
        if len(fields) != len(FIELDS):
            raise ValueError(f"Unequal number of fields: {len(fields)} versus {len(FIELDS)}")
        row = {}
        for i in range(len(fields)):
            curr_field = FIELDS[i]
            value = fields[i]
            row[curr_field] = value

        if '%A' in row['stdout']:
            row['stdout'] = row['stdout'].replace('%A', row['array_job_id']).replace("%a", row['array_task_id'])
            row['stderr'] = row['stderr'].replace('%A', row['array_job_id']).replace("%a", row['array_task_id'])
        elif '%j' in row['stdout']:
            row['stdout'] = row['stdout'].replace('%j', row['job_id'])
            row['stderr'] = row['stderr'].replace('%j', row['job_id'])
        table_rows.append(row)
    lookup_table = {(r['array_job_id'], r['array_task_id']): r for r in table_rows}
    return table_rows, lookup_table


def read_file(path: Path):
    with open(path) as f:
        return f.read()
        


class SlurmDashboardApp(App):
    BINDINGS = [
        ('r', 'refresh_slurm', 'Refresh Slurm'),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = 'slurm_tui_styles/style.css'

    def _update_slurm(self):
        self.squeue_rows, self.squeue_lookup = run_squeue()
        table = self.query_one(DataTable)
        table.clear()
        for (job_id, task_id), row in self.squeue_lookup.items():
            cells = [row[f] for f in DISPLAY_FIELDS]
            table.add_row(*cells, key=f'{job_id}_{task_id}')
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*DISPLAY_FIELDS)
        table.cursor_type = 'row'
        self._update_slurm()
        self.query_one('#stdout').write('No Log File Selected', width=os.get_terminal_size().columns - 2)
        self.query_one('#stderr').write('No Log File Selected', width=os.get_terminal_size().columns - 2)
        self.query_one('#loading').add_class('hidden')
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        job_id, task_id = event.row_key.value.split('_')
        key = (job_id, task_id)
        if key in self.squeue_lookup:
            entry = self.squeue_lookup[(job_id, task_id)]
        else:
            raise ValueError(f"Unexpected missing key {key} in:\n{self.squeue_lookup}")
        stdout_file = entry['stdout']
        stderr_file = entry['stderr']
        self.query_one('#stdout').clear()
        self.query_one('#stderr').clear()
        if os.path.exists(stdout_file):
            self.query_one('#stdout').write(read_file(stdout_file), width=os.get_terminal_size().columns - 2)
        else:
            self.query_one('#stdout').write(f'Path does not exist: {stdout_file}')
        
        if os.path.exists(stderr_file):
            self.query_one('#stderr').write(read_file(stderr_file), width=os.get_terminal_size().columns - 2)
        else:
            self.query_one('#stderr').write(f'Path does not exist: {stderr_file}')
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator(id="loading")
        yield DataTable(id='queue_table')
        with TabbedContent(id='logs'):
            with TabPane("STDOUT", classes='max_height'):
                yield TextLog(id='stdout', highlight=True, markup=True, wrap=True, classes='max_height')
            with TabPane("STDERR", classes='max_height'):
                yield TextLog(id='stderr', highlight=True, markup=True, wrap=True, classes='max_height')
        yield Footer()
    
    def action_refresh_slurm(self) -> None:
        self._update_slurm()


if __name__ == '__main__':
    app = SlurmDashboardApp()
    app.run()