from conans import ConanFile, tools, CMake, AutoToolsBuildEnvironment
from conans.util import files
from conans.tools import download, unzip
import os


class Nghttp2Conan(ConanFile):
    description = "HTTP/2 C Library"
    name = "libnghttp2"
    version = "1.21.1"
    src_dir = "nghttp2" + "-" + version
    build_dir = "_build"
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
        with tools.chdir(self.src_dir):
            files.mkdir(self.build_dir)
            with tools.chdir(self.build_dir):
                build_dir_path = os.getcwd()
            if self.settings.os != "Windows":
                env_build = AutoToolsBuildEnvironment(self)
                with tools.environment_append(env_build.vars):
                    self.run("./configure  --prefix=%s" % build_dir_path)
                    self.run("make")
                    self.run("make install")
            else:
                cmake = CMake(self.settings)
                shared = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF -DNGHTTP2_STATICLIB=1"
                ext_flag = "-DENABLE_EXAMPLES=0"
                with tools.chdir(self.build_dir):
                    self.run("cmake .. %s %s %s" % (cmake.command_line, shared, ext_flag))
                    self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        build_dir = os.path.join(self.src_dir, self.build_dir)
        self.copy("*.h", dst="include/nghttp2", src=self.src_dir + "/lib/includes/nghttp2", keep_path=False)
        if self.settings.os != "Windows":
            self.copy("*.pc", dst="lib/pkgconfig", src=build_dir, keep_path=False)
            if self.options.shared:
                self.copy("*.so*", dst="lib", src=build_dir, keep_path=False)
                self.copy("*.dylib", dst="lib", src=build_dir, keep_path=False)
            else:
                self.copy("*.a", dst="lib", src=build_dir, keep_path=False)
        else:
            self.copy("*.dll", dst="bin", src=build_dir, keep_path=False)
            self.copy("*.lib", dst="lib", src=build_dir, keep_path=False)
            self.copy("*.exp", dst="lib", src=build_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nghttp2"]