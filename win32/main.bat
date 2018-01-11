@echo off 
@echo ##########################################################################
@echo.
@echo       	  欢迎使用Cocos Studio合图重新打包工具
@echo       	请按提示依次拖入plist文件和新增图片文件夹
@echo. 
@echo ##########################################################################
@echo. 
set path_plist=
set /p path_plist=请拖入plist文件:
echo plist路径：%path_plist%
echo.

set img_plist=
set /p img_plist=请拖入新增图片文件夹:
echo 新增图片路径：%img_plist%
echo.

python main.py %path_plist% %img_plist%
explorer.exe %~dp0export
pause