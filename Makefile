all: clean_freq_list sort_freq sort_alpha hftok_learn

clean_freq_list:
	echo "import db_stats as dbs; dbs.clean_freqlist('data/cstenten17_mj2.freqlist'); exit()" | python3

sort_freq: clean_freq_list
	sort -nrk2 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted

sort_alpha: clean_freq_list
	sort -k1 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted_alpha

hftok_learn:
	python3 hftok/hftoks.py learn hftok/desam.pretok > hftok/desam.vocab

clean:
	rm -rf data/cstenten17_mj2.freqlist.cleaned data/cstenten17_mj2.freqlist.cleaned.sorted data/cstenten17_mj2.freqlist.cleaned.sorted.alpha