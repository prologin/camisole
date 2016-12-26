OBJS := camisole-git.install camisole.service sysusers.conf build_optdepends.py

all: pkg .SRCINFO

PKGBUILD: PKGBUILD.in $(OBJS)
	awk '{if($$0=="optdepends=()"){system("PYTHONPATH=../.. python build_optdepends.py")}else{print}}' $< >$@
	updpkgsums

.SRCINFO: PKGBUILD
	mksrcinfo

pkg: PKGBUILD
	makepkg -fc

clean:
	$(RM) PKGBUILD .SRCINFO *.pkg.*

.PHONY: all clean
