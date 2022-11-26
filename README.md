# Stable Diffusion Bot UI

## 使い方

1. `/generate` コマンドに必要情報ぶちこむ
2. Enterターン
3. ででーん

## 環境構築ガイド

(Windowsの場合)

1. Stable Diffusion web UIを入れる
2. `models/Stable-Diffusion`にモデルを入れる(名前はわかりやすいように変更しよう)
3. `webui-user.bat`を開いて`set COMMANDLINE_ARGS=`の行を`set COMMANDLINE_ARGS=--api --precision full --no-half --opt-split-attention --medvram`に書き換える
4. ボットのディレクトリを開いて`py -3 -m pip install -r requirements.txt`を実行する
5. `.env.sample`を`.env`にリネームし、それぞれトークンとサーバーのURL(Stable Diffusion web UIを起動したら表示されるやつ)を書き込む
6. Stable Diffusion web UIを起動してから`py main.py`を実行でボットが起動するよ！

## 注意

- R18フィルタが有効化されてないので気をつけないと悲惨なことになるよ
- 同時に処理できる数を制限してないのでスパムされるとサーバー死ぬかもよ(やばそうだったら直す)
