GDBM_CFLAGS="-I$(brew --prefix gdbm)/include" \
   GDBM_LIBS="-L$(brew --prefix gdbm)/lib -lgdbm" \
   py_cv_module__tkinter=n/a \
   ./configure --with-pydebug \
               --with-openssl="$(brew --prefix openssl@3)"