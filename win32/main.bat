@echo off 
@echo ##########################################################################
@echo.
@echo       	  ��ӭʹ��Cocos Studio��ͼ���´������
@echo       	�밴��ʾ��������plist�ļ�������ͼƬ�ļ���
@echo. 
@echo ##########################################################################
@echo. 
set path_plist=
set /p path_plist=������plist�ļ�:
echo plist·����%path_plist%
echo.

set img_plist=
set /p img_plist=����������ͼƬ�ļ���:
echo ����ͼƬ·����%img_plist%
echo.

python main.py %path_plist% %img_plist%
explorer.exe %~dp0export
pause