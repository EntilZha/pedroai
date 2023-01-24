import re
import copy
from typing import List
from pathlib import Path

import bibtexparser
import typer
import tantivy
from rich.console import Console

app = typer.Typer()
console = Console()

def parse_bib(filename):
    parser = bibtexparser.bparser.BibTexParser(
        ignore_nonstandard_types=False,
        interpolate_strings=True,
        common_strings=True,
    )
    with open(filename, 'r') as f:
        bib = bibtexparser.load(f, parser=parser)
        return bib




@app.command('format')
def format_bibtex(input_file: Path, output_file: Path):
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.order_entries_by = ('ENTRYTYPE', 'year', 'title')
    writer.indent = '    '
    writer.add_trailing_comma = True
    bib = parse_bib(input_file)
    out = writer.write(bib)
    with open(output_file, 'w') as f:
        f.write(out)

@app.command('merge')
def merge_bibtex(input_files: List[Path], output_file: Path):
    if len(input_files) == 0:
        raise ValueError("Must provide at least one input file")
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field("title", stored=True, tokenizer_name='en_stem')
    schema_builder.add_text_field("id", stored=True, tokenizer_name='raw')
    schema =  schema_builder.build()
    index = tantivy.Index(schema)
    writer = index.writer()

    first_bib = parse_bib(input_files[0])
    key_to_entry = first_bib.entries_dict
    for e in first_bib.entries:
        writer.add_document(tantivy.Document(title=e['title'], id=e['ID']))
        writer.commit()
    searcher = index.searcher()

    path_to_bib = {}
    for f in input_files[1:]:
        bib = parse_bib(f)
        path_to_bib[f] = bib
        total = len(bib.entries)
        skipped = 0
        new_entries = {}
        for entry in bib.entries:
            if entry['ID'] in key_to_entry or entry['ID'] in new_entries:
                skipped += 1
            else:
                new_entries[entry['ID']] = f, entry
        console.print(f"Entries in {f}, Total: {total} New: {len(new_entries)} Skipped: {skipped}")
    
    console.rule(style='red bold')
    for _, (_, entry) in new_entries.items():
        console.rule("Potentially new entry")
        console.print(entry)
        normalized_title = re.sub(r"[^A-Za-z0-9 ]+", " ", entry["title"]).lower()
        query = index.parse_query(normalized_title, ['title'])
        similar = searcher.search(query, 1).hits
        if len(similar) > 0:
            _, doc_addr = similar[0]
            similar_bib = searcher.doc(doc_addr)
            console.rule("Most similar existing entry")
            console.print(key_to_entry[similar_bib['id'][0]])
        console.rule(style='red bold')
    console.print(f"Outputting new entry candidates to: {output_file}")
    new_db = bibtexparser.bibdatabase.BibDatabase()
    new_db.strings = copy.deepcopy(first_bib.strings)
    for _, entry in new_entries.values():
        new_db.entries.append(entry)

    writer = bibtexparser.bwriter.BibTexWriter()
    writer.order_entries_by = ('ENTRYTYPE', 'year', 'title')
    writer.indent = '    '
    writer.add_trailing_comma = True
    out = writer.write(new_db)
    with open(output_file, 'w') as f:
        f.write(out)
