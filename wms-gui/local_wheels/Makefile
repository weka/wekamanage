
.PHONY: all 
.DEFAULT_GOAL:=all
PYTHON=/usr/bin/python3.11

all: clean
	${PYTHON} -m pip download -r ../requirements.txt

clean:
	@echo "Cleaning..."
	rm -f *.whl *.tar.gz
