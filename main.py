import pandas as pd
import re
from typing import List, Match, Dict, TextIO


def read_bprom_file(bprom_file: TextIO) -> List[str]:
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

    # Removing the empty string '' at element 0 used to make the join
    concat_contents: str = concat_contents[1:]

    # Splits the file into a list of strings on ">"
    features: List[str] = concat_contents.split('>')

    return features


def remove_promoterless_features(features: List[str]) -> List[str]:
    """For each concatenated feature string, removes the element
       if the # of predicted promoters is 0. Call on the concatenated string"""
    cleaned_features = features
    indices_to_delete = []
    for i, feature in enumerate(cleaned_features):
        if "Number of predicted promoters -      0" in cleaned_features[i]:
            indices_to_delete.append(i)
    # Must delete in reverse order, otherwise it changes the list indices after
    # the element deleted, and you delete subsequent elements at i+1, i+2, i+3, etc
    for i in sorted(indices_to_delete, reverse=True):
        del cleaned_features[i]

    return cleaned_features


def extract_accession(feature: str) -> str:
    """Extract accession"""
    accession: Match = re.search('[\w](.*)(?=_)', feature)
    accession: str = accession.group().replace('_', '').strip()

    return accession


def extract_test_seq_position(feature: str) -> str:
    """Extract position in genome. Gets any number of values '(.*)' between the brackets
    using 'lookbehind/lookright' (?<=PATTERN) and 'lookahead/lookleft' regex assertions"""
    # Matches for 'Location=[(.*)]('
    location: Match = re.search('(?<=Location=\\[)(.*)(?=]\\()', feature)
    location: str = location.group().split(':')

    return location


def extract_strand_direction(feature: str) -> str:
    """Extract strand direction for a feature, - or +"""
    # Matches for '(.)'
    direction: Match = re.search('(?<=\\().(?=\\))', feature)
    direction: str = direction.group()

    return direction


def extract_promoter_data(feature: str) -> Dict[str, str]:
    """Extracts all promoter data using regular expressions.
    Use for one element in the output of concatenate_then_split()"""
    # Extract promoter -10 and -35 sequences and scores
    # Gets everything between "-xx box at pos." and " Score"
    minus10: Match = re.search('(?<=-10 box at pos.)(.*)(?= Score)(.*)', feature)
    minus35: Match = re.search('(?<=-35 box at pos.)(.*)(?= Score)(.*)', feature)

    # Extracts the match and removes leading and trailing whitespace (which can be variable)
    # (the bprom output does not maintain the same # of whitespace characters
    # if there are less digits, at least for the scoring)
    minus10: List[str] = minus10.group().lstrip().split(' ')
    minus10_pos: str = minus10[0]
    minus10_seq: str = minus10[1]
    minus10_score: str = minus10[-1]

    minus35: List[str] = minus35.group().lstrip().split(' ')
    minus35_pos: str = minus35[0]
    minus35_seq: str = minus35[1]
    minus35_score: str = minus35[-1]
    promoter_data = {'minus10_pos': minus10_pos,
                     'minus10_seq': minus10_seq,
                     'minus10_score': minus10_score,
                     'minus35_pos': minus35_pos,
                     'minus35_seq': minus35_seq,
                     'minus35_score': minus35_score}
    return promoter_data


def extract_LDF_score(feature: str) -> str:
    """Extract LDF score"""
    LDF = re.search('(?<=LDF-)(.*)', feature)
    LDF = LDF.group().strip()

    return LDF


def extract_promoter_position(feature: str):
    """Extract promoter position (not -10 or -35 box position)"""
    # Get 'Promoter Pos:     X' data
    promoter_pos: Match = re.search('(?<=Promoter Pos:)(.*)(?=LDF)', feature)
    promoter_pos: int = int(promoter_pos.group().strip())

    # Get start and end positions from 'Location=[XXX:YYYY]'
    test_seq_position: List[str] = extract_test_seq_position(feature).split(':')
    test_seq_start: int = int(test_seq_position[0])
    test_seq_end: int = int(test_seq_position[1])

    # Now need to calculate promoter position with respect to the genome
    # Get's -10 position and -35 position
    # -35 position is the START, Promoter Pos is the end?? Or -10 + 10 is the end??

    # IMPORTANT!! Whether or not you add or subtract to calculate the promoter start
    # position depends on whether we're on the + or - strand! Must take into account.
    direction: str = extract_strand_direction(feature)

    if direction == '+':
        # start = test_seq/CDS start + minus35 position
        # end = start + 35
        pass
    elif direction == '-':
        # The workflow Jolene uses is smart enough to correctly pull upstream
        # for both + and - strands (i.e., pulls left for +, pulls right for -)
        # THEREFORE, for a gene with a start at 930 on the + strand, it pulls 830:930
        # And for a gene with a start at 930 on the - strand, it pulls 930:1030
        pass
    else:
        assert "Error: Strand data neither \'+\' nor \'-\'"

    calculated_promoter_pos: List[int] = [
        promoter_pos + test_seq_end,
        promoter_pos + test_seq_start,
                                         ]

    return calculated_promoter_pos


def extract_tf_binding_elements():
    """Extract predicted transcription factor binding elements"""
    return


def extract_data_for_all_features(features: List[str]) -> List[List[str]]:
    """Loops through cleaned bprom output extracting all data of interest"""
    data: List[List[str]] = []
    for feature in features:
        # loop through features, a List[str] containing each feature [str] in the
        # original bprom format as a single string, but cleaned of irrelevant data
        promoter_data = extract_promoter_data(feature)
        location: List[str] = extract_test_seq_position(feature)
        data.append(
            [extract_accession(feature),            # Seqid col
             'bprom',                               # Source col
             'promoter',                            # Type col
             location[0],                           # Start col
             location[1],                           # End col
             extract_strand_direction(feature),
             extract_LDF_score(feature),
             extract_promoter_position(feature),
             promoter_data['minus10_pos'],
             promoter_data['minus10_seq'],
             promoter_data['minus10_score'],
             promoter_data['minus35_pos'],
             promoter_data['minus35_seq'],
             promoter_data['minus35_score'],
             ])

    return data


def convert_to_dataframe(extracted_data: List[List[str]]):
    """Convert extracted data to Pandas dataframe with gff3 columns"""

    df = pd.DataFrame()
    # gff3
    # gff3_columns = Seqid	Source	Type	Start	End	Score	Strand	Phase	Attributes
    # Create Dataframe, then read in data in order to fill the columns.
    # So, for each dictionary in the list of dictionaries, add for each col
    # Col (1) Accession (as Seqid)
    # Col (2) bprom (as Source)
    # Col (3) promoter (but this might be incorrect)
    # Col (4) start and (5) end positions
    # Col (6) LDF Score (Score)
    # Col (7) strand_direction, '+' or '-' (strand)
    # Col (8) phase = '.'
    # Col (9) (attributes)

    return


def write_to_gff3(dataframe):
    """Create a gff3 file by using Pandas to tsv"""
    with open(extracted_data, 'r') as rf:
        return

    return


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
    print(' bprom_file :', bprom_file)
    # print(concatenate_then_split(bprom_file)[0])
    concatenated_bprom_file: List[str] = concatenate_then_split(bprom_file)
    working_file = remove_promoterless_features(concatenated_bprom_file)
    # print(' concat file w/o promoterless features: ', working_file)
    position = extract_test_seq_position(concatenated_bprom_file[0])
    promoters = extract_promoter_data(concatenated_bprom_file[1])
    strand_direction = extract_strand_direction(working_file[2])
    accession = extract_accession(working_file[0])

    # print(remove_promoterless_features(concatenated_bprom_file)[2])
    # print('working_file: ', working_file[0])
    print(' position:', position,
          '\n', '-10 promoter:', promoters['minus10_pos'], promoters['minus10_seq'],
          '\n', '-35 promoter:', promoters['minus35_pos'], promoters['minus35_seq'],
          '\n', 'strand direction: ', strand_direction,
          '\n', 'accession: ', accession,
          )
    print(extract_data_for_all_features(working_file))