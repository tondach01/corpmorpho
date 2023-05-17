### Requirements

- for correct work of the program, please respect described directory structure
- `data/current.dic` and `data/current.par` files (owned by third party)
  - these are present on server `aurora.fi.muni.cz` accessible only to members of Faculty of Informatics
  of Masaryk University (FI MU), thus non-members have to gain the access with permission from the
  server administrators and from the code owners
- `data/cstenten17_mj2.freqlist` file (owned by third party)
  - this word list was downloaded via `ske.fi.muni.cz`, service cooperatively operated by FI MU and
  Lexical Computing, s.r.o. - for other interested persons a fee might be required to get the full
  data. For more information, visit [SketchEngine](https://sketchengine.eu).
  - prepare all necessary files
    ```
    make sort_alpha filter_for_morph_db
    ```
- `desam/desam` file (owned by third party)
  - this is present on server `aurora.fi.muni.cz` accessible only to members of Faculty of Informatics
  of Masaryk University (FI MU), thus non-members have to gain the access with permission from the
  server administrators and from the code owners
  -  create pre-vertically formatted corpus:
    ```
    make prevert_desam
    ```
- segmented *csTenTen* frequency list (if you want to test **Substitus**, continue [here](#substitus-testing) )
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
    # this creates quite huge file and takes a lot of time
    db_stats.segment_freq_list("data/cstenten17_mj2.freqlist.cleaned.sorted_alpha", m, segmentator_id)
    ```
    - if you want to use `hft`:
      - clone the [HFT repository](https://github.com/pary42/hftoks) to `hftok` directory
      - run in terminal:
        ```
        make hftok_segment_cstenten
        ```

### How to guess a paradigm

To obtain most probable paradigm for word or whole text file of words, run:
  ```
  python3 guesser.py -h
  ```

and follow the instructions to customize script parameters.
  
Works for Substitus logs as well.

### How to test segmentator
  
- Create `logs` directory if such is not present
- In terminal, run:
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
  python3 eval_logs.py -h
  ```

and follow the instructions to customize script parameters and get the desired evaluation.
  
Works for Substitus logs as well.

#### Substitus testing

For running Substitus, you need to have Java installed and added to PATH (so the terminal can call `java -jar ...`). Then make sure that test files are present, or create them as stated [here](#testing).

- Download the [Substitus binary](https://is.muni.cz/auth/th/l3y56/substitus-20191210-thesis.jar) into `substitus` directory
- To segment all necessary files, run:
  ```
  make substitus_sfwl substitus_segment_cstenten
  # for testing lemmas, run following afterwards
  make substitus_segment_test_lemmas
  # otherwise run
  make substitus_segment_test_forms
  ```
- Continue to [testing](#testing) and use `substitus` as `segmentator_id`.