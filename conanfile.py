from conans import ConanFile, CMake, tools
from conans.tools import download, unzip
import os


class Nghttp2Conan(ConanFile):
    description = "HTTP/2 C Library"
    name = "libnghttp2"
    version = "1.21.1"
    src_dir = "nghttp2" + "-" + version
    license = "https://raw.githubusercontent.com/nghttp2/nghttp2/master/COPYING"
    url = "https://github.com/pbtrung/conan-nghttp2"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        zip_name = "nghttp2-%s.tar.gz" % self.version
        url = "https://github.com/nghttp2/nghttp2/releases/download/v" + self.version + "/%s"
        download(url % zip_name, zip_name, verify=False)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.settings.os != "Windows":
            cd_src = "cd " + self.src_dir
            self.run("%s && ./configure" % cd_src)
            self.run("%s && make" % cd_src)
        else:
            cmake = CMake(self.settings)
            shared = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF -DNGHTTP2_STATICLIB=1"
            ext_flag = "-DENABLE_EXAMPLES=0"
            cd_src = "cd " + self.src_dir
            self.run("%s && cmake . %s %s %s" % (cd_src, cmake.command_line, shared, ext_flag))
            self.run("%s && cmake --build . %s" % (cd_src, cmake.build_config))

    def package(self):
        self.copy("*.h", dst="include/nghttp2", src=self.src_dir + "/lib/includes/nghttp2", keep_path=False)
        if self.settings.os != "Windows":
            self.copy("*.pc", dst="lib/pkgconfig", src=self.src_dir + "/lib", keep_path=False)
            if self.options.shared == True:
                self.copy("*.so*", dst="lib", keep_path=False)
                self.copy("*.dylib", "bin", keep_path=False)
            else:
                self.copy("*.a", dst="lib", keep_path=False)
        else:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.exp", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nghttp2"]