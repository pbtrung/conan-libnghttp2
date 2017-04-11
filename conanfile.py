from conans import ConanFile, CMake, tools, ConfigureEnvironment
from conans.tools import download, unzip
import os


class Nghttp2Conan(ConanFile):
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
        cmake = CMake(self.settings)
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
            if self.settings.arch == "x86":
                env_line = env.command_line_env.replace('-m64', '')
                env_line = env_line.replace('-m32', '')
                env_line = env_line.replace('CFLAGS="', 'CFLAGS="-m32 ')
            elif self.settings.arch == "x86_64":
                env_line = env.command_line_env.replace('-m32', '')
                env_line = env_line.replace('-m64', '')
                env_line = env_line.replace('CFLAGS="', 'CFLAGS="-m64 ')

            self.output.warn(env_line)

        shared = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else ""
        cd_src = "cd " + self.src_dir
        self.run("%s && cmake . %s %s" % (cd_src, cmake.command_line, shared))
        self.run("%s && cmake --build . %s" % (cd_src, cmake.build_config))

    def package(self):
        self.copy("*.h", dst="include/nghttp2", src=self.src_dir + "/lib/includes/nghttp2")
        self.copy("*.pc", dst="lib/pkgconfig", src=self.src_dir + "/lib")
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["nghttp2"]
