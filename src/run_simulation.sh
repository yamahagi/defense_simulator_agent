# 実行するユニットのディレクトリ
UNIT_DIR="results/enemy_units"

# すべての *.py ファイルに対してループ
for filepath in "$UNIT_DIR"/*.py; do
    # 拡張子なしファイル名取得（例：天空の盾）
    filename=$(basename "$filepath" .py)

    echo "🚀 Running simulation for: $filename"
    
    # Python runner を呼び出し
    python src/run_simulation_template.py "$filename"
done