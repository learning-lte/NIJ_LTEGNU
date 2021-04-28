INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_NIJ NIJ)

FIND_PATH(
    NIJ_INCLUDE_DIRS
    NAMES NIJ/api.h
    HINTS $ENV{NIJ_DIR}/include
        ${PC_NIJ_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    NIJ_LIBRARIES
    NAMES gnuradio-NIJ
    HINTS $ENV{NIJ_DIR}/lib
        ${PC_NIJ_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NIJ DEFAULT_MSG NIJ_LIBRARIES NIJ_INCLUDE_DIRS)
MARK_AS_ADVANCED(NIJ_LIBRARIES NIJ_INCLUDE_DIRS)

