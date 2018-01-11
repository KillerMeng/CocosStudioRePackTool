# coding=utf-8

"""
    description: split the plist file created by Cocos Studio and pack it again with extend images
    time: 2018-01-11 10:21:41
    author: KillerMeng
    version: 1.0
    usage: python main.py /path/a.plist /extendImages
"""

import os
import sys
import shutil
from xml.etree import ElementTree
from PIL import Image


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index + 1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d


def find_all_img(path, cb, join_file):
    find_list = os.listdir(path)
    for f in find_list:
        if f.find('.svn') > 0 or f.find(".DS_Store") > 0 or f.startswith("~$"):
            continue
        f_path = os.path.join(path, f)
        if os.path.isdir(f_path):
            print("recursive create folder:{}".format(os.path.join(join_file, f)))
            find_all_img(f_path, cb, os.path.join(join_file, f))
        else:
            if f.endswith('.png') or f.endswith('.jpg'):
                cb(f_path, join_file)


class SplitAndPack(object):
    def __init__(self, path_runtime, path_plist, path_extend_png):
        # the python script path
        self.path_runtime = path_runtime
        # the file need split(*.plist and *.png)
        self.path_plist = path_plist
        self.path_png = path_plist.replace('.plist', '.png')
        # extend png path
        self.path_extend_png = path_extend_png
        # need split file name
        self.old_res_name = os.path.split(self.path_plist)[1].split('.')[0]
        # the path of split images
        self.path_split_png = os.path.join(self.path_runtime, 'split_png')
        # export path
        self.path_export = os.path.join(self.path_runtime, 'export')

    # convert plist to images
    def plist_to_img(self):
        # remove old split png
        if os.path.exists(self.path_split_png):
            shutil.rmtree(self.path_split_png)
        if not os.path.isdir(self.path_split_png):
            os.makedirs(self.path_split_png)

        # create export file folder
        if not os.path.isdir(self.path_export):
            os.makedirs(self.path_export)

        # load plist
        plist_content = open(self.path_plist, 'r').read()
        # load png
        src_image = Image.open(self.path_png)

        # convert to ElementTree
        plist_root = ElementTree.fromstring(plist_content)
        # tree => dict
        plist_dict = tree_to_dict(plist_root[0])
        # {x,b}=>[x,y]
        to_list = lambda x: x.replace('{', '').replace('}', '').split(',')

        for k, v in plist_dict['frames'].items():
            pos_str = str(v['frame'])
            rect_list = to_list(pos_str)
            width = int(rect_list[3] if v['rotated'] else rect_list[2])
            height = int(rect_list[2] if v['rotated'] else rect_list[3])
            bounding_box = (
                int(rect_list[0]),
                int(rect_list[1]),
                int(rect_list[0]) + width,
                int(rect_list[1]) + height,
            )
            # size_list = [int(x) for x in to_list(v['sourceSize'])]

            rect_image = src_image.crop(bounding_box)
            if v['rotated']:
                rect_image = rect_image.rotate(90, expand=1)
            # rect_image.show()

            # check if the frame name is a path,such as '/aa/bb/cc.png'
            k_path = os.path.split(k)
            if k_path[0] != '':
                out_file_dir = os.path.join(self.path_split_png, k_path[0])
                if not os.path.isdir(out_file_dir):
                    print("create new folder", out_file_dir)
                    os.makedirs(out_file_dir)

            outfile = os.path.join(self.path_split_png, k)
            rect_image.save(outfile)

    # copy all extend images to split folder
    def copy_extend_to_split(self):
        def copy_one(file_path, join_file):
            des_path = os.path.join(self.path_split_png, join_file)
            if not os.path.exists(des_path):
                os.makedirs(des_path)
            print('copy', file_path, "to", des_path)
            check_path = os.path.join(des_path, os.path.split(file_path)[1])
            if os.path.exists(check_path):
                print('\nwarning! the new image:{} have the same name with one old image in plist'.format(check_path))
                sys.exit(-1)
            shutil.copy(file_path, des_path)

        print("---start copy---")
        find_all_img(self.path_extend_png, copy_one, '')
        print("---copy end---")

    # repack all image include split images and extend images
    def repack_all_image(self):
        cmd = 'TexturePacker --smart-update ' \
              '--format cocos2d ' \
              '--padding 2 ' \
              '--data {ex_plist} ' \
              '--sheet {ex_png} ' \
              '--size-constraints NPOT ' \
              '--enable-rotation ' \
              '--dither-fs-alpha ' \
              '--opt RGBA8888 ' \
              '--multipack ' \
              '--trim ' \
              '{new_img}'.format(ex_plist=os.path.join(self.path_export, '{}{}'.format(self.old_res_name, ".plist")),
                                 ex_png=os.path.join(self.path_export, '{}{}'.format(self.old_res_name, ".png")),
                                 new_img=self.path_split_png
                                 )
        print(cmd)
        print('\n')
        os.system(cmd)


# 1:plist path
# 2:extend img folder path
if __name__ == '__main__':
    if len(sys.argv) <= 3:
        runtime_path = os.path.split(sys.argv[0])[0]
        arg_plist_path = sys.argv[1]
        extend_img_folder_path = sys.argv[2]

        split_and_pick = SplitAndPack(runtime_path, arg_plist_path, extend_img_folder_path)
        split_and_pick.plist_to_img()
        split_and_pick.copy_extend_to_split()
        split_and_pick.repack_all_image()
        print('\nsuccess')
    else:
        print('parameter error')
        sys.exit(1)
