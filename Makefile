.PHONY: validate build clean

validate:
	check-jsonschema --schemafile schema/addon.schema.json addons/*.yaml
	python scripts/validate_addons.py

build:
	python scripts/build_matrix.py

clean:
	python -c "from pathlib import Path; p=Path('dist/matrix.yaml'); p.unlink(missing_ok=True)"
