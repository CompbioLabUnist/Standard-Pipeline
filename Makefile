all:

clean:
	rm -fv **/*.sh **/*.txt
.PHONY: clean

purge:
	$(MAKE) clean
	rm -fv **/*.bam
.PHONY: purge
