from knitting_parser import KnittingPatternParser

def text_to_json(text, title='自动识别图解'):
    parser = KnittingPatternParser()
    knitting_data = parser.create_knitting_data(title, text)
    return knitting_data.to_dict()

if __name__ == '__main__':
    with open('ocr_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    result = text_to_json(text)
    print(result)