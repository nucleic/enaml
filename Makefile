.PHONY: all clean test cover

all:  
	make clean
	python setup.py install

clean:
	rm -rf build
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f

test: 
	make clean
	python -m py.test
	python setup.py check -r
	
cover: 
	make clean
	coverage run --source enaml -m py.test
	coverage report

release:
	make clean
	python setup.py register
	python setup.py bdist_wheel upload
	python setup.py sdist --formats=gztar,zip upload
