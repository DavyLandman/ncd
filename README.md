# Normalized Compression Distance

This python script calculates the [Normalize Compression Distance](https://en.wikipedia.org/wiki/Normalized_compression_distance) between all the files passed as argument.
NCD can be used as a distance measure in hierarchical clustering.
Since NCD gets slow quickly, I've at least parallized the calculation over the available cores. If more speed is required, there are publications that discuss an approach on dictionaries.

## Internals

NCD is quite sensitive to the selection of the compressor. Especially for larger
data, gzip is quite a bad choice. (`NCD(a,a) > 0.1`). 
LZMA2 was chosen since it can handle large windows and allows for fine tuned configuration.

After calculating NCD, always analyze the diagonal, if the values are to high,
the compressor might be unsuited for your data.

## Usage

Progress is reported on `stderr` results on `stdout`.

If you pass:

- 1 file: the `Z(a)` is returned
- 2 files: `NCD(a,b)` is returned, without the surrounding table.
- >2 files: a distance matrix is returned, only the lower half of the matrix is
  filled.


```
./ncd.py data/*.csv > results/calculated-ncds.csv
```

Which can then be imported as a distance matrix in R:

```
dst = as.dist(as.matrix(read.csv("results/calculated-ncds.csv", row.names=1)))
```

The progress will be reported every 10 rows. However, since it is a distance matrix, the last row takes n times longer than the first row. More accurate progress calculation is possible, but I haven't yet spend time on that.
