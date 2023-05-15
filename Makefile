
all: build serve

build:
	jupyter-book build . --config docs/_config.yml --toc docs/_toc.yml
	mkdir ./_build/html/docs/maps
	cp ./docs/maps/*.* -t _build/html/docs/maps
serve:
	open _build/html/index.html
