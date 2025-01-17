# -*- coding: utf-8 -*-

#
# 短時間フーリエ変換を用いて
# 音声のスペクトログラムを作成します．
#

# wavデータを読み込むためのモジュール(wave)をインポート
import wave

# 数値演算用モジュール(numpy)をインポート
import numpy as np

# プロット用モジュール(matplotlib)をインポート
import matplotlib.pyplot as plt

import sys
import pathlib


class Waveform:
    def __init__(self, wav_file):
        # wavファイルを開き、以降の処理を行う
        with wave.open(str(wav_file)) as wav:
            # サンプリング周波数 [Hz] を取得
            sample_frequency = wav.getframerate()

            # wavデータのサンプル数を取得
            num_samples = wav.getnframes()

            # wavデータを読み込む
            data = wav.readframes(num_samples)

            # 読み込んだデータはバイナリ値(16bit integer)
            # なので，数値(整数)に変換する
            data = np.frombuffer(data, dtype=np.int16)
        
        self.sample_frequency = sample_frequency
        self.num_samples = num_samples
        self.data = data

    def plot(self, plt):
        # 横軸(時間軸)を作成する
        time_axis = np.arange(self.num_samples) / self.sample_frequency
        
        # 時間波形のプロット
        plt.plot(time_axis, self.data)

        # プロットのタイトルと、横軸と縦軸のラベルを定義
        plt.title('waveform')
        plt.xlabel('Time [sec]')
        plt.ylabel('Value')

        # 横軸の表示領域を0から波形終了時刻に制限
        plt.xlim([0, self.num_samples / self.sample_frequency])


class Spectrogram:
    def __init__(self, waveform):
        self.waveform = waveform
        self.sample_frequency = waveform.sample_frequency
        self.num_samples = waveform.num_samples
        self.data = _make_spectrogram(waveform)

    def plot(self, plt):
        spectrogram = self.data

        # スペクトログラムの最大値を0に合わせて
        # カラーマップのレンジを調整
        spectrogram -= np.max(spectrogram)
        vmax = np.abs(np.min(spectrogram)) * 0.0
        vmin = - np.abs(np.min(spectrogram)) * 0.7

        # ヒストグラムをプロット
        plt.imshow(spectrogram.T[-1::-1,:],
                extent = [0, self.num_samples / self.sample_frequency, 
                            0, self.sample_frequency / 2],
                cmap = 'gray',
                vmax = vmax,
                vmin = vmin,
                aspect = 'auto')

        # プロットのタイトルと、横軸と縦軸のラベルを定義
        plt.title('spectrogram')
        plt.xlabel('Time [sec]')
        plt.ylabel('Frequency [Hz]')


def _make_spectrogram(waveform):
    # フレームサイズ [ミリ秒]
    frame_size = 25
    # フレームシフト [ミリ秒]
    frame_shift = 10

    # フレームサイズをミリ秒からサンプル数に変換
    frame_size = int(waveform.sample_frequency \
                     * frame_size * 0.001)

    # フレームシフトをミリ秒からサンプル数へ変換
    frame_shift = int(waveform.sample_frequency * frame_shift * 0.001)

    # FFTを行う範囲のサンプル数を，
    # フレームサイズ以上の2のべき乗に設定
    fft_size = 1
    while fft_size < frame_size:
        fft_size *= 2

    # 短時間フーリエ変換をしたときの
    # 総フレーム数を計算する
    num_frames = (waveform.num_samples - frame_size) // frame_shift + 1

    # スペクトログラムの行列を用意
    spectrogram = np.zeros((num_frames, int(fft_size / 2) + 1))

    # 1フレームずつ振幅スペクトルを計算する
    for frame_idx in range(num_frames):
        # 分析の開始位置は，フレーム番号(0始まり)*フレームシフト
        start_index = frame_idx * frame_shift

        # 1フレーム分の波形を抽出
        frame = waveform.data[start_index : \
                              start_index + frame_size].copy()

        # ハミング窓を掛ける
        frame = frame * np.hamming(frame_size)
      
        # 高速フーリエ変換(FFT)を実行
        spectrum = np.fft.fft(frame, n=fft_size)

        # 振幅スペクトルを得る
        absolute = np.abs(spectrum)

        # 振幅スペクトルは左右対称なので，左半分までのみを用いる
        absolute = absolute[:int(fft_size / 2) + 1]

        # 対数を取り、対数振幅スペクトルを計算
        log_absolute = np.log(absolute + 1E-7)

        # 計算結果をスペクトログラムに格納
        spectrogram[frame_idx, :] = log_absolute

    return spectrogram


#
# メイン関数
#
def test_spectrogram(wav_file=None, out_plot=None, no_wave=False):
    if wav_file is None:
        wav_file = '../data/wav/BASIC5000_0001.wav'
        out_plot = './spectrogram.png'

    # wavファイルを開き、以降の処理を行う
    waveform = Waveform(wav_file)

    # 時間波形からスペクトログラムを求める
    spectrogram = Spectrogram(waveform)

    #
    # 時間波形とスペクトログラムをプロット
    #
    if no_wave:
        plt.figure(figsize=(10,4))
        spectrogram.plot(plt)
    else:
        plt.figure(figsize=(10,10))

        plt.subplot(2, 1, 1)
        waveform.plot(plt)

        plt.subplot(2, 1, 2)
        spectrogram.plot(plt)

    # プロットする
    if out_plot is None:
        plt.show()
    else:
        plt.savefig(out_plot)
        plt.clf()
        plt.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='短時間フーリエ変換を用いて音声のスペクトログラムを作成します')
    parser.add_argument('--wav_file', type=pathlib.Path, help='入力wavファイル')
    parser.add_argument('--out', type=pathlib.Path, help='出力先ファイル')
    parser.add_argument('--no_wave', action='store_true', default=False, help='時間波形をプロットしない')
    args = parser.parse_args()

    test_spectrogram(args.wav_file, args.out, args.no_wave)
