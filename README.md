# Taxonomic review of Amietina (Coleoptera: Scarabaeinae) with semantic phenotypes

## Clean generated Markdown

PhenoScript adds specimen and taxon metadata above the first `---` separator in
its Markdown output. Remove that block from every generated Markdown file before
building the manuscript:

```sh
python3 scripts/clean_phenoscript_markdown.py
```

The script scans `Amietina_phenoscript/output/nl` recursively and is safe to run
again after regenerating the files. Use `--dry-run` to preview changes, or pass
another file or directory explicitly. `--check` makes no changes and exits with
status 1 when cleanup is needed, which is useful in an automated build.
