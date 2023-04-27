### How to test segmentator

#### Requirements

- provided `Makefile`
- `data/current.dic`, `data/current.par` and `data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.filtered` files for creating a morphological database
  - if the last one is not present, you can download it from [here](https://nlp.fi.muni.cz/projekty/corpmorpho/) or obtain by running
  ```
  # make sure data/cstenten17_mj2.freqlist.cleaned.sorted_alpha file is present
  make filter_for_morph_db
  ```
- `desam/desam` and `desam/prevert_desam` files for model training
- segmented *csTenTen* frequency list (if you want to test **Substitus**, continue [here](#substitus-testing) )
  - if you are at `aurora.fi.muni.cz`, connect to `apollo`, change directory to `\nlp\projekty\corpmorpho\git`, and run ```source init.sh```
  - if `data/cstenten17_mj2.freqlist.cleaned.sorted_alpha` is not present, you can download it from [here](https://nlp.fi.muni.cz/projekty/corpmorpho/)
  - determine the `segmentator_id`:
    - `sentencepiece_{unigram, bpe}_{vocabulary size}`
    - `morfessor_{max epochs}`
    - `hft`
    - `character` for no segmentator (all possible segmentations are taken into account)
  - in Python terminal, run:
    ```
    import db_stats
    import guesser
    m = guesser.get_segment_method(segmentator_id)
    db_stats.segment_freq_list("data/cstenten17_mj2.freqlist.cleaned.sorted_alpha", m, segmentator_id) # this creates quite huge file and takes a lot of time
    ```
    - if you want to use `hft`, instead run in terminal:
      ```
      make hftok_segment_cstenten
      ```
  
#### Testing
  
In terminal, run:
  ```
  python3 compare_segmenters.py [-l] [-d] -s segmentator_id
  ```
  - the `-l` switch tests against `data/current.dic.cleaned.utf8.sorted` file containing just lemmas, otherwise `data/current.dic.cleaned.utf8.sorted.forms.filtered` will be used (Substitus uses its own test files which are similar, but already segmented)
    - if these files are not present, run:
    ```
    make clean_dic_file
    # for obtaining also .forms.filtered file, run following afterwards
    make dic_file_all_forms
    ```
  - the `-d` switch prints the paradigm guessing to standard output, otherwise `logs/log_{segmentator_id}_{lemmas, forms}` is created and written into

#### Summarizing results

To summarize results from logs, run:
  ```
  python3 eval_logs.py
  ```
  
Works for Substitus logs as well.

#### Substitus testing

For running Substitus, you need to have Java installed and added to PATH (so the terminal can call `java -jar ...`). Then make sure that test files are present, or create them as stated [here](#testing).

To segment all necessary files, run:

```
make substitus_sfwl substitus_segment_cstenten
# for testing lemmas, run following afterwards
make substitus_segment_test_lemmas
# otherwise run
make substitus_segment_test_forms
```

Then, you can continue to [testing](#testing) and use `substitus` as `segmentator_id`.