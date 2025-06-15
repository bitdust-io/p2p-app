# This Makefile requires the following commands to be available:
# * docker

BUILD_PATH:=$(shell pwd)

build:
	@rm -rf bin/*
	@rm -rf workspace
	@mkdir workspace
	@cp -v src/* workspace/
	@cd image && docker build -t wine-wix . && cd ..
	@docker run --workdir /wix --rm -v $(BUILD_PATH)/workspace:/wix wine-wix candle product.wxs
	@docker run --workdir /wix --rm -v $(BUILD_PATH)/workspace:/wix wine-wix light product.wixobj -sval -ext WixUIExtension -ext WixUtilExtension
	@mv -v workspace/product.msi bin/bitdust-p2p-app.msi
	@echo "Go to GitHub releases page at https://github.com/bitdust-io/p2p-app/releases/tag/alpha"
	@echo "Click [Edit] icon button in the top right corner"
	@echo "First remove the bitdust-p2p-app.msi file from the attached binaries"
	@echo "Then upload bin/bitdust-p2p-app.msi file and click [Update release] button"
