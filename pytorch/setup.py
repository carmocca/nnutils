import os
import re
import torch
from setuptools import setup, find_packages
from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDAExtension


extra_compile_args = {
    "cxx": ["-std=c++11", "-O2", "-fopenmp"],
    "nvcc": ["-std=c++11", "-O2"],
}

CC = os.getenv("CC", None)
if CC is not None:
    extra_compile_args["nvcc"].append("-ccbin=" + CC)


def get_cuda_compile_archs(nvcc_flags=None):
    """Get the target CUDA architectures from CUDA_ARCH_LIST env variable"""
    if nvcc_flags is None:
        nvcc_flags = []

    CUDA_ARCH_LIST = os.getenv("CUDA_ARCH_LIST", None)
    if CUDA_ARCH_LIST is not None:
        for arch in CUDA_ARCH_LIST.split(";"):
            m = re.match(r"^([0-9.]+)(?:\(([0-9.]+)\))?(\+PTX)?$", arch)
            assert m, "Wrong architecture list: %s" % CUDA_ARCH_LIST
            cod_arch = m.group(1).replace(".", "")
            com_arch = m.group(2).replace(".", "") if m.group(2) else cod_arch
            ptx = True if m.group(3) else False
            nvcc_flags.extend(
                ["-gencode", "arch=compute_{},code=sm_{}".format(com_arch, cod_arch)]
            )
            if ptx:
                nvcc_flags.extend(
                    [
                        "-gencode",
                        "arch=compute_{},code=compute_{}".format(com_arch, cod_arch),
                    ]
                )

    return nvcc_flags


include_dirs = [os.path.dirname(os.path.realpath(__file__)) + "/src"]

headers = [
    "src/adaptive_avgpool_2d.h",
    "src/adaptive_maxpool_2d.h",
    "src/mask_image_from_size.h",
    "src/nnutils/adaptive_pool.h",
    "src/nnutils/utils.h",
    "src/nnutils/cpu/adaptive_avgpool_2d.h",
    "src/nnutils/cpu/adaptive_maxpool_2d.h",
    "src/nnutils/cpu/mask_image_from_size.h",
]

sources = [
    "src/binding.cc",
    "src/adaptive_avgpool_2d.cc",
    "src/adaptive_maxpool_2d.cc",
    "src/mask_image_from_size.cc",
    "src/cpu/adaptive_avgpool_2d.cc",
    "src/cpu/adaptive_maxpool_2d.cc",
    "src/cpu/mask_image_from_size.cc",
]

if torch.cuda.is_available():
    sources += [
        "src/gpu/adaptive_avgpool_2d.cu",
        "src/gpu/adaptive_maxpool_2d.cu",
        "src/gpu/mask_image_from_size.cu",
    ]

    headers += [
        "src/nnutils/gpu/adaptive_avgpool_2d.h",
        "src/nnutils/gpu/adaptive_maxpool_2d.h",
        "src/nnutils/gpu/mask_image_from_size.h",
    ]
    Extension = CUDAExtension

    extra_compile_args["cxx"].append("-DWITH_CUDA")
    extra_compile_args["nvcc"].append("-DWITH_CUDA")
    extra_compile_args["nvcc"].extend(get_cuda_compile_archs())
else:
    Extension = CppExtension


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="nnutils_pytorch",
    version="0.2.1.post1",
    description="PyTorch bindings of the nnutils library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jpuigcerver/nnutils",
    author="Joan Puigcerver",
    author_email="joapuipe@gmail.com",
    license="MIT",
    packages=find_packages(),
    ext_modules=[
        Extension(
            name="nnutils_pytorch._C",
            sources=sources,
            include_dirs=include_dirs,
            extra_compile_args=extra_compile_args,
        )
    ],
    cmdclass={"build_ext": BuildExtension},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    setup_requires=["pybind11", "torch>=0.4.1"],
    install_requires=["pybind11", "torch>=0.4.1"],
)
