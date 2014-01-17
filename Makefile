# Note: This is meant for enaml developers, not for end users
#       To install Enaml, please use setup.py.

.PHONY: all clean test cover release

all:  
	make clean
	pip install -e .

clean:
	rm -rf build
	find . -name "*.pyc" -o -name "*.py,cover" | xargs rm -f

test: 
	python -m py.test
	python setup.py check -r
	
cover: 
	coverage run --source enaml -m py.test
	coverage report

release:
	rm -rf dist
	python setup.py register
	python setup.py sdist --formats=gztar,zip upload

gh-pages:
	git checkout master
	git pull origin master
	rm -rf ../enaml_docs
	mkdir ../enaml_docs
	rm -rf docs/build
	make -C docs html
	cp -R docs/build/html/ ../enaml_docs
	mv ../enaml_docs/html ../enaml_docs/docs
	git checkout gh-pages
	rm -rf docs
	cp -R ../enaml_docs/docs/ .
	git commit -a -m "rebuild docs"
	git push upstream-rw gh-pages
	rm -rf ../enaml_docs
	git checkout master
	rm docs/.buildinfo
