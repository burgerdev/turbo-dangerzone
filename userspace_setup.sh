#!/bin/bash

if [[ `whoami` == 'root' ]]
then
echo "Please drop privileges before using this script."
exit 1
fi


TARGETDIR=${HOME}/hci
LOCALDIR=${HOME}/local
PYTHONDIR=${LOCALDIR}/lib/python2.7/site-packages
LIBPATH=${LOCALDIR}/lib
INCLUDEPATH=${LOCALDIR}/include

cd ${TARGETDIR} || exit $?

remindpython () 
{
    #echo "######################"
    #echo "Add to .bashrc:"
    echo "export PYTHONPATH=\"$1:\$PYTHONPATH\""
    #echo "######################"
}

remindlib () 
{
    #echo "######################"
    #echo "Add to .bashrc:"
    echo "export LD_LIBRARY_PATH=\"$1:\$LD_LIBRARY_PATH\""
    #echo "######################"
}

# PRELIMINARIES

remindpython ${PYTHONDIR}
remindpython ${TARGETDIR}/lazyflow
remindpython ${TARGETDIR}/ilastik
remindpython ${TARGETDIR}/volumina
remindlib ${LIBPATH}


# VIGRA

git clone https://github.com/ukoethe/vigra.git || exit $?

cd vigra || exit $?

mkdir build || exit $?

mkdir -p ${PYTHONDIR} || exit $?

cd build || exit $?

cmake -DCMAKE_INSTALL_PREFIX:PATH="${LOCALDIR}" -DVIGRANUMPY_INSTALL_DIR:PATH=${PYTHONDIR} .. || exit $?

make || exit $?
make install || exit $?

export PYTHONPATH="$PYTHONDIR:$PYTHONPATH" || exit $?
export LD_LIBRARY_PATH="${LIBPATH}:${LD_LIBRARY_PATH}" || exit $?

python -c 'import vigra' || exit $?

cd ../.. || exit $?

# LAZYFLOW

git clone https://github.com/ilastik/lazyflow.git || exit $?

cd lazyflow/lazyflow/drtile

cmake -DVigranumpy_DIR:PATH=$LIBPATH/vigranumpy . || exit $?

cd ../../..

export PYTHONPATH="`pwd`/lazyflow:$PYTHONPATH"

# TODO stuff missing here!

python -c 'import lazyflow' || exit $?

git clone https://github.com/ilastik/volumina.git
git clone https://github.com/ilastik/ilastik.git


# for context: (switch to correct branch!)
# cmake -DVIGRA_INCLUDE_DIR:PATH=${INCLUDEPATH} ..
