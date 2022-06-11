# -*- coding: utf-8 -*-

#
# ダウンロードしたwavファイルを，サンプリングレート16000Hzのデータに変換します．
# また，変換したwavデータのリストを作成します．
#

# サンプリング周波数を変換するためのモジュール(sox)をインポート
import sox

import os
from pathlib import Path
import sys

from tqdm import tqdm

#
# メイン関数
#
def main(data_dir='../data'):

    if isinstance(data_dir, str):
        data_dir = Path(data_dir)

    # wavファイルが展開されたディレクトリ
    original_wav_dir = data_dir / 'original/jsut_ver1.1/basic5000/wav'

    # フォーマット変換したwavファイルを出力するディレクトリ
    out_wav_dir = data_dir / 'wav'

    # wavデータのリストを格納するディレクトリ
    out_scp_dir = data_dir / 'label/all'

    # 出力ディレクトリが存在しない場合は作成する
    out_wav_dir.mkdir(parents=True, exist_ok=True)
    out_scp_dir.mkdir(parents=True, exist_ok=True)

    # soxによる音声変換クラスを呼び出す
    tfm = sox.Transformer()
    # サンプリング周波数を 16000Hz に変換するよう設定する
    tfm.convert(samplerate=16000)

    # wavデータのリストファイルを書き込みモードで開き，以降の処理を実施する
    with open(out_scp_dir / 'wav.scp', mode='w') as scp_file:
        # BASIC5000_0001.wav ~ BASIC5000_5000.wav に対して処理を繰り返し実行
        for i in tqdm(range(5000)):
            filename = 'BASIC5000_%04d' % (i+1)
            # 変換元のオリジナルデータ (48000Hz)のファイル名
            wav_path_in = original_wav_dir / (filename + '.wav')
            # 変換後のデータ(16000Hz)の保存ファイル名
            wav_path_out = out_wav_dir / (filename + '.wav')

            # ファイルが存在しない場合はエラー
            assert wav_path_in.exists()

            # サンプリング周波数の変換と保存を実行する
            tfm.build_file(input_filepath=str(wav_path_in), 
                           output_filepath=str(wav_path_out))

            # wavファイルのリストを書き込む
            scp_file.write('%s %s\n' % 
                           (filename, os.path.abspath(wav_path_out)))

if __name__ == "__main__":
    main(*sys.argv[1:])
