OUTPUT = paper.pdf

CONTENT = paper.markdown

PANDOC = pandoc
FLAGS = --smart \
		--standalone \
		--filter pandoc-citeproc \
		--output $(OUTPUT)


.PHONY: clean

$(OUTPUT): $(CONTENT)
	$(PANDOC) $(FLAGS) -- $(CONTENT)

clean:
	rm -f $(CONTENT)
