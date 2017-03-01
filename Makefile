.PHONY: build clean default prepare test

default: build

prepare:
	rm -rf vendor/googletest && git clone https://github.com/google/googletest.git vendor/googletest
	rm -rf cmake_modules && git clone https://github.com/bilke/cmake-modules.git cmake_modules

clean:
	rm -rf ./build/

build:
	mkdir -p build/
	cd build/ && cmake .. && make comp_main

test:
	mkdir -p build/
	cd build/ && cmake .. && make comp_test && ./comp_test && valgrind --leak-check=full --error-exitcode=1 ./comp_test && make comp_coverage
