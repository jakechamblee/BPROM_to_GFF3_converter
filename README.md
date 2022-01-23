# BPROM to GFF3 converter

Uses regular expressions to extract the data from the output of BPROM 
(a bacterial promoter prediction software tool) and converts it to the GFF3 file format.

### Converts the following input:
![bprom_input](img.png)

### To the following GFF3 output:
![output](img_1.png)

### Run at the command line
```python
python bprom_gff3_converter.py -f bprom_output_file_name/path.txt
```