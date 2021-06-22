import os
import hparams as hp

from utils import backup_meta, create_lab, create_dictionary, create_lexicon

def main():
    audio_path = hp.audio_path
    meta_path = os.path.join(hp.data_path, hp.meta_name)
    print(audio_path)
    print(meta_path)

    # copy meta file as meta_backup.txt
    backup_meta(meta_path)

    # create .lab files from metadata
    create_lab(audio_path, meta_path)

    # create dictionary
    p_dict = create_dictionary(meta_path, 1)

    # create lexicon file
    lex_path = create_lexicon(audio_path, p_dict)

    # filter out short audio files in meta
    filter_short(meta_path, audio_path)

    # resample audio files to 22050 Hz, original files move to "original" directory
    resample(hp.data_path)



if __name__ == '__main__':
    main()
