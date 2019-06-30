# PrePostTool
Tool to automatically generate code for the beginning and end of functions

# Dependencies
+ Clang
+ Python 2.7
+ libclang

# Installation
+ Currently the tool only supports ubuntu 3.8
  + Run [ubuntu_3.8_install.sh](ubuntu_3.8_install.sh)

# Manual installation/Errors with installation
+ For systems not supported by installation script
+ If you can get clang installed, find the location of libclang
+ Set the `libclang_lib` variable to point to the location of libclang
+ Default is set to `'/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1'`

# Example in test.c
`python test.py test.c test.json`
