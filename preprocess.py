import os
import shutil
from data import kss
import hparams as hp

def write_metadata(train, val, out_dir):
    with open(os.path.join(out_dir, 'train.txt'), 'w', encoding='utf-8') as f:
        for m in train:
            f.write(m + '\n')
    with open(os.path.join(out_dir, 'val.txt'), 'w', encoding='utf-8') as f:
        for m in val:
            f.write(m + '\n')

def main():
    in_dir = hp.data_path
    out_dir = hp.preprocessed_path
    meta = hp.meta_name
    textgrid_name = hp.textgrid_name
    textgrid_path=hp.textgrid_path

    build_dir = lambda x: [os.makedirs(os.path.join(x, y), exist_ok = True) for y in ['mel', 'alignment', 'f0', 'energy']]
    build_dir(out_dir)
    
    if not os.path.exists(os.path.join(out_dir, textgrid_name.replace(".zip", ""))):
        os.system('unzip {} -d {}'.format(os.path.join(textgrid_path, textgrid_name), os.path.join(out_dir,textgrid_name.replace(".zip",""))))

    
    if True:
        if not os.path.exists(os.path.join(in_dir, "wavs_bak")):
            os.makedirs(os.path.join(in_dir, "wavs"))
            os.system("mv {} {}".format(os.path.join(in_dir, "../", meta), os.path.join(in_dir)))
            for i in range(1, 3) : os.system("mv {} {}".format(os.path.join(in_dir, str(i)), os.path.join(in_dir, "wavs")))
            os.system("mv {} {}".format(os.path.join(in_dir, "wavs"), os.path.join(in_dir, "wavs_bak")))
            os.makedirs(os.path.join(in_dir, "wavs"))
        else:
            # shutil.rmtree(os.path.join(in_dir, "wavs"))
            # os.makedirs(os.path.join(in_dir, "wavs"))
            pass
    
        train, val = kss.build_from_path(in_dir, out_dir, meta)

    write_metadata(train, val, out_dir)
    
if __name__ == "__main__":
    main()
