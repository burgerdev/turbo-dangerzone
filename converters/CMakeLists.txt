project(blockedarray)

cmake_minimum_required(VERSION 2.8)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})

set(Python_ADDITIONAL_VERSIONS 2.7)
find_package(PythonLibs 2.7 REQUIRED)
find_package(PythonInterp 2.7 REQUIRED)
find_package(Numpy REQUIRED)
find_package(Boost COMPONENTS python REQUIRED)

#
# The converter python module
#

include_directories(
    ${PYTHON_INCLUDE_DIR}
    ${PROJECT_SOURCE_DIR}
    ${PYTHON_NUMPY_INCLUDE_DIR}
)

add_library(converter SHARED
    converter.cxx
)

if(WIN32 OR APPLE)
    set(RT_LIBRARY "")
else()
    set(RT_LIBRARY "rt")
endif()

target_link_libraries(converter
    ${PYTHON_LIBRARY}
    ${Boost_PYTHON_LIBRARIES}
    ${VIGRA_IMPEX_LIBRARY}
    ${RT_LIBRARY}
)
if(BUILD_COMMON_DTYPES_LIBRARY)
    target_link_libraries(converter bw)
endif()

if(WIN32)                                                                                                               
    set_target_properties(converter PROPERTIES OUTPUT_NAME "converter" PREFIX "" SUFFIX  ".pyd")
elseif(APPLE)
    set_target_properties(converter PROPERTIES OUTPUT_NAME "converter" PREFIX "" SUFFIX ".so")
else()
    set_target_properties(converter PROPERTIES OUTPUT_NAME "converter" PREFIX "")
endif()


