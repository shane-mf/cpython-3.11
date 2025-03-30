/* Minimal main program -- everything is loaded from the library */

#include "Python.h"

#ifdef MS_WINDOWS
int
wmain(int argc, wchar_t **argv)
{
    return Py_Main(argc, argv);
}
#else
int
main(int argc, char **argv)
{
    printf("Hello, Mf! this is main(int argc, char **argv) in python.c\n");
    return Py_BytesMain(argc, argv);
}
#endif
