URL = "http://localhost:42920"
SRC = $(filter-out 004-ocaml-limits.in.json,$(wildcard *.in.json))
OUT = $(SRC:.in.json=.out.json)
OUT += languages.json system.json

CURL = curl -s -H 'content-type: application/json'
PRETTY = python -m json.tool

all: $(OUT)

%.out.json: %.in.json
	$(CURL) -d "@$^" $(URL)/run | $(PRETTY) > $@

languages.json:
	# just keep two example languages: C and Python
	$(CURL) $(URL)/languages | jq '.languages |= {c,python}' | $(PRETTY) > $@

system.json:
	$(CURL) $(URL)/system | $(PRETTY) > $@

clean:
	$(RM) $(OUT)

.PHONY: all clean
