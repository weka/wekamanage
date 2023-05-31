
.PHONY: all clean Makefile Linux-full/BaseOS Linux-full/AppStream Weka tarballs/wms-gui.tgz
.DEFAULT_GOAL:=all

# to do: download iso from http://dl.rockylinux.org/vault/rocky/8.6/isos/x86_64/Rocky-8.6-x86_64-dvd1.iso rather than expecting it to be there

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

SUFFIX=-${BRANCH}
SOURCEISO=../Rocky-8.6-LTS/Rocky-8.6-LTS${SUFFIX}.iso

LABEL := $(shell file ${SOURCEISO} | cut -d\' -f2)
#WEKAVERSIONS=$(wildcard weka-*.tar)
ISO=wekamanage${SUFFIX}.iso
DIR=$(ISO:%.iso=%.dir)

all: ${DIR} ${ISO} 
	@echo making all $<
	@echo ISO is ${ISO}
	@echo TARGETS is ${DIR}

#%wekamanage${SUFFIX}.iso: %wekamanage${SUFFIX}.dir

${ISO}: ${DIR}
	@echo Building ISO for $< target is $@
	@echo LABEL is ${LABEL}
	mkisofs -o $@ -quiet -b isolinux/isolinux.bin -J -R -l -c isolinux/boot.cat -no-emul-boot \
		-boot-load-size 4 -boot-info-table -eltorito-alt-boot -e images/efiboot.img --joliet-long \
		-no-emul-boot -graft-points -V ${LABEL} $<
	implantisomd5 $@

${DIR}: docker-ce ${SOURCEISO} tarballs/ansible-install.tgz tarballs/tools.tgz tarballs/weka-mon.tgz tarballs/local-weka-home.tgz tarballs/wms-gui.tgz
	@echo Creating build directory for $@ 
	mkdir -p source_iso
	mount ${SOURCEISO} source_iso
	#cp -rf source_iso $@
	rsync -a --info=progress2 --delete source_iso/ $@
	umount source_iso
	cp -rf wekabits $@
	cp -rf tarballs $@
	cp -rf docker-ce $@
	cp -f datafiles/partmap $@
	cp -f datafiles/ks-* $@
	cp -rf python-wheels $@
	echo Install kickstart
	sed -i 's/WEKA/WEKA Management Station/' $@/EFI/BOOT/grub.cfg
	# run this twice so we get the first 2 occurences only
	sed -i "0,/quiet/{s/quiet/inst.ks=hd:LABEL=${LABEL}/}" $@/EFI/BOOT/grub.cfg
	sed -i "0,/quiet/{s/quiet/inst.ks=hd:LABEL=${LABEL}/}" $@/EFI/BOOT/grub.cfg
	cp -f datafiles/isolinux.cfg $@/isolinux/isolinux.cfg
	cp -f datafiles/grub.conf $@/isolinux/grub.conf
	cp -f datafiles/isolinux.cfg $@/isolinux/isolinux.cfg
	cp -f README.md $@/wekabits
	touch $@
	date > $@/.weka-buildstamp

tarballs/tools.tgz:
	./repack_tools

tarballs/ansible-install.tgz:
	cd tarballs; curl -LO https://weka-repo-test.s3.us-west-2.amazonaws.com/ansible-install.tgz

tarballs/weka-mon.tgz:
	cd tarballs; curl -LO https://weka-repo-test.s3.us-west-2.amazonaws.com/weka-mon.tgz

tarballs/wms-gui.tgz: 
	$(MAKE) -C wms-gui
	tar cvzf $@ wms-gui

tarballs/local-weka-home.tgz:
	cd tarballs; curl -LO https://weka-repo-test.s3.us-west-2.amazonaws.com/local-weka-home.tgz

clean:
	@echo making clean
	rm -rf ${ISO} ${DIR}


docker-ce:
	@echo Updating docker-ce
	mkdir -p docker-ce
	reposync --repo=docker-ce-stable --download-path $@ --norepopath --newest-only
	createrepo docker-ce
	touch $@

upload:
	./aws_upload_iso ${ISO}

dist:	dist-7 dist-whorfin

dist-7:
	scp ${ISO} zweka07:/opt

dist-whorfin:
	scp ${ISO} whorfin:/sns/samba_share

