#!/bin/bash

xhost +local:docker || true

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
echo $ROOT_DIR
if [[ $1 = "--nvidia" ]] || [[ $1 = "-n" ]]
  then
    docker run --gpus all \
                -ti --rm \
                -e "DISPLAY" \
                -e "QT_X11_NO_MITSHM=1" \
                -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
                -e XAUTHORITY \
                -v /dev:/dev \
                -v /home/navn0319/ros2_turtlebot3/ws_slam:/ws_slam \
               --net=host \
               --privileged \
               --name slamn1 slamn1-img

else

    echo "[!] If you wanna use nvidia gpu, please use script with -n or --nvidia argument"
    docker run  -ti --rm \
                -e "DISPLAY" \
                -e "QT_X11_NO_MITSHM=1" \
                -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
                -e XAUTHORITY \
                -v /dev:/dev \
                -v ./ws_slam:/ws_slam \
               --net=host \
               --privileged \
               --name slamn1 slamn1-img
fi


## Permitir que Docker acceda al display X
#xhost +local:docker || true
#
#ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
#echo $ROOT_DIR
#
## Verifica y exporta XAUTHORITY si no está definido
#if [ -z "$XAUTHORITY" ]; then
#  export XAUTHORITY="$HOME/.Xauthority"
#fi
#
## Configuración para GPU Nvidia
#if [[ $1 = "--nvidia" ]] || [[ $1 = "-n" ]]; then
#    docker run --gpus all \
#        -ti --rm \
#        -e DISPLAY=$DISPLAY \
#        -e QT_X11_NO_MITSHM=1 \
#        -e XAUTHORITY=$XAUTHORITY \
#        -e "TURTLEBOT3_MODEL=burger" \
#        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#        -v $XAUTHORITY:$XAUTHORITY \
#        --device=/dev/dri \
#        --mount source=ws_slam,target=/ws_slam \
#        --net=host \
#        --privileged \
#        --name slamn1 slamn1-img
#else
#    echo "[!] If you wanna use nvidia gpu, please use script with -n or --nvidia argument"
#    docker run -ti --rm \
#        -e DISPLAY=$DISPLAY \
#        -e QT_X11_NO_MITSHM=1 \
#        -e XAUTHORITY=$XAUTHORITY \
#        -e "TURTLEBOT3_MODEL=burger" \
#        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
#        -v $XAUTHORITY:$XAUTHORITY \
#        --device=/dev/dri \
#        -v /home/navn0319/ros2_turtlebot3/ws_slam:/ws_slam \
#        --net=host \
#        --privileged \
#        --name slamn1 slamn1-img
#fi
#
