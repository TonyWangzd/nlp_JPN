import MeCab
mecab = MeCab.Tagger ("-Ochasen")
sentence = '太郎はこの本を二郎を見た女性に渡した。'
print(mecab.parse(sentence))