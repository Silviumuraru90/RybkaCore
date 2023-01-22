$(info ===============================================)
$(info Running Makefile commands under shell: $(SHELL))
$(info ===============================================)



# ===============================================
#	Variables
# ===============================================

PYINSTALLER=$(shell which pyinstaller)



# ===============================================
#	Targets
# ===============================================

tk_win:
	cd binarization && pyinstaller --onefile --windowed --icon="rybka.ico" RybkaSoft.py
	move "binarization\dist\RybkaSoft.exe" "."
	rmdir /s /q binarization\build binarization\dist binarization\__pycache__
	del binarization\RybkaSoft.spec

tk_linux:
	cd binarization && $(PYINSTALLER) --onefile --windowed --icon="rybka.xbm" RybkaSoft.py
	mv "binarization/dist/RybkaSoft" "."
	rm -rf binarization/build binarization/dist binarization/__pycache__
	rm -f binarization/RybkaSoft.spec
