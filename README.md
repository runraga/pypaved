# PAVED (Python)

### Short description

Python-based version of the PAVED (Positional Averaging for Visualising Exchange Data) app for processing hydrogen-deuterium exchange-mass spectrometry (HX-MS) data. 

### Languages used

- Python

### Overview

See [DOI:10.1007/s13361-018-2067-y](https://pubs.acs.org/doi/abs/10.1007/s13361-018-2067-y) for the original publication behind the development of this software and more information on the technique used to acquire the data.

The idea behind this app was developed in my previous role for taking large data sets from advanced structural biology anlyses and developing an informative but high-level overview of the dataset. These can be used for presenting data easily to less experienced audiences or as a preliminary look at the data before delving deeper in to the underlying raw data. It makes use of all data present in the data set in an unbiased way. The result is a series of plots for different time points that show differences between different treatment states. When one state is chosen as the reference, the data is plotted relative to this and other states that show a significant difference for each position in the protein being analysed are indicated on the plot.

The software was originally written in Java and made use of R libraries for the stats calculations but this was problematic to install and get working. Following the Northcoders bootcamp course I decided to rewrite the basic functionality of the app using Python to enable the use of Pandas dataframes for more efficient handling and manipulation of the data.

### Knowledge gains
- Working with and gaining a better understanding of Pandas dataframes
- Statistical calculations in Python and specifically dataframes
- Graphical user interfaces with TKinter and CustomTKinter
- Threading and multiprocessing

### Future Features

- Peptide coverage map
- Show up take plots for peptides at each position
- Bootstrapping to check ANOVA and Tukey assumptions
- Kruskal-Wallis test for cases of small sample observation, n
