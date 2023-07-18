$(info ===============================================)
$(info Running Makefile commands under shell: $(SHELL))
$(info ===============================================)


# ===============================================
#	Variables
# ===============================================

PYINSTALLER=$(shell which pyinstaller)


# ===============================================
#	Do-it-all functions
# ===============================================

sc: style check


# ===============================================
#	Targets
# ===============================================

tk_win:
	cd binarization && pyinstaller --onefile --windowed --icon="rybkacore_brown.ico" RybkaSoft.py
	move "binarization\dist\RybkaSoft.exe" "."
	rmdir /s /q binarization\build binarization\dist binarization\__pycache__
	del binarization\RybkaSoft.spec

tk_linux:
	cd binarization && $(PYINSTALLER) --onefile --windowed --icon="rybkacore.xbm" RybkaSoft.py
	mv "binarization/dist/RybkaSoft" "."
	rm -rf binarization/build binarization/dist binarization/__pycache__
	rm -f binarization/RybkaSoft.spec



# ===============================================
#	Code Reformatting
# ===============================================

style: black isort

isort:
	( isort --recursive . )

black:
	( black --line-length 100 . )

format: style


# ===============================================
#	Static Code Analysis
# ===============================================

checks: pylint pydocstyle flake8

pylint:
	( pylint --rcfile=.pylintrc --output-format=parseable **/*.py )

pydocstyle:
	( pydocstyle --match-dir=. . )

flake8:
	( flake8 --exclude=.git,__pycache__,.mypy_cache --max-line-length=100 . )

check: checks