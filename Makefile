
.PHONY: all clean Makefile Linux-full/BaseOS Linux-full/AppStream Weka
.DEFAULT_GOAL:=all

# to do: download iso from http://dl.rockylinux.org/vault/rocky/8.6/isos/x86_64/Rocky-8.6-x86_64-dvd1.iso rather than expecting it to be there
SOURCEISO=../Rocky-8.6-LTS/Rocky-8.6-LTS-beta.iso
#SOURCEISO=../Rocky-8.6-LTS/Rocky-8.6-LTS-dvd1.iso

SUFFIX=-beta6

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

${DIR}: docker-ce ${SOURCEISO} wekabits/tools.tgz wekabits/weka-mon.tgz wekabits/local-weka-home.tgz wekabits/wms-gui.tgz
	@echo Creating build directory for $@ 
	mkdir -p source_iso
	mount ${SOURCEISO} source_iso
	cp -r source_iso $@
	umount source_iso
	cp -r wekabits $@
	#cp -r Weka $@	- now has weka on it already
	cp -r docker-ce $@
	#cp datafiles/ks.cfg $@
	cp datafiles/partmap $@
	cp datafiles/ks-* $@
	#cp datafiles/ks-local-repos $@
	#cp datafiles/ks-postinstall $@
	cp -r python-wheels $@
	echo Install kickstart
	cp datafiles/grub.cfg $@/EFI/BOOT/grub.cfg
	cp datafiles/grub.conf $@/isolinux/grub.conf
	cp datafiles/isolinux.cfg $@/isolinux/isolinux.cfg
	cp README.md $@/wekabits
	touch $@
	date > $@/.weka-buildstamp

wekabits/tools.tgz:
	./repack_tools

wekabits/weka-mon.tgz:
	cd wekabits; curl -LO https://weka-repo-test.s3.us-west-2.amazonaws.com/weka-mon.tgz

wekabits/wms-gui.tgz: 
	$(MAKE) -C wms-gui
	tar cvzf $@ wms-gui

wekabits/local-weka-home.tgz:
	cd wekabits; curl -LO https://weka-repo-test.s3.us-west-2.amazonaws.com/local-weka-home.tgz

clean:
	@echo making clean
	rm -rf ${ISO} ${MYTARGETS}


docker-ce:
	@echo Updating docker-ce
	mkdir -p docker-ce
	reposync --repo=docker-ce-stable --download-path $@ --norepopath --newest-only
	createrepo docker-ce
	touch $@

upload:
	./aws_upload_iso ${ISO}

dist:
	scp ${ISO} zweka07:/opt
	scp ${ISO} whorfin:/sns/samba_share
