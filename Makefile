
.PHONY: all clean Makefile Linux-full/BaseOS Linux-full/AppStream Weka tarballs/wms-gui.tgz
.DEFAULT_GOAL:=all

# to do: download iso from http://dl.rockylinux.org/vault/rocky/8.6/isos/x86_64/Rocky-8.6-x86_64-dvd1.iso rather than expecting it to be there

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

SUFFIX=-${BRANCH}
SOURCEISO=../Rocky-8.6-LTS/Rocky-8.6-LTS-dvd1.iso

LABEL := $(shell file -L ${SOURCEISO} | cut -d\' -f2)
#WEKAVERSIONS=$(wildcard weka-*.tar)
ISO=wekamanage${SUFFIX}.iso
DIR=$(ISO:%.iso=%.dir)

all: ${DIR} ${ISO} dist
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

${DIR}: docker-ce tarballs/ansible-install.tgz tarballs/tools.tgz tarballs/weka-mon.tgz tarballs/local-weka-home.tgz tarballs/wms-gui.tgz
	@echo Creating build directory for $@ 
	mkdir -p source_iso
	mount ${SOURCEISO} source_iso
	./prep_base.py source_iso $@
	#
	#cp -rf source_iso $@ # need to trim - how to copy everything BUT the repos?  Python??
	#rsync -a --info=progress2 --delete source_iso/ $@
	cp -rf wekabits $@
	cp -rf tarballs $@
	cp -rf docker-ce $@
	cp -f datafiles/partmap $@
	cp -f datafiles/ks-* $@
	cp -rf python-wheels $@
	#
	# now we have to trim the full repos to only what we need.
	./prep_repos.py packlist $@ source_iso docker-ce
	umount source_iso
	echo Install kickstart
	cp -rf $@/datafiles/grub.cfg $@/EFI/BOOT
	sed -i 's/WEKA/WEKA Management Station/' $@/EFI/BOOT/grub.cfg
	# run this twice so we get the first 2 occurences only
	sed -i "0,/quiet/{s/quiet/inst.ks=hd:LABEL=${LABEL}/}" $@/EFI/BOOT/grub.cfg
	sed -i "0,/quiet/{s/quiet/inst.ks=hd:LABEL=${LABEL}/}" $@/EFI/BOOT/grub.cfg
	cp -f datafiles/isolinux.cfg $@/isolinux/isolinux.cfg
	cp -f datafiles/grub.conf $@/isolinux/grub.conf
	#cp -f datafiles/isolinux.cfg $@/isolinux/isolinux.cfg
	cp -f README.md $@/wekabits
	cp -rf $@/datafiles/product.img $@/images
	cp -rf $@/datafiles/ks.cfg $@
	cp -rf $@/datafiles/partitioner.sh $@
	echo 'module_hotfixes=1' >> $@/media.repo
	touch $@
	date > $@/.weka-buildstamp
	echo ${BRANCH} > $@/.wms-version

#trimmed_iso:
#	mkdir -p source_iso
#	mount ${SOURCEISO} source_iso
	# AppStream  BaseOS  datafiles  EFI  images  isolinux  LICENSE  LTS  media.repo  OFED58  TRANS.TBL  Weka
	#cp -r source_iso/datafiles


tarballs/tools.tgz:
	./repack_tools

tarballs/ansible-install.tgz:
	cd tarballs; curl -LO https://weka-repo.s3.amazonaws.com/ansible-install.tgz

tarballs/weka-mon.tgz:
	cd tarballs; curl -LO https://weka-repo.s3.amazonaws.com/weka-mon.tgz

tarballs/wms-gui.tgz: 
	$(MAKE) -C wms-gui
	tar cvzf $@ wms-gui

tarballs/local-weka-home.tgz:
	#mkdir -p /tmp/local-weka-home
	#cd /tmp/local-weka-home; curl -OL https://home-weka-io-offline-packages-dev.s3.eu-west-1.amazonaws.com/weka_minikube.tar.gz
	#cd /tmp/local-weka-home; tar xvf weka_minikube.tar.gz; rm weka_minikube.tar.gz
	#cd /tmp/local-weka-home; curl -OL https://home-weka-io-offline-packages-dev.s3.eu-west-1.amazonaws.com/wekahome-vm-docker-images.tar.gz
	#cd /tmp/local-weka-home; tar xvf wekahome-vm-docker-images.tar.gz; rm wekahome-vm-docker-images.tar.gz
	#cd /tmp; tar czvf local-weka-home.tgz local-weka-home
	#rm -rf /tmp/local-weka-home
	#mv /tmp/local-weka-home.tgz $@

clean:
	@echo making clean
	rm -rf ${ISO} ${DIR}
	umount source_iso


docker-ce:
	@echo Updating $@
	mkdir -p docker-ce
	reposync --repo=docker-ce-stable --download-path $@ --norepopath --newest-only
	./repo_subdir $@
	createrepo docker-ce
	touch $@

upload:
	./aws_upload_iso ${ISO}

dist:	dist-test #dist-whorfin

dist-test:
	cp ${ISO} /space/test_isos

dist-whorfin:
	scp ${ISO} whorfin:/sns/samba_share

