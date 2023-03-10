all: clean_freq_list sort_freq sort_alpha hftok_learn filter_for_morph_db

clean_freq_list:
	echo "import db_stats as dbs; dbs.clean_freqlist('data/cstenten17_mj2.freqlist'); exit()" | python3

sort_freq: clean_freq_list
	sort -nrk2 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted

sort_alpha: clean_freq_list
	sort -k1 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted_alpha

filter_for_morph_db:
	echo "import db_stats as dbs; import morph_database as md; dbs.filter_freqlist('data/cstenten17_mj2.freqlist.cleaned.sorted_alpha', md.MorphDatabase('data/current.dic', 'data/current.par')); exit()" | python3

hftok_learn:
	python3 hftok/hftoks.py learn hftok/desam.pretok hftok/desam.vocab

clean_dic_file:
	echo "import morph_database as md; md.clean_dic_file('data/current.dic'); exit()" | python3

sort_dic_file: clean_dic_file
	sort -f data/current.dic.cleaned.utf8 > data/current.dic.cleaned.utf8.sorted

clean:
	rm -rf data/cstenten17_mj2.freqlist.cleaned*