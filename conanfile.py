from conans import ConanFile, CMake, tools
import os

class LibsshConan(ConanFile):
    name = "libssh"

    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Libssh here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = ["cmake_paths", "cmake"]
    requires = "zlib/1.2.11@"
    exports_sources = ["patches/**"]
    _source_subfolder = "sources_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libssh-" + self.version, self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file("%s/CMakeLists.txt" % self._source_subfolder, "set(APPLICATION_NAME ${PROJECT_NAME})",
                              '''set(APPLICATION_NAME ${PROJECT_NAME})
set(CONAN_DISABLE_CHECK_COMPILER 1)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)
set(CMAKE_FIND_ROOT_PATH ${CMAKE_FIND_ROOT_PATH} ${CMAKE_MODULE_PATH})
set(OPENSSL_USE_STATIC_LIBS ''' + ('TRUE' if not self.options["openssl"].shared else 'FALSE') + ''')
conan_basic_setup()''')

        #fixme cmake doesnt see this function ...
        tools.replace_in_file("%s/ConfigureChecks.cmake" % self._source_subfolder,
            "check_function_exists(EVP_aes_128_ctr HAVE_OPENSSL_EVP_AES_CTR)",
            "set(HAVE_OPENSSL_EVP_AES_CTR 1)")

        #fixme findSSL link to libcrypto.a and not to libssl.a
        tools.replace_in_file("%s/src/CMakeLists.txt" % self._source_subfolder,
                              "${OPENSSL_CRYPTO_LIBRARY}",
                              "${CONAN_LIBS}")


    def requirements(self):
        if tools.Version(self.version) < "0.8":
            self.requires("openssl/[>=1.0.2a <=1.0.2t]")
        elif tools.Version(self.version) < "0.9":
            self.requires("openssl/[>=1.1.0a <=1.1.0l]")
        else:
            self.requires("openssl/[>=1.1.1a <=1.1.1n]")

    def package_id(self):
        if not self.options["openssl"].shared:
            self.info.options = self.info.full_options

    def configure(self):
        #c library
        del self.settings.compiler.libcxx


    def fixTransitiveCrossLink(self):
        if tools.cross_building(self.settings):
            for root, dirs, files in os.walk("."):
                for name in files:
                    if name == "link.txt":
                        tools.replace_in_file(os.path.join(root, name), "-rpath,", "-rpath-link,")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = True
        cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "ONLY"
        cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "ONLY"
        cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_PACKAGE"] = "ONLY"
        cmake.configure(source_folder=self._source_subfolder)
        self.fixTransitiveCrossLink()
        cmake.build()


    def package(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = True
        cmake.configure(source_folder=self._source_subfolder)
        self.fixTransitiveCrossLink()
        cmake.install()
        self.copy("*.h", dst="include", src="%s/include" % self._source_subfolder)
        self.copy("*ssh.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["ssh"]

