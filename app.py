import streamlit as st
from ultralytics import YOLO
from PIL import Image

# --- 1. 設定とデータベース ---
# ページ設定
st.set_page_config(page_title="AI料理栄養診断", layout="centered")

# 栄養データベース（サンプル）
# 料理栄養データベース
# 単位: cal(kcal), pro(タンパク質g), fat(脂質g), carbs(炭水化物g)

nutrition_db = {
    'うな重': {'name': 'うな重', 'cal': 750, 'pro': 25.0, 'fat': 18.0, 'carbs': 110.0},
    'おでん': {'name': 'おでん(盛り合わせ)', 'cal': 250, 'pro': 15.0, 'fat': 8.0, 'carbs': 20.0},
    'おにぎり': {'name': 'おにぎり(1個)', 'cal': 180, 'pro': 3.5, 'fat': 0.5, 'carbs': 39.0},
    'お好み焼き': {'name': 'お好み焼き', 'cal': 550, 'pro': 18.0, 'fat': 25.0, 'carbs': 55.0},
    'かけうどん': {'name': 'かけうどん', 'cal': 320, 'pro': 9.0, 'fat': 1.0, 'carbs': 65.0},
    'かつ丼': {'name': 'かつ丼', 'cal': 900, 'pro': 30.0, 'fat': 35.0, 'carbs': 110.0},
    'きんぴらごぼう': {'name': 'きんぴらごぼう(小鉢)', 'cal': 70, 'pro': 1.5, 'fat': 3.0, 'carbs': 9.0},
    'ご飯': {'name': 'ご飯(普通盛り)', 'cal': 250, 'pro': 3.8, 'fat': 0.5, 'carbs': 55.0},
    'さんまの塩焼き': {'name': 'さんまの塩焼き', 'cal': 320, 'pro': 18.0, 'fat': 25.0, 'carbs': 0.5},
    'ざるそば': {'name': 'ざるそば', 'cal': 350, 'pro': 12.0, 'fat': 1.5, 'carbs': 70.0},
    'すき焼き': {'name': 'すき焼き(1人前)', 'cal': 700, 'pro': 25.0, 'fat': 45.0, 'carbs': 40.0},
    'たい焼き': {'name': 'たい焼き', 'cal': 220, 'pro': 5.0, 'fat': 2.0, 'carbs': 45.0},
    'たこ焼き': {'name': 'たこ焼き(8個)', 'cal': 400, 'pro': 15.0, 'fat': 18.0, 'carbs': 45.0},
    'たたき': {'name': 'カツオのたたき', 'cal': 150, 'pro': 25.0, 'fat': 3.0, 'carbs': 1.0},
    'ちらし寿司': {'name': 'ちらし寿司', 'cal': 600, 'pro': 22.0, 'fat': 8.0, 'carbs': 100.0},
    'つけ麵': {'name': 'つけ麵', 'cal': 700, 'pro': 25.0, 'fat': 25.0, 'carbs': 90.0},
    'なすの油味噌': {'name': 'なすの油味噌', 'cal': 200, 'pro': 3.0, 'fat': 15.0, 'carbs': 12.0},
    'ほうれん草炒め': {'name': 'ほうれん草ソテー', 'cal': 100, 'pro': 3.0, 'fat': 8.0, 'carbs': 3.0},
    'ウィンナーのソテー': {'name': 'ウィンナーソテー', 'cal': 280, 'pro': 10.0, 'fat': 25.0, 'carbs': 2.0},
    'エビフライ': {'name': 'エビフライ(3本)', 'cal': 350, 'pro': 18.0, 'fat': 22.0, 'carbs': 15.0},
    'オムライス': {'name': 'オムライス', 'cal': 750, 'pro': 18.0, 'fat': 25.0, 'carbs': 100.0},
    'オムレツ': {'name': 'オムレツ', 'cal': 250, 'pro': 12.0, 'fat': 18.0, 'carbs': 5.0},
    'カツカレー': {'name': 'カツカレー', 'cal': 1100, 'pro': 30.0, 'fat': 45.0, 'carbs': 130.0},
    'カレーライス': {'name': 'カレーライス', 'cal': 750, 'pro': 15.0, 'fat': 25.0, 'carbs': 105.0},
    'クロワッサン': {'name': 'クロワッサン', 'cal': 200, 'pro': 3.5, 'fat': 10.0, 'carbs': 20.0},
    'グラタン': {'name': 'グラタン', 'cal': 500, 'pro': 18.0, 'fat': 25.0, 'carbs': 45.0},
    'グリーンサラダ': {'name': 'グリーンサラダ', 'cal': 80, 'pro': 2.0, 'fat': 5.0, 'carbs': 5.0},
    'コロッケ': {'name': 'コロッケ(1個)', 'cal': 180, 'pro': 3.0, 'fat': 10.0, 'carbs': 18.0},
    'コーンスープ': {'name': 'コーンスープ', 'cal': 150, 'pro': 3.0, 'fat': 8.0, 'carbs': 15.0},
    'ゴーヤチャンプル': {'name': 'ゴーヤチャンプル', 'cal': 350, 'pro': 18.0, 'fat': 25.0, 'carbs': 8.0},
    'サンドウィッチ': {'name': 'ミックスサンド', 'cal': 350, 'pro': 12.0, 'fat': 18.0, 'carbs': 30.0},
    'シチュー': {'name': 'クリームシチュー', 'cal': 400, 'pro': 15.0, 'fat': 20.0, 'carbs': 30.0},
    'シュウマイ': {'name': 'シュウマイ(5個)', 'cal': 300, 'pro': 12.0, 'fat': 18.0, 'carbs': 20.0},
    'スパゲティ': {'name': 'スパゲティ(麺のみ)', 'cal': 380, 'pro': 13.0, 'fat': 2.0, 'carbs': 75.0},
    'スパゲティーミートソース': {'name': 'ミートソースパスタ', 'cal': 650, 'pro': 22.0, 'fat': 20.0, 'carbs': 85.0},
    'チキンライス': {'name': 'チキンライス', 'cal': 550, 'pro': 15.0, 'fat': 15.0, 'carbs': 80.0},
    'チャンジャオロース': {'name': 'チンジャオロース', 'cal': 350, 'pro': 15.0, 'fat': 25.0, 'carbs': 10.0},
    'チャーシュー麺': {'name': 'チャーシュー麺', 'cal': 700, 'pro': 28.0, 'fat': 25.0, 'carbs': 70.0},
    'チャーハン': {'name': 'チャーハン', 'cal': 650, 'pro': 15.0, 'fat': 20.0, 'carbs': 90.0},
    'トースト': {'name': 'トースト(バター)', 'cal': 220, 'pro': 6.0, 'fat': 8.0, 'carbs': 30.0},
    'ハンバーガー': {'name': 'ハンバーガー', 'cal': 350, 'pro': 13.0, 'fat': 15.0, 'carbs': 35.0},
    'ハンバーグ': {'name': 'ハンバーグ(単品)', 'cal': 450, 'pro': 22.0, 'fat': 30.0, 'carbs': 15.0},
    'ビビンバ': {'name': 'ビビンバ', 'cal': 650, 'pro': 20.0, 'fat': 20.0, 'carbs': 90.0},
    'ビーフステーキ': {'name': 'ビーフステーキ(200g)', 'cal': 600, 'pro': 35.0, 'fat': 45.0, 'carbs': 1.0},
    'ピザ': {'name': 'ピザ(1人前)', 'cal': 700, 'pro': 25.0, 'fat': 30.0, 'carbs': 80.0},
    'ピザトースト': {'name': 'ピザトースト', 'cal': 350, 'pro': 12.0, 'fat': 15.0, 'carbs': 35.0},
    'ピラフ': {'name': 'ピラフ', 'cal': 600, 'pro': 12.0, 'fat': 18.0, 'carbs': 85.0},
    'フライドポテト': {'name': 'フライドポテト(M)', 'cal': 350, 'pro': 4.0, 'fat': 17.0, 'carbs': 45.0},
    'ホットドック': {'name': 'ホットドック', 'cal': 350, 'pro': 12.0, 'fat': 18.0, 'carbs': 30.0},
    'ポテトサラダ': {'name': 'ポテトサラダ(小鉢)', 'cal': 150, 'pro': 2.0, 'fat': 10.0, 'carbs': 12.0},
    'マカロニサラダ': {'name': 'マカロニサラダ', 'cal': 200, 'pro': 4.0, 'fat': 12.0, 'carbs': 18.0},
    'ラーメン': {'name': 'ラーメン(醤油)', 'cal': 500, 'pro': 20.0, 'fat': 10.0, 'carbs': 70.0},
    'ローストビーフ': {'name': 'ローストビーフ', 'cal': 250, 'pro': 25.0, 'fat': 15.0, 'carbs': 1.0},
    'ロールキャベツ': {'name': 'ロールキャベツ(2個)', 'cal': 250, 'pro': 12.0, 'fat': 10.0, 'carbs': 15.0},
    'ロールパン': {'name': 'ロールパン(1個)', 'cal': 100, 'pro': 3.0, 'fat': 2.0, 'carbs': 18.0},
    '冷やし中華': {'name': '冷やし中華', 'cal': 500, 'pro': 18.0, 'fat': 12.0, 'carbs': 75.0},
    '刺身': {'name': '刺身盛り合わせ', 'cal': 200, 'pro': 35.0, 'fat': 5.0, 'carbs': 1.0},
    '卵焼き': {'name': '卵焼き(2切)', 'cal': 150, 'pro': 8.0, 'fat': 10.0, 'carbs': 5.0},
    '味噌汁': {'name': '味噌汁', 'cal': 50, 'pro': 3.0, 'fat': 1.0, 'carbs': 6.0},
    '天ぷら盛り合わせ': {'name': '天ぷら盛り合わせ', 'cal': 500, 'pro': 15.0, 'fat': 30.0, 'carbs': 35.0},
    '天丼': {'name': '天丼', 'cal': 800, 'pro': 18.0, 'fat': 30.0, 'carbs': 100.0},
    '天津飯': {'name': '天津飯', 'cal': 700, 'pro': 15.0, 'fat': 25.0, 'carbs': 95.0},
    '寿司': {'name': '寿司(1人前)', 'cal': 600, 'pro': 25.0, 'fat': 5.0, 'carbs': 100.0},
    '干物': {'name': 'アジの開き', 'cal': 180, 'pro': 25.0, 'fat': 8.0, 'carbs': 0.5},
    '惣菜パン': {'name': '惣菜パン', 'cal': 350, 'pro': 10.0, 'fat': 15.0, 'carbs': 40.0},
    '春巻き': {'name': '春巻き(2本)', 'cal': 300, 'pro': 8.0, 'fat': 20.0, 'carbs': 20.0},
    '海鮮丼': {'name': '海鮮丼', 'cal': 700, 'pro': 30.0, 'fat': 10.0, 'carbs': 105.0},
    '炊き込みご飯': {'name': '炊き込みご飯', 'cal': 350, 'pro': 8.0, 'fat': 3.0, 'carbs': 65.0},
    '焼きそば': {'name': 'ソース焼きそば', 'cal': 550, 'pro': 15.0, 'fat': 20.0, 'carbs': 70.0},
    '焼き鳥': {'name': '焼き鳥(3本)', 'cal': 300, 'pro': 30.0, 'fat': 15.0, 'carbs': 8.0},
    '煮魚': {'name': '煮魚(カレイなど)', 'cal': 250, 'pro': 20.0, 'fat': 10.0, 'carbs': 10.0},
    '牛丼': {'name': '牛丼(並)', 'cal': 700, 'pro': 20.0, 'fat': 25.0, 'carbs': 95.0},
    '目玉焼き': {'name': '目玉焼き(卵1個)', 'cal': 100, 'pro': 7.0, 'fat': 8.0, 'carbs': 0.5},
    '筑前煮': {'name': '筑前煮', 'cal': 200, 'pro': 10.0, 'fat': 8.0, 'carbs': 18.0},
    '納豆': {'name': '納豆(1パック)', 'cal': 100, 'pro': 8.0, 'fat': 5.0, 'carbs': 6.0},
    '肉じゃが': {'name': '肉じゃが', 'cal': 400, 'pro': 12.0, 'fat': 20.0, 'carbs': 40.0},
    '親子丼': {'name': '親子丼', 'cal': 700, 'pro': 25.0, 'fat': 15.0, 'carbs': 100.0},
    '角煮': {'name': '豚の角煮', 'cal': 500, 'pro': 20.0, 'fat': 40.0, 'carbs': 10.0},
    '豚カツ': {'name': '豚カツ(単品)', 'cal': 600, 'pro': 25.0, 'fat': 45.0, 'carbs': 15.0},
    '豚肉の生姜焼き': {'name': '豚の生姜焼き', 'cal': 400, 'pro': 20.0, 'fat': 28.0, 'carbs': 10.0},
    '酢豚': {'name': '酢豚', 'cal': 450, 'pro': 15.0, 'fat': 25.0, 'carbs': 35.0},
    '野菜炒め': {'name': '野菜炒め', 'cal': 300, 'pro': 10.0, 'fat': 20.0, 'carbs': 15.0},
    '餃子': {'name': '餃子(6個)', 'cal': 350, 'pro': 10.0, 'fat': 18.0, 'carbs': 30.0},
    '魚のフライ': {'name': '白身魚のフライ', 'cal': 300, 'pro': 15.0, 'fat': 18.0, 'carbs': 15.0},
    '魚の照り焼き': {'name': 'ブリの照り焼き', 'cal': 250, 'pro': 20.0, 'fat': 15.0, 'carbs': 8.0},
    '鮭のムニエル': {'name': '鮭のムニエル', 'cal': 300, 'pro': 20.0, 'fat': 20.0, 'carbs': 10.0},
    '鮭の塩焼き': {'name': '鮭の塩焼き', 'cal': 200, 'pro': 22.0, 'fat': 12.0, 'carbs': 0.5},
    '鶏の唐揚': {'name': '鶏の唐揚げ(5個)', 'cal': 450, 'pro': 25.0, 'fat': 30.0, 'carbs': 15.0},
    '麻婆豆腐': {'name': '麻婆豆腐', 'cal': 350, 'pro': 15.0, 'fat': 25.0, 'carbs': 10.0},
}
# --- 2. アプリのメイン画面 ---
st.title("🥗 AI料理栄養診断アプリ")
st.write("料理の写真をアップロードすると、カロリーと栄養素を計算します。")

# 画像アップロード
uploaded_file = st.file_uploader("写真をアップロード", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption='アップロードされた画像', use_column_width=True)

    # --- 3. 推論実行 ---
    # ボタンが押されたら解析開始
    if st.button("栄養を診断する"):
        with st.spinner("AIが料理を分析中..."):
            try:
                # モデルの読み込み（同じフォルダにある best.pt を探す）
                model = YOLO('best.pt')
                results = model.predict(image)

                # 集計用変数
                total_cal = 0
                detected_list = []

                # 結果の解析
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = r.names[cls_id]

                        # データベースにあるか確認
                        if cls_name in nutrition_db:
                            data = nutrition_db[cls_name]
                            detected_list.append(data)
                            total_cal += data['cal']
                        else:
                            st.warning(f"「{cls_name}」を検出しましたが、栄養データが未登録です。")

                # --- 4. 結果表示 ---
                if detected_list:
                    st.success(f"合計カロリー: {total_cal} kcal")

                    # 詳細テーブルの表示
                    st.subheader("検出された料理内訳")
                    for item in detected_list:
                        st.write(f"✅ **{item['name']}**")
                        st.write(f"   - カロリー: {item['cal']} kcal / タンパク質: {item['pro']}g / 脂質: {item['fat']}g")
                else:
                    st.error("料理を検出できませんでした。別の写真を試してください。")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.info("ヒント: 'best.pt' モデルファイルが同じ場所にアップロードされているか確認してください。")
