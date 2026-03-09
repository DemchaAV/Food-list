# Scripts

Maintenance scripts are grouped by responsibility:

- `scripts/data/` - scraping, sync, cleanup, glossary normalization
- `scripts/images/` - image matching, generation, PDF extraction
- `scripts/validation/` - data quality checks
- `scripts/migrations/` - one-off menu update scripts kept for history

Run scripts from the project root, for example:

```powershell
python scripts/validation/validate_scotts.py
python scripts/data/scrape_viewthemenu_allergens.py --url https://viewthe.menu/dbav --out data/viewthemenu_allergens.json
```
