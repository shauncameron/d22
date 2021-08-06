# d22

---

d22 is a project inspired by the Avrae owned **[d20](https://d20.readthedocs.io/en/latest/start.html)** project made also in python. It was made in order to provide a better sense of customisability to another project: **[d22 Dice Roller App]()**. d22 differs in quite a few ways from d20 in terms of run time and features, however one of which is that d22 includes the use of assignment to an expression. This is something I  thought was paramount in deciding to implement my own language instead of using pre-made resources because it allows users to reference in-app names. Other key features are as below.

### Key Features

* Doesn't require complex set-up
* JSON to AST convertibility 
* Self-described lambda expressions 
* Assignment operations
* Hosted on `api.libnexus.com`

### Installation

* Made in python 3.9
* Supported by python 3.8+
* `python3 -m pip install -U d22` 

### Quick-start example

```python
>>> import d22
>>> result, error = d22.roll('4d6')
>>> if error:
...    print(error.printable())
... elif:
...     print(result.evalprintable())
...     print(result.plainprintable())
'<Sequence: (<Number: 1>, <Number: 3>, <Number: 3>, <Number: 5>)> = <Sequence: (<Number: 1>, <Number: 3>, <Number: 3>, <Number: 5>)>'
'4d6 = 1, 3, 3, 5'
```

### [Grammar]()

### [Tutorials]()



