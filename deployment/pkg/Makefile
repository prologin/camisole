all: pkg .SRCINFO

PKGBUILD: PKGBUILD.in
	awk '{if($$0=="optdepends=()"){system("PYTHONPATH=../.. python build_optdepends.py")}else{print}}' $< >$@

.SRCINFO: PKGBUILD
	mksrcinfo

pkg: PKGBUILD
	makepkg

.PHONY: all
