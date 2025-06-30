#!/bin/bash

# 设置环境变量
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig:/opt/homebrew/share/pkgconfig:$PKG_CONFIG_PATH"
export LDFLAGS="-L/opt/homebrew/lib"
export CPPFLAGS="-I/opt/homebrew/include"

# 设置英文环境
export LANG=en_US.UTF-8
export LANGUAGE=en_US
export LC_ALL=en_US.UTF-8

# GTK 相关设置
# export GDK_BACKEND=x11
# export GTK_MODULES="gail:atk-bridge"
# export GTK_IM_MODULE=xim
# export QT_IM_MODULE=xim
# export XMODIFIERS="@im=none"
export XMODIFIERS="@im=none"
# export GDK_BACKEND=quartz
export GTK_IM_MODULE=none

# 确保 XQuartz 正在运行
if ! pgrep -x "Xquartz" > /dev/null; then
    echo "请确保 XQuartz 正在运行"
    echo "如果没有运行，请从应用程序文件夹启动 XQuartz"
fi

# 启动 MyPaint
/opt/local/bin/python3.12 setup.py demo
