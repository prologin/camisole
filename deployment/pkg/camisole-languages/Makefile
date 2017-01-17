OBJS := build_depends.py

all: pkg .SRCINFO

PKGBUILD: PKGBUILD.in $(OBJS)
	awk '{if($$0=="depends=()"){system("PYTHONPATH=../../.. python build_depends.py")}else{print}}' $< >$@
	updpkgsums

.SRCINFO: PKGBUILD
	mksrcinfo

pkg: PKGBUILD
	makepkg -fc

clean:
	$(RM) PKGBUILD .SRCINFO *.pkg.*

.PHONY: all clean
