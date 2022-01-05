import pandas as pd


def parse_bprom_output(bprom_file):
    with open(bprom_file) as f:
        # creates a list of strings of each line from the .txt file
        lines: List[str] = f.readlines()

    return print(lines)

# What do we want from the BPROM output:
# (1) Gene # or name (line 1, between ">" and " -")
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
    parse_bprom_output('C:\\Users\jcham\PycharmProjects\BPROM_to_GFF3_converter\Galaxy327_BPROM_output_concatenated.txt')
