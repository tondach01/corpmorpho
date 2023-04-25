all: clean_freq_list sort_freq sort_alpha hftok_learn filter_for_morph_db

clean_freq_list:
	echo "import db_stats as dbs; dbs.clean_freqlist('data/cstenten17_mj2.freqlist'); exit()" | python3

sort_freq: clean_freq_list
	sort -nrk2 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted

sort_alpha: clean_freq_list
	sort -k1 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted_alpha

filter_for_morph_db:
	echo "import db_stats as dbs; dbs.filter_freqlist('data/cstenten17_mj2.freqlist.cleaned.sorted_alpha', 'data/current.dic.cleaned.utf8.sorted.forms'); exit()" | python3

hftok_learn:
	python3 hftok/hftoks.py learn hftok/desam.pretok hftok/desam.vocab

hftok_segment_cstenten: hftok_learn
	cut -f1 data/cstenten17_mj2.freqlist.cleaned.sorted_alpha | hftok/pretokenize | python3 hftok/hftoks.py tokenize hftok/desam.vocab | tr " " "=" | paste - data/cstenten17_mj2.freqlist.cleaned.sorted_alpha > data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.hft

clean_dic_file:
	echo "import morph_database as md; md.clean_dic_file('data/current.dic'); exit()" | python3

sort_dic_file: clean_dic_file
	sort -f data/current.dic.cleaned.utf8 > data/current.dic.cleaned.utf8.sorted

dic_file_all_forms:
	echo "import morph_database as md; md.MorphDatabase('data/current.dic', 'data/current.par').dic_file_all_forms('data/current.dic.cleaned.utf8.sorted'); exit()" | python3
	sort -f --output=data/current.dic.cleaned.utf8.sorted.forms data/current.dic.cleaned.utf8.sorted.forms

dic_file_test_forms: dic_file_all_forms
	echo "import db_stats as dbs; dbs.test_forms(); exit()" | python3
	rm data/current.dic.cleaned.utf8.sorted.forms

substitus_fwl:
	cat desam/prevert_desam | java -jar substitus/substitus-20191210-thesis.jar create-frequency-list > substitus/desam.fwl

substitus_sfwl: substitus_fwl
	grep -E '^[0-9]+[[:space:]][[:alpha:]]+$$' substitus/desam.fwl | java -jar substitus/substitus-20191210-thesis.jar convert-frequency-list > substitus/desam.lfwl
	java -jar substitus/substitus-20191210-thesis.jar segmentize-frequency-list --frequency-list substitus/desam.lfwl > substitus/desam.sfwl

substitus_tok:
	cat substitus/desam.sfwl | java -jar substitus/substitus-20191210-thesis.jar find-tokens > substitus/desam.tok
	cat substitus/desam.tok | java -jar substitus/substitus-20191210-thesis.jar tune-tokens --output-dir ./substitus --output-prefix desam.rtok

substitus_segment_cstenten:
	cut -f1 data/cstenten17_mj2.freqlist.cleaned.sorted_alpha | java -jar substitus/substitus-20191210-thesis.jar segmentize-words --frequency-list substitus/desam.lfwl --output-format binary --frequency-list-limit 22M | tr " " "=" | paste - data/cstenten17_mj2.freqlist.cleaned.sorted_alpha > data/cstenten17_mj2.freqlist.cleaned.sorted_alpha.substitus

substitus_segment_test_lemmas:
	cut -f1 -d: data/current.dic.cleaned.utf8.sorted | java -jar substitus/substitus-20191210-thesis.jar segmentize-words --frequency-list substitus/desam.lfwl --output-format binary --frequency-list-limit 22M | tr " " "=" | paste - data/current.dic.cleaned.utf8.sorted > data/current.dic.cleaned.utf8.sorted.substitus

substitus_segment_test_forms:
	cut -f1 -d: data/current.dic.cleaned.utf8.sorted.forms.filtered | java -jar substitus/substitus-20191210-thesis.jar segmentize-words --frequency-list substitus/desam.lfwl --output-format binary --frequency-list-limit 22M | tr " " "=" | paste - data/current.dic.cleaned.utf8.sorted.forms.filtered > data/current.dic.cleaned.utf8.sorted.forms.filtered.substitus

clean:
	rm -rf data/cstenten17_mj2.freqlist.cleaned*