URL = "http://localhost:42920/run?pretty"
SRC = $(wildcard *.in.json)
OUT = $(SRC:.in.json=.out.json)

all: ${OUT}

%.out.json: %.in.json
	curl -s -d "@$^" ${URL} > $@
	@echo >> $@  # Newline
