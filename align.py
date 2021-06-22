import os
import shutil
import argparse
import hparams as hp

from glob import glob
from tqdm import tqdm
from sklearn.model_selection import train_test_split

def main():
    parser = argparse.ArgumentParser(
        description = 'Performs MFA train/align'
        'MFA must already be installed (refer to https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html)'
        'and must be inside aligner conda environment'
    )
    parser.add_argument(
        '--align_only',
        action = 'store_true',
        help = 'Activate to only perform alignment using pretrained model instead of training from scratch'
    )
    args = parser.parse_args()

    meta_path = os.path.join(hp.data_path, hp.meta_name)
    lex_path = os.path.join(hp.data_path, 'lexicon.txt')

    if not args.align_only:
        # execute mfa training
        mfa_train = 'mfa train {} {} {} -o {} --clean --beam 1000'.format(hp.audio_path, lex_path, os.path.join(base_path, 'mfa_result'), base_path)
        print(f'Executing mfa train command: {mfa_train}')
        os.system(mfa_train)
    else:
        # execute mfa alignment
        mfa_align = 'mfa align {} {} {} {} --clean --beam 1000'.format(hp.audio_path, lex_path, '~/kss_model.zip', os.path.join(base_path, 'mfa_result'))
        print(f'Executing mfa align command: {mfa_align}')
        os.system(mfa_align)

    # train test split
    text_list = open(meta_path, 'r').readlines()
    train, test = train_test_split(text_list, test_size = 0.03, random_state = 42)
    print(len(train), len(test))

    with open(meta_path, 'w') as new:
        for line in test:
            new.write('1/' + line.replace('.flac', '.wav'))
        for line in train:
            new.write('2/' + line.replace('.flac', '.wav'))
    
    with open(meta_path, 'r') as meta:
        for line in tqdm(meta):
            path = line.split('|')[0]
            shutil.move(f'{dir}/wavs/{path[2:]}', f'{dir}/{path}')

if __name__ == '__main__':
    main()