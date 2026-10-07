# GP2040-CE Python Controller Overlay

`pygame` で接続中のゲームコントローラー入力を読み取り、ボタンの押下状態を画面上に表示する Windows 向けのオーバーレイです。OBS の **ウィンドウキャプチャ**で取り込める 640×360 の表示モードに対応しています。

## 主な機能

- GP2040-CE、XInput、SDL 系のコントローラー入力を表示
- A / B / X / Y、LB / RB、LT / RT、方向キー、LS / RS などに対応
- アナログスティック、ハットスイッチ、トリガー軸も読み取り
- ボタン名を画面上から変更して保存
- 背景画像の選択、位置移動、拡大・縮小
- OBS 向けの 640×360 オーバーレイモード
- 複数コントローラー接続時の選択
- 入力番号を確認できるデバッグ出力
- コントローラー未接続状態からの接続・再接続に対応

## 必要な環境

- Windows
- GP2040-CE などのゲームコントローラー

Python を使ってスクリプトから起動する場合は、次も必要です。

- Python 3.10 以降を推奨
- `pygame`
- ボタン名や背景画像の編集を使う場合は、通常の Python 環境に `tkinter` が含まれていること

> **簡単に使う場合:** 配布フォルダーにはビルド済みの `dist\controller_overlay.exe` を用意しています。`.exe` を使う場合、Python や pygame のインストールは不要です。

## セットアップ

PowerShell またはコマンドプロンプトで、このフォルダーへ移動して `pygame` をインストールします。

```powershell
cd C:\Users\Novem\OneDrive\デスクトップ\controller_overlay
py -m pip install pygame
```

Python が `py` コマンドで起動できない場合は、次の形式を使用してください。

```powershell
python -m pip install pygame
```

## .exe で起動する（Python不要）

Python のインストールやコマンド操作をせずに使う場合は、次のファイルをダブルクリックしてください。

```text
dist\controller_overlay.exe
```

おすすめの手順は次のとおりです。

1. コントローラーを接続する
2. `dist\controller_overlay.exe` をダブルクリックする
3. 表示された一覧から使用するコントローラーを選択する

## 起動方法

### 通常モード

```powershell
py controller_overlay.py
```

通常モードでは、起動時に接続されているコントローラーの一覧が表示されます。使用するコントローラーをクリックして選択してください。

### OBS 用オーバーレイモード

```powershell
py controller_overlay.py --obs
```

このモードでは、ウィンドウサイズが **640×360** になり、コントローラー選択画面を表示せずに最初のコントローラーを使用します。OBS では次のように取り込めます。

1. OBS の「ソース」で「ウィンドウキャプチャ」を追加
2. `GP2040-CE Python Controller Overlay` のウィンドウを選択
3. 必要に応じて「ウィンドウの非表示部分をキャプチャ」などを調整
4. 配信画面上で位置・サイズを調整

### 背景起動モード

```powershell
py controller_overlay.py --background
```

`--background` はコントローラー選択画面を表示せずに起動します。`--obs` と同様に最初のコントローラーを使用し、640×360 の画面を表示します。スタートアップタスクや `pythonw.exe` と組み合わせて起動する場合に利用できます。

### 使用するコントローラーを指定

複数のコントローラーが接続されている場合は、インデックスを指定できます。

```powershell
py controller_overlay.py --obs --controller-index 1
```

インデックスは通常モードの選択画面に表示される `[0]`、`[1]` などの番号です。

### 入力診断モード

```powershell
py controller_overlay.py --debug-input
```

ボタン、軸、ハットスイッチの生の値がコンソールに出力されます。ボタンが正しく反応しない場合の確認に使用してください。

OBS モードと組み合わせることもできます。

```powershell
py controller_overlay.py --obs --debug-input
```

## 画面操作

通常モードでは、次のショートカットを使用できます。

| キー / 操作 | 内容 |
|---|---|
| `F2` | ボタン名変更モードの ON / OFF |
| `F3` | 背景編集モードの ON / OFF |
| `B` | 背景画像を選択 |
| `R` | 背景位置と倍率を初期化 |
| `Esc` | コントローラー選択に戻る、または終了 |
| 左クリック | 編集モード中のボタン名変更、背景編集時のドラッグ開始 |
| マウスドラッグ | 背景画像を移動（背景編集モード中） |
| マウスホイール | 背景画像を拡大 / 縮小（背景編集モード中） |

### ボタン名を変更する

1. 通常モードで `F2` を押す
2. 名前を変更したいボタンをクリック
3. 表示されたダイアログに新しい名前を入力
4. Enter または OK で確定
5. 設定は `gp2040_settings.json` に自動保存されます

### 背景画像を設定する

1. 通常モードで `B` を押す
2. PNG / JPG / JPEG / BMP / WEBP 画像を選択
3. `F3` を押して背景編集モードに切り替える
4. ドラッグで位置を調整し、マウスホイールで倍率を調整
5. `R` を押すと位置と倍率を初期化できます

背景画像は半透明で表示され、コントローラーのボタン状態がその上に描画されます。

## 設定ファイル

設定はスクリプトと同じフォルダーにある `gp2040_settings.json` に保存されます。

```json
{
  "labels": {
    "back": "LS",
    "left": "L",
    "down": "D",
    "right": "R",
    "ls": "M2",
    "lb": "LB",
    "up1": "U",
    "up2": "M1",
    "lt": "LT",
    "x": "X",
    "y": "Y",
    "rb": "RB",
    "a": "A",
    "b": "B",
    "rt": "RT",
    "rs": "RS"
  },
  "bg": "C:/path/to/background.png",
  "bg_x": 0,
  "bg_y": 0,
  "bg_scale": 1.0
}
```

### 設定項目

- `labels`: 各ボタンに表示する文字列
- `bg`: 背景画像の絶対パス。空文字列の場合は背景なし
- `bg_x`: 背景画像の水平方向オフセット
- `bg_y`: 背景画像の垂直方向オフセット
- `bg_scale`: 背景画像の倍率。`0.1` ～ `10.0` の範囲

設定ファイルを直接編集した場合は、次回起動時に反映されます。JSON の書式が壊れている場合は、既定値で起動します。

## 入力マッピングについて

スクリプトは `pygame` / SDL の生のボタン番号と、GP2040・XInput 系の一般的な番号をもとに表示を判定します。また、方向入力は次の複数方式に対応しています。

- ボタン入力
- 左スティックの X / Y 軸
- ハットスイッチ
- トリガー軸（SDL によってアイドル値が `0.0` または `-1.0` の場合に対応）

コントローラーやファームウェアの設定によってはボタン番号が異なるため、表示が合わない場合は `--debug-input` で値を確認し、`controller_overlay.py` の `BUTTON_MAP` を調整してください。

## PyInstaller で実行ファイルを作成

同梱の `controller_overlay.spec` を使って、コンソールを表示しない実行ファイルを作成できます。

```powershell
py -m pip install pyinstaller
pyinstaller controller_overlay.spec
```

ビルド後の実行ファイルは通常、次の場所に作成されます。

```text
dist\controller_overlay.exe
```

`gp2040_settings.json` は実行ファイルと同じフォルダーに置いてください。背景画像を使う場合は、設定ファイルの `bg` に実際の画像パスを指定します。

> 注意: 現在の `.spec` は `console=False` の設定です。入力診断のログを確認したい場合は、Python から `--debug-input` を付けて実行するか、`.spec` のコンソール設定を変更してください。

## トラブルシューティング

### `pygame is required` と表示される

`pygame` がインストールされていません。次を実行してください。

```powershell
py -m pip install pygame
```

### コントローラーが見つからない

- コントローラーを接続してからスクリプトを起動する
- Windows の「ゲーム コントローラーの設定」で認識されているか確認する
- GP2040-CE の USB モードが目的の入力方式になっているか確認する
- 複数のゲームパッド関連ソフトが入力を占有していないか確認する
- `--debug-input` を付けて pygame がデバイスを認識しているか確認する

接続後にコントローラーを抜き差しした場合、スクリプトはデバイス追加・削除イベントを検出して再読み込みします。ただし、認識されない場合は一度再起動してください。

### ボタンが違う場所で点灯する

コントローラーのボタン番号が標準マッピングと異なる可能性があります。

1. `py controller_overlay.py --debug-input` を実行
2. 各ボタンを押して `buttons`、`axes`、`hat` の値を確認
3. `controller_overlay.py` の `BUTTON_MAP` をコントローラーに合わせて変更

### 背景画像が表示されない

- `gp2040_settings.json` の `bg` が正しい絶対パスか確認する
- ファイルが PNG / JPG / JPEG / BMP / WEBP のいずれかであることを確認する
- Windows のパスは JSON 内で `\\` にするか、`/` を使用する
- 例: `C:/Users/Example/Pictures/background.png`

### 日本語が文字化けする

スクリプトは次のフォントを順番に探します。

1. Meiryo
2. Yu Gothic
3. Noto Sans CJK JP
4. Arial

いずれも利用できない場合は pygame の既定フォントを使用します。日本語表示には Meiryo、Yu Gothic、または Noto Sans CJK JP のインストールを推奨します。

## ファイル構成

```text
controller_overlay/
├─ controller_overlay.py       # pygame 製のメインアプリケーション
├─ controller_overlay.spec     # PyInstaller 用ビルド設定
├─ gp2040_settings.json        # ラベル・背景画像・位置・倍率の設定
├─ layout.js                   # 参考用の HTML レイアウト定義
├─ dist/
│  └─ controller_overlay.exe   # Python不要で起動できるビルド済み実行ファイル
└─ README.md                   # このファイル
```

`layout.js` は Python 版のボタン配置と対応する、参考用の Web レイアウト定義です。Python 版の実行には必須ではありません。

## 終了方法

- 通常モード: `Esc` またはウィンドウ右上の閉じるボタン
- `--obs` / `--background` モード: `Esc` またはウィンドウ右上の閉じるボタン

終了時には接続中のジョイスティックを解放し、pygame を終了します。
