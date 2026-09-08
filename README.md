<p align="center">
  <img src="docs/logo.png" alt="sgRNAtor" width="320">
</p>

# sgRNAtor

**Identification and quantification pipeline for subgenomic RNAs (sgRNAs).**

SARS-CoV-2 can undergo discontinuous transcription of it's RNA genome. The
polyermase pauses at a transcription-regulatory sequence (TRS-B) upstream of a
body ORF, jumps to the homologous leader TRS (TRS-L) at the 5' end of the
genome, resulting in a disjointed, subgenomic RNA template that is transcribed
and subsequently translated.

SgRNAtor exploits the presence of the TRS-L sequence to identify sgRNA in viral
sequencing data. It finds reads whose 5' end matches the leader, trims
the leader off, aligns what remains to the viral genome, and treats the
alignment start of each leader-bearing fragment as a template-switching site
(TSS). Those sites are then assigned to annotated ORF junctions to produce
per-ORF and per-junction count tables.

---

## Workflow

<p align="center">
  <img src="docs/workflow.png" alt="sgRNAtor workflow" width="620">
</p>

1. **Adapter trimming** (`prepro.py`) — reads are streamed through an HTStream
   pipe: `hts_Stats` → `hts_LengthFilter` (drops reads < 15 bp) →
   `hts_AdapterTrimmer`. Handles SE or PE input.
2. **Leader search & trim** (`search.py`) — each read (and its reverse
   complement, since libraries are treated as unstranded) is searched against
   every leader sequence in the leader FASTA. Two match modes are considered,
   and each uses a **different algorithm**:

   - **Full leader anywhere in the read** — `_myers_search`, the Myers (1999)
     bit-vector algorithm. One O(len(read)) pass, with the DP column packed into
     a single machine word, finds the 5'-most position where the complete leader
     aligns with Levenshtein distance ≤ `--max-edit`. Machine word caps leaders
     at **64 bp**.

   - **Partial 5' overlap** — `_suffix_prefix_overlap`, an explicit two-row
     **Levenshtein DP**. This is the read that *begins inside* the leader, where
     only a leader suffix of ≥ `--min-match` bases is present. Bit-parallel Myers
     can't express that asymmetric free-prefix/anchored-start geometry, so this
     more traditional edit distances are necessary here.

   `__myers_leader_search` runs both and merges the results: the 5'-most match
   wins, and ties go to the full-leader hit. 

   Matching reads are trimmed through the end of the leader and tagged
   `ls:i:{0,1}` (the flag records whether the match was found on the reverse
   complement). Only leader-bearing fragments are written out.
3. **Alignment** (`align.py`) — `bwa mem -C` (carries the `ls` comment through
   into the BAM) piped into `samtools view -b`.
4. **Quantification** (`quantify.py`) — For each fragment, the 3'-most alignment 
   start among its leader-tagged reads becomes the template-switching site. 
   Sites are counted, then assigned to an ORF if they fall within `± --tss-window` bp 
   of a junction in the TSS BED file. Assigned sites are counted as **canonical**, 
   unassigned sites as **noncanonical**. However, these can harbor many false positives
   given the overal prevelance of "leader-like" motifs in the genome.
5. **Reporting** (`stats.py`) — writes counts, CPMs, per-read assignments, and a
   run summary.

---

## Input data

sgRNAtor is built for **short-read (Illumina) RNA-seq or amplicon sequencing**, 
with reference files for the virus of interest.

| Input | Flag | Description |
| --- | --- | --- |
| FASTQ | positional | R1 (or SE) reads, and optionally R2. Plain or gzipped — detected automatically. |
| Reference FASTA | `-R/--reference` | Viral genome, BWA-indexed. sgRNAtor checks for `.amb/.ann/.bwt/.pac/.sa` before doing any work and tells you the `bwa index` command if they are missing. *Defaults to the bundled SARS-CoV-2 genome, which ships pre-indexed.* |
| Leader FASTA | `-L/--leader-fasta` | Multi-FASTA of leader / TRS-L sequences. Each sequence must be **≤ 64 bp** (the bit-vector matcher uses a single machine word). Multiple variants can be supplied; the first one that matches a read is used. *Defaults to the bundled TRS-L sequences.* |
| TSS BED | `-b/--tss-bed` | Known template-switching sites. Tab-separated `chrom  start  end  name`; `start` (0-based) is the junction position and `name` is the ORF label. Duplicate start positions are rejected. *Defaults to the bundled 12 junctions.* |

Reference files for SARS-CoV-2 (Wuhan-Hu-1 / `MN908947.3`) are **bundled inside
the package** and are used automatically when `-R`, `-L`, and `-b` are omitted:

```
src/sgRNAtor/data/nCoV-2019.reference.fasta              # genome            -> default -R
src/sgRNAtor/data/leader_seq.fasta                       # 2 leader variants -> default -L
src/sgRNAtor/data/sgRNA_template_switch_sites.bed        # 12 junctions      -> default -b
src/sgRNAtor/data/nCoV-2019.reference.fasta.{amb,ann,bwt,pac,sa}  # pre-built BWA index
src/sgRNAtor/data/GCF_009858895.2_ASM985889v3_genomic.gtf  # annotation only; not read by the pipeline
```

They install alongside the code, so the defaults resolve from any working
directory. The BWA index ships too (64 KB, built with bwa 0.7.19), so a
SARS-CoV-2 run needs no reference setup at all:

```bash
sgRNAtor --threads 12 -o out/sample sample_1.fq.gz sample_2.fq.gz
```

The FASTA and BED both use `MN908947.3`; the GTF is the RefSeq copy of the same
29,903 bp genome under `NC_045512.2`. Coordinates are interchangeable, but
nothing in `src/` reads the GTF.

`sgRNA_template_switch_sites.bed`:

```
MN908947.3	67	68	genomic
MN908947.3	21553	21554	S
MN908947.3	25382	25383	orf3
...
```

---

## Installation

**1. Install conda** (miniconda or miniforge).

**2. Create the environment.** This installs the external binaries the pipeline
shells out to — `bwa`, `samtools`, and `htstream` — alongside the Python
dependencies.

```bash
conda env create -f environment.yml
```

**3. Activate it.**

```bash
conda activate sgRNAtor
```

**4. Install the package** from the directory containing `setup.py`.

```bash
pip install .
```

`setup.py` checks `PATH` for `bwa`, `samtools`, `bbduk.sh`, and `htstream` and
warns (but does not fail) if any are missing. Expect a warning about `bbduk.sh`:
`environment.yml` deliberately omits bbmap, which is only needed by
`scripts/paper_implementation.sh`, not by the pipeline itself.

**5. Verify.**

```bash
sgRNAtor --help
```

Requires **Python ≥ 3.12** — `stats.py` and `search.py` use PEP 701 f-strings
(nested same-type quotes, e.g. `f"{orf["ORF"]}"`), which are a `SyntaxError` on
3.11 and below. `environment.yml` pins `python=3.12` and `setup.py` enforces
`python_requires=">=3.12"`.

---

## Usage

```
usage: sgRNAtor [-h] [--reference REFERENCE] [--leader-fasta LEADER_FASTA] [--tss-bed TSS_BED]
                [--threads THREADS] [--min-match MIN_MATCH] [--max-edit MAX_EDIT]
                [--tss-window TSS_WINDOW] [--output-prefix OUTPUT_PREFIX]
                fastq [fastq2]

Identification and Quantification pipeline for sgRNA. Performs leader sequence matching and
trimming, alignment with BWA, and generates sgRNA counts tables.

positional arguments:
  fastq                 Path to the input fastq file (R1 or SE)
  fastq2                Path to optional Read 2 fastq file

options:
  -h, --help            show this help message and exit
  --reference REFERENCE, -R REFERENCE
                        Path to genome reference fasta file. (default: bundled SARS-CoV-2
                        MN908947.3, ships pre-indexed)
  --leader-fasta LEADER_FASTA, -L LEADER_FASTA
                        Path to leader sequence multi fasta file. All sequences should be no
                        greater than 64 bp long. (default: bundled SARS-CoV-2 TRS-L sequences)
  --tss-bed TSS_BED, -b TSS_BED
                        Path to sgRNA template switching sites bed file. (default: bundled SARS-
                        CoV-2 junctions)
  --threads THREADS, -t THREADS
                        Number of threads to use (default: 1)
  --min-match MIN_MATCH, -m MIN_MATCH
                        Minimum length of substring to match (default: 12)
  --max-edit MAX_EDIT, -e MAX_EDIT
                        Maximum edit distance for a leader sequence match (default: 2)
  --tss-window TSS_WINDOW, -w TSS_WINDOW
                        Window size for template switching sites (+/- specified number). (default:
                        10)
  --output-prefix OUTPUT_PREFIX, -o OUTPUT_PREFIX
                        Prefix for output files.
```

### Example

For SARS-CoV-2 the bundled references and index are used automatically:

```bash
sgRNAtor --threads 12 --output-prefix 01-sgRNAQuant/SRR31567433 \
         SRR31567433_1.fq.gz SRR31567433_2.fq.gz
```

Spelling every reference out explicitly:

```bash
sgRNAtor --reference    my_virus.fasta \
         --leader-fasta my_leaders.fasta \
         --tss-bed      my_junctions.bed \
         --threads      12 \
         --min-match    10 \
         --max-edit     2 \
         --tss-window   10 \
         --output-prefix 01-sgRNAQuant/sample \
         sample_1.fq.gz sample_2.fq.gz
```

`scripts/basic_sgRNAtor_usage.sh` is the same call as a template — edit the
paths first, as it expects reads in `00-RawData/` and references in
`References/` rather than `data/`. `scripts/paper_implementation.sh` is the SGE
array-job version used to reproduce the published bbduk/bbmap approach for
comparison; it hardcodes BU SCC paths and needs bbmap, so it is a record of that
run rather than something to launch unedited.

### Tuning

- `--min-match` is the shortest leader suffix accepted for a read that starts
  inside the leader. Lower it for short reads or heavily fragmented libraries;
  raising it reduces spurious hits.
- `--max-edit` is the Levenshtein budget (substitutions **and** indels) for a
  leader match. `2` tolerates sequencing error and leader variation; `0` is
  exact.
- `--tss-window` widens the ± window around each BED junction. Template
  switching is imprecise, so a small window (10 bp) captures the real spread
  without merging adjacent ORFs. The closest pair in the shipped BED is `N`
  (28257) and `orf9b` (28280), 23 bp apart, so windows begin to overlap at
  `-w 12`; on a tie the first matching BED line wins. `-w 0` matches the
  junction base exactly.

---

## Using your own reference

The bundled SARS-CoV-2 files are only defaults. Any virus, a different
SARS-CoV-2 assembly, or a custom junction set — works by supplying the three
reference inputs yourself. Nothing else in the pipeline is virus-specific.

**1. Genome FASTA, indexed.** One record per replicon. Index it once:

```bash
bwa index my_virus.fasta
```

**2. Leader FASTA.** The TRS-L sequence(s) fused onto every sgRNA body, as a
multi-FASTA. Each record must be **≤ 64 bp**. If your leader varies across
strains, add each variant as its own record — the search tries them in file
order and takes the first that matches a read.

```
>leader1
CTTTCGATCTCTTGTAGATCTGTTCTC
```

To find it, take the 5' end of the genome and locate the core TRS motif
(`ACGAAC` in SARS-CoV-2) shared with the body junctions; the leader is the
sequence ending at that motif. Include only what is genuinely shared — extra
genome-specific bases on either side cost you matches.

**3. TSS BED.** Tab-separated, 4 columns, one row per known junction:

```
chrom	start	end	name
MN908947.3	21553	21554	S
```

- `chrom` must match the FASTA record name exactly.
- `start` is the **0-based** position of the junction; `end` is `start + 1`.
- `name` is the ORF label used in the output tables.
- Duplicate `start` values are rejected.

Keep junctions further apart than `2 × --tss-window`, or their windows overlap
and the first matching row wins.

**Then run:**

```bash
sgRNAtor --reference    my_virus.fasta \
         --leader-fasta my_leaders.fasta \
         --tss-bed      my_junctions.bed \
         --threads      12 \
         --output-prefix out/sample \
         sample_1.fq.gz sample_2.fq.gz
```

You can mix and match — passing only `-b` keeps the bundled SARS-CoV-2 genome
and leader while swapping in your own junction set, which is the usual way to
test an alternative or extended annotation.

---

## Outputs

All files are prefixed with `--output-prefix`.

| File | Contents |
| --- | --- |
| `{prefix}_ORF_counts.txt` | `ORF  Start  Stop  Counts  CPMs` — one row per junction in the TSS BED, with its ± window bounds. |
| `{prefix}_sgRNA_counts.txt` | `Pos  Assigned  Counts  CPMs` — one row per observed template-switching site (1-based), with the ORF it was assigned to or `None` if noncanonical. |
| `{prefix}_read_assignments.txt` | `ORF  Reads` — comma-separated read IDs per ORF, plus an `unassigned` row. |
| `{prefix}_summary.txt` | `Library_Size`, `TRS_Found`, `Aligned`, `Canonical`, `Noncanonical`. |
| `{prefix}_sgRNA_R*.fastq.gz` | Leader-trimmed reads. |
| `{prefix}_aligned_sgRNA.bam` | BWA alignment of the trimmed reads. |
| `{prefix}_R1/R2.fastq.gz` (`{prefix}_SE.fastq.gz` for SE) | Adapter-trimmed reads from HTStream — the input to the leader search. |
| `{prefix}_stats.json`, `{prefix}.stdout/.stderr` | HTStream preprocessing logs. |

CPMs are counts per million of `Library_Size`, which is the number of
**fragments entering the leader search** — i.e. after HTStream adapter trimming
and the 15 bp length filter, and counted once per pair for PE input. It is not
the raw FASTQ read count.

---

## Notes and caveats

- **The bundled index is little-endian.** BWA writes `.bwt`/`.sa` in native
  byte order with no conversion on read, so the shipped index is valid on
  x86-64 and arm64 but not on a big-endian host. Re-run `bwa index` there.
- **Assignment is positional, not sequence-verified.** A site is called
  canonical purely because it falls inside a BED window, so leader-like motifs
  elsewhere in the genome can produce false positives. Treat the noncanonical
  bin as enriched for artefacts rather than as a discovery set.
- **`--threads` covers the leader search and BWA.** HTStream runs as a single
  fixed pipe, and quantification is single-threaded pysam.
- **Only leader-bearing fragments reach alignment.** `{prefix}_sgRNA_R*.fastq.gz`
  is not the full library; `Library_Size` in the summary is what the CPM
  denominator uses.

---

## Repository layout

```
src/sgRNAtor/
  main.py       CLI entry point and pipeline driver
  prepro.py     HTStream adapter trimming / length filtering
  search.py     Dual-strategy leader search (Myers bit-vector + Levenshtein DP)
  align.py      BWA MEM → samtools BAM
  quantify.py   BAM → template-switching sites → ORF assignment
  stats.py      Count tables and run summary
  utils.py      FASTA reader, gzip detection, revcomp, overlap, bundled() paths
  data/         Bundled SARS-CoV-2 references + BWA index — the -R/-L/-b defaults
scripts/        Usage templates and standalone helpers
  sgRNAQuant.py     Quantify from an existing BAM (skips search/alignment)
  ProcessBams.py    Pandas-based read-start counting around BED junctions
docs/           Workflow diagram, logo, notes
test/           Unit tests for the leader matchers (incl. fuzz vs. brute-force oracle)
```

## Tests

```bash
python3 test/test_myers.py
```

16 tests covering both match modes — exact hits, partial 5' overlaps at and
below `min_match`, substitutions and indels at the edit-budget boundary, and
three randomized fuzz tests that check `_myers_search`, `_suffix_prefix_overlap`,
and the combined `__myers_leader_search` against a brute-force Levenshtein
oracle. The file adds `src/` to `sys.path`, so it runs without installing the
package (Biopython is still required).
