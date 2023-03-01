all: sort_freq sort_alpha

sort_freq:
	sort -nrk2 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted

sort_alpha:
	sort -k1 data/cstenten17_mj2.freqlist.cleaned > data/cstenten17_mj2.freqlist.cleaned.sorted.alpha

clean:
	rm -rf data data/data/cstenten17_mj2.freqlist.cleaned.sorted data/cstenten17_mj2.freqlist.cleaned.sorted.alpha