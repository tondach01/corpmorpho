### How to test segmentator

*Note: Automated testing for substitus will be added soon*

Requirements:

- *data/current.dic* and *data/current.par* files for creating a morphological database
- *desam/desam* and *desam/prevert_desam* files for model training
- provided *Makefile*
- segmented *csTenTen* frequency list
  - if you are at `aurora.fi.muni.cz`, connect to `apollo`, change directory to `\nlp\projekty\corpmorpho\git`, and run ```source init.sh```
  - determine the `segmentator_id`:
    - `sentencepiece_{unigram, bpe}_{vocabulary size}`
    - `morfessor_{max epochs}`
    - `hft`
  - in Python terminal, run:
    ```
    import db_stats
    import guesser
    m = guesser.get_segment_method(segmentator_id)
    db_stats.segment_freq_list("data/cstenten17_mj2.freqlist.cleaned.sorted_alpha", m, segmentator_id) # this creates quite huge file and takes a lot of time
    ```
    
In terminal, run:
  ```
  python3 compare_segmenters.py [-l] [-d] -s segmentator_id
  ```
  - the `-l` switch tests against `data/current.dic.cleaned.utf8.sorted` file containing just lemmas, otherwise `data/current.dic.cleaned.utf8.sorted.forms.filtered` will be used
    - if these files are not present, run:
    ```
    make clean_dic_file
    # for obtaining also .forms.filtered file, run following
    make dic_file_all_forms
    ```
  - the `-d` switch prints the paradigm guessing to standard output, otherwise `logs/log_{segmentator_id}_{lemmas, forms}` is created and written into

To summarize results from logs, run:
  ```
  python3 eval_logs.py
  ```