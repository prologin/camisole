OBJS := camisole-git.install camisole.service sysusers.conf _camisole

all: pkg .SRCINFO

PKGBUILD: PKGBUILD.in $(OBJS)
	cp PKGBUILD.in PKGBUILD
	updpkgsums

.SRCINFO: PKGBUILD
	makepkg --printsrcinfo > .SRCINFO

pkg: PKGBUILD
	makepkg -fc

clean:
	$(RM) PKGBUILD .SRCINFO *.pkg.*

.PHONY: all clean
