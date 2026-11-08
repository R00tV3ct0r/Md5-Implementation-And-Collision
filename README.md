# MD5 Implementation and Collision Attacks

A personal Python implementation of MD5, together with experiments and research material I used to learn about hash collisions and practical collision techniques.

## MD5 Implementation

Calculate the MD5 hash of a string:

```bash
python Md5.py -s "Hello World!"
```

Calculate the MD5 hash of a file:

```bash
python Md5.py -f my_file.txt
```

Display available options:

```bash
python Md5.py --help
```

## Collision Attacks

### Suggested Learning Path

This is the order I recommend for discovering the subject and following the same path I took:

1. **Start with MD5 itself.** Try to re-implement the MD5 function using the sources listed below, or inspect my implementation in `Md5.py`.
2. **Understand the goals.** Learn the difference between a collision attack and a preimage attack.
3. **Try the simple search.** Try implementing a basic brute-force collision search, then compare your approach with `Collision_Attack/0_Brute_force.py`. Notice how storing previously seen hashes uses more and more memory.
4. **Reduce memory use.** Read about cycle detection, then implement `Collision_Attack/1_Floyd.py` and `Collision_Attack/2_Brent.py`. These approaches use constant memory, trading some additional computation for the reduced memory use.
5. **Explore the Xiaoyun Wang and Hongbo Yu research.** Read `3_How to Break MD5 and Other Hash Functions.pdf`. Work through the mathematical reasoning to understand how the attacks work.
6. **Continue with M.M.J. Stevens paper.** Read `4_On Collisions for MD5 - M.M.J. Stevens.pdf` to learn more about MD5 collisions. If you are short on time, focus on the main ideas rather than working through every derivation.
7. **Explore existing examples.** Experiment with the [universal-pdf-md5-collision repository](https://github.com/adrien1018/universal-pdf-md5-collision) to see how the PDF collision technique works in practice, and check out the early example in [PoC||GTFO 0x14](https://security-bits.de/pocgtfo/pocorgtfo14.pdf).
8. **Learn about the PDF format.** Use the [PDF structure diagram](https://github.com/corkami/pics/blob/master/binary/PDF.png) and [this introduction to PDF files](https://medium.com/@jberkenbilt/the-structure-of-a-pdf-file-6f08114a58f6) to understand how PDFs are structured.
9. **Implement the final script yourself.** Use the supplied `collisions-1` and `collisions-2` blocks to build your own version of `Collision_Attack/5_MD5_IN_PDF.py`.

To run the PDF example, first install `pypdf` and the `qpdf` command-line tool. From the repository root, run:

```bash
cd Collision_Attack
python 5_MD5_IN_PDF.py input.pdf -o output.pdf
```

The script also accepts `--posx`, `--posy`, and `--color` options. Run `python 5_MD5_IN_PDF.py --help` for details. Run it from `Collision_Attack/` so it can find the supplied collision-block files.

As you go, consider: What counts as a collision? Why does storing every result cost memory? How does cycle detection trade computation for memory? What is different about the generic search scripts and the attacks described in the research papers?

### What's Included

The `Collision_Attack/` directory contains the scripts and research material for these steps:

- `0_Brute_force.py` — basic brute-force collision implementation.
- `1_Floyd.py` — collision search using Floyd's cycle-finding algorithm to reduce memory use.
- `2_Brent.py` — collision search using Brent's cycle-finding algorithm, an alternative to Floyd's method.
- `3_How to Break MD5 and Other Hash Functions.pdf` — a research paper on attacks against MD5 and other hash functions.
- `4_On Collisions for MD5 - M.M.J. Stevens.pdf` — a research paper by Marc Stevens about MD5 collisions.
- `5_MD5_IN_PDF.py` — an example involving MD5 collisions in PDF files, based on the work of [Adrien Wu](https://github.com/adrien1018/universal-pdf-md5-collision).
- `collisions-1` / `collisions-2` — files used for the PDF collision.

**Important:** The brute-force, Floyd, and Brent scripts search for collisions on a truncated hash prefix (32 bits by default), not collisions between complete 128-bit MD5 digests. They demonstrate generic collision-search strategies and are separate from the differential cryptanalysis techniques described in the research papers. This repository is an educational exploration, not a practical full-MD5 collision generator. MD5 is cryptographically broken and should not be used where security or collision resistance is required.

## Sources

- [MD5 Explained – YouTube](https://www.youtube.com/watch?v=5MiMK45gkTY)
- [MD5 – Wikipedia](https://en.wikipedia.org/wiki/MD5)
- *How to Break MD5 and Other Hash Functions* — included in `Collision_Attack/`.
- *On Collisions for MD5* — Marc Stevens, included in `Collision_Attack/`.
- [universal-pdf-md5-collision](https://github.com/adrien1018/universal-pdf-md5-collision)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
