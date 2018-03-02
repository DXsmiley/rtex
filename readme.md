# rTeX

[Deployed example here](http://rtex.probablyaweb.site/)

Minimal LaTeX rendering server.

Requirements:
- Python 3.5.2
- The libraries in `requirements.txt`
- An installation of LaTeX, of some description.
	- MikTeX and TeXLive both work decently.
- A command called `convert`. I think it's part of imagemagik but I'm not sure.

## Security Concerns

The following settings should be applied to your `texmf.cnf` file in order to prevent security breaches:

```
shell_escape = f
parse_first_line = f
openout_any = p
openin_any = p
```

More details [here](https://tex.stackexchange.com/questions/10418/how-can-i-safely-compile-other-peoples-latex-documents).
