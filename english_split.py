def segment(text, segs):
    words = []
    last = 0
    for i in range(len(segs)):
        if segs[i] == '1':
            words.append(text[last:i+1])
            last = i+1
    words.append(text[last:])
    return words

if __name__ == "__main__":
    text = "doyouseethekittyseethedoggydoyoulikethekittylikethedoggy"
    seg2 = "0100100100100001001001000010100100010010000100010010000"
    words = segment(text,seg2)
    print(words)

