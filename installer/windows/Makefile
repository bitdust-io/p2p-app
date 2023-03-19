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
