#include <iostream>
#include <libssh/libssh.h>

int main() {
    std::cout<<"libssh version is "<< SSH_STRINGIFY(LIBSSH_VERSION)<<"\n";

    return 0;
}
