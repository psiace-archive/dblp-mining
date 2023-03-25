import argparse
import pandas as pd
import codecs
import ujson

from lxml import etree

from values import JOURNS_PATH, DATA_PATH, SURVEY_PATH

def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd

def clear_element(element):
    """Free up memory for temporary element tree after processing the element"""
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]

def parse_entity(dblp_path, save_path, start, end, journs):
    results = []
    for _, element in context_iter(dblp_path):
        if element.tag in {"inproceedings", "article"}:
            year = element.find("year")
            if year is not None and year.text is not None:
                year = int(year.text)
                if start <= year <= end:
                    booktitle = element.find("booktitle") if element.tag == "inproceedings" else element.find("journal")
                    if booktitle is not None and booktitle.text in journs:
                        authors = [author.text for author in element.findall("author")]
                        title = element.find("title").text
                        results.append({"title": title, "authors": authors, "year": year, "conference": booktitle.text})
        else:
            continue
        clear_element(element)
    with codecs.open(save_path, mode='w', encoding='utf8', errors='ignore') as f:
            ujson.dump(results, f, indent=4)

def args_parser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("start", type=int, help="The year from which the oldest "
                        "publications to be considered come.")
    argparser.add_argument("end", type=int, help="The year to which the newest "
                        "publications to be considered come.")
    return argparser.parse_args()

def main():
    journs = list(pd.read_csv(JOURNS_PATH, header=None)[0])
    args = args_parser()
    parse_entity(DATA_PATH, SURVEY_PATH, args.start, args.end, journs)

if __name__ == '__main__':
    main()
