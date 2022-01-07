import pandas as pd
import re
import regex
from typing import List, Match


def parse_bprom_output():
    return


def read_bprom_file(bprom_file) -> List[str]:
    """Creates list of strings, with each element containing a line from the file"""
    contents: List[str] = []

    with open(bprom_file) as file:
        # creates a list of strings of each line from the .txt file
        # Reads in one line at a time so it can handle very large files
        for line in file:
            contents.append(line)

    return contents


def concatenate_then_split(contents: List[str]) -> List[str]:
    """Concatenates the file into one large string.
       Then splits it on '>' so that each feature's data is together in one element"""
    # Concatenates the entire file into one large string
    concat_contents: str = ''.join(contents)

    # Removing the empty string '' at element 0
    concat_contents: str = concat_contents[1:]

    # Splits the file into a list of strings on ">"
    features: List[str] = concat_contents.split('>')

    return features


def extract_accession(feature: str):
    """Extract position in genome. Gets any number of values '(.*)' between the brackets
    using 'lookbehind/lookright' (?<=) and 'lookahead/lookleft' regex assertions"""
    location: Match = re.search('(?<=Location\=\[)(.*)(?=\]\(.\)\])', feature)

    return location


def extract_data_for_feature(feature: str):
    """Extracts all data from an element using regular expressions.
    Use for one element in the output of concatenate_then_split()"""
    # These regexes need to match all EXCEPT whitespaces in many cases b/c otherwise
    # they may match 2 digit but not 3 digit scores "  100" but not "   10" b/c
    # the bprom output does not maintain the same # of whitespace characters
    # if there are less digits (at least for the scoring)

    feature_data = {}
    # Extract accession
    # accession = re.search('')

    # Extract promoter -10 and -35 sequences and scores
    # Gets everything between "-xx box at pos." and " Score"
    minus10: Match = re.search('(?<=-10 box at pos\.)(.*)(?= Score)', feature)
    minus35: Match = re.search('(?<=-35 box at pos\.)(.*)(?= Score)', feature)

    # noinspection PyBroadException
    try:
        # Strip leading whitespace (which can be variable depending on # of digits)
        minus10: str = minus10.group().lstrip()
        minus35: str = minus35.group().lstrip()
    except:
        None


    # Extract predicted transcription factor binding elements

    return minus10, minus35,


# def get_section_indexes(contents: List[str]) -> List[str]:
#     """Gets the starting indexes of each '>' separated section"""
#     feature_indexes = []
#     for i, line in enumerate(contents):
#         # Want to figure out the windows in the list for each section, so
#         if line.startswith(">"):
#             feature_indexes.append(i)
#
#     return feature_indexes


def split_bprom(contents: List[str], feature_indexes: List[str]):
    """Split the BPROM contents by each feature"""
    # test = [contents.split() for content in contents]

    return None


# One way to do this is to take this list of strings of lines and loop through it
# For each element, check for certain characters such as ">",
# " Number of predicted promoters -" , etc.
# If found, then get element[position_of_desired_piece_of_data]
# Problem with this approach is that it will break if BPROM's output format changes

# Better approach would be to make a list of lists separated by the text in
# each section in-between the ">".

# Alternative approaches?


# What do we want from the BPROM output:
# (1) Location/Pos, so what's in brackets [] on the line starting with >
# (2) LDF score, so after "LDF-  "
# (3) Promoter pos, so the number after "Promoter Pos:     "
# (4) -10 box pos and nucleotide sequence and score
# (5) -35 box pos and nucleotide sequence and score
# (6) Get all predicted binding genes

# What we need from the BPROM output:
# (1) Accession # of the genome for Col 1
# (2) Strand of each feature for Col 2
# (3) The position of the promoter features **with respect to the genome**

# GFF3 is a tab delimited text file format, so ultimately need to get relevant data into
# a tab delimited format


# Col 1 Sequence ID (this would be the accession # for the genome. Would need to get this
# from before this step, as it is not present in the BPROM output)
# Col 2 Source = BPROM for all as this is a BPROM output -> GFF3 converter
# Col 3 Feature Type = "promoter"
# Col 4 Start ONE BASE OFFSET (+1)
# Col 5 End ONE BASE OFFSET (+1)
# Col 6 Score (Confidence score of the source for the annotation - put BPROM scores here)
# Col 7 Strand ("+" or "-")
# Col 8 Phase = "." because 0, 1, 2 for CDS, "." for everything else
# Col 9 Attributes (can shove all the extra information in here possibly)

if __name__ == '__main__':
    bprom_file = read_bprom_file('BPROM_output.txt')
    print(bprom_file)
    #print(concatenate_then_split(bprom_file)[0])
    accession = extract_accession(bprom_file[0])
    concatenated_bprom_file = concatenate_then_split(bprom_file)
    promoters = extract_data_for_feature(concatenated_bprom_file[0])

    print(' location:', accession.group(),
          '\n', '-10 promoter:', promoters[0],
          '\n', '-35 promoter:', promoters[1],
          )
