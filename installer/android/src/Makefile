REQUIREMENTS_TXT:=../../../requirements.txt
REQUIREMENTS_ANDROID:="kivy==2.1.0,kivymd==1.0.2,PIL,sdl,plyer,pyjnius,service_identity,pyparsing,appdirs,cffi,six,pycryptodome,attrs,hyperlink,idna,cryptography,automat,android,toml,incremental,twisted,python3"

.PHONY: clean pyclean

pyclean:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@rm -rf *.egg-info build
	@rm -rf coverage.xml .coverage

clean: pyclean
	@rm -rf venv

venv:
	@rm -rf venv
	@python3 -m venv venv
	@./venv/bin/pip install --upgrade pip
	@venv/bin/pip install -r $(REQUIREMENTS_TXT)

spec:
	@P_requirements="$(requirements)" ./venv/bin/python3 -c "tpl=open('buildozer.spec.template').read();import os,sys;sys.stdout.write(tpl.format(requirements=os.environ['P_requirements']));" > buildozer.spec

install_buildozer:
	@cd ../sdk/buildozer/ && ../../workspace/venv/bin/python setup.py build && ../../workspace/venv/bin/pip install -e . && cd ../../workspace

build_android_environment: clean venv install_buildozer
	@$(MAKE) spec requirements=$(REQUIREMENTS_ANDROID)

aab:
	@rm -rfv ./bin/BitDustAndroid.aab
	@rm -rfv ./bin/BitDustAndroid_unsigned.aab
	@rm -rfv ./bin/bitdust1-*-release.aab
	@PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v android release 1>buildozer.log 2>buildozer.err
	@cp -f -T -v ./bin/bitdust*arm64-v8a_armeabi-v7a_x86_64-release.aab ./bin/BitDustAndroid_unsigned.aab

apk:
	@rm -rfv ./bin/*.apk
	@PYTHONIOENCODING=utf-8 VIRTUAL_ENV=1 ./venv/bin/buildozer -v --profile arm64_v8a android release 1>buildozer.log 2>buildozer.err
	@cp -v -T -f ./bin/bitdust*.apk ./bin/BitDustAndroid_unsigned.apk
