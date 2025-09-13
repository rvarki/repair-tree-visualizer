# repair-tree-visualizer

This repository contains code to print the parse tree created by RePair grammars. Currently supported are the grammars created by [RePair](http://www.dcc.uchile.cl/gnavarro/software/repair.tgz) [1], [BigRepair](https://gitlab.com/manzai/bigrepair) [2], and [RLZ-RePair](https://github.com/rvarki/RLZ-RePair) [3]. Currently, working on supporting grammars created by [Recursive RePair](https://github.com/jkim210/Recursive-RePair) [4].

## Install

Ensure that you have graphviz installed and it is present on your system's path.

## How to use

This project contains example grammars for an alpha satellite region created by the aforementioned software.

```
>S67971.1 {alpha satellite DNA, alphoid DNA p4n1/4} [human, Genomic, 171 nt]
CATTCTCAGAAACTTCTTTGTGATGTGTCCATTCAACTCACAGAGTTGAACCTTTCTTTTGATAGAGCAG
TTTTGAAACACTCTTTTTGTAGAATCTGCAAGTGGATATTTGGAGCGCTTTGAGGCCTATGGTGGAAAAG
GAAATATCTTCACATAAAAACTAGACAGAAG
```

### Repair
Can generate the parse tree visualization with the following command:

```
mkdir -p images
python3 visualize.py -s data/repair/alpha_sat.seq.txt.C -r data/repair/alpha_sat.seq.txt.R -o images/repair_parse_tree -e png pdf -p repair
```

### RLZ-RePair
Can generate the parse tree visualization with the following command:
```
mkdir -p images
python3 visualize.py -s data/rlz-repair/alpha_sat.seq.txt.C -r data/rlz-repair/alpha_sat.seq.txt.R -o images/rlz-repair_parse_tree -e png pdf -p rlz-repair
```

### BigRePair
Can generate the parse tree visualization with the following command:
```
mkdir -p images
python3 visualize.py -s data/bigrepair/alpha_sat.seq.txt.C -r data/bigrepair/alpha_sat.seq.txt.R -o images/bigrepair_parse_tree -e png pdf -p bigrepair
```

## Usage
```
usage: visualize.py [-h] -s SEQUENCE -r RULES [-o OUTPUT] [-e EXTENSION [EXTENSION ...]] [-p PROGRAM] [--print_grammar] [--print_sequence] [--no_image]

Print the parse tree of RePair grammars

options:
  -h, --help            show this help message and exit
  -s SEQUENCE, --sequence SEQUENCE
                        Path to the compressed sequence file.
  -r RULES, --rules RULES
                        Path to grammar rule file.
  -o OUTPUT, --output OUTPUT
                        Prefix of output file.
  -e EXTENSION [EXTENSION ...], --extension EXTENSION [EXTENSION ...]
                        One or more image file extensions (e.g., png svg jpg).
  -p PROGRAM, --program PROGRAM
                        Compression program used (repair, rlz-repair, bigrepair, rerepair).
  --print_grammar       If set, print the parsed grammar rules to the console.
  --print_sequence      If set, print the compressed sequence to the console.
  --no_image            If set, do not produce the parse tree image.
```

## References

1. N. J. Larsson and A. Moffat, "Off-line dictionary-based compression," in Proceedings of the IEEE, vol. 88, no. 11, pp. 1722-1732, Nov. 2000, doi: 10.1109/5.892708.

2. Gagie, T., I, T., Manzini, G., Navarro, G., Sakamoto, H., Takabatake, Y. (2019). Rpair: Rescaling RePair with Rsync. In: Brisaboa, N., Puglisi, S. (eds) String Processing and Information Retrieval. SPIRE 2019. Lecture Notes in Computer Science(), vol 11811. Springer, Cham. https://doi.org/10.1007/978-3-030-32686-9_3

3. Efficient Grammar Compression via RLZ-based RePair.
Rahul Varki, Travis Gagie, Christina Boucher
bioRxiv 2025.07.22.666196; doi: https://doi.org/10.1101/2025.07.22.666196

4. Justin Kim, Rahul Varki, Marco Oliva, and Christina Boucher. Re²Pair: Increasing the Scalability of RePair by Decreasing Memory Usage. In 32nd Annual European Symposium on Algorithms (ESA 2024). Leibniz International Proceedings in Informatics (LIPIcs), Volume 308, pp. 78:1-78:15, Schloss Dagstuhl – Leibniz-Zentrum für Informatik (2024) https://doi.org/10.4230/LIPIcs.ESA.2024.78