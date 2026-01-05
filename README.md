# beancount GIC

A script that automatically calculates and inserts the future date for a GIC investment in [beancount](https://github.com/beancount/beancount/).

## Get Started

Download the `GIC.py` script into the same directory as your beancount file. Then insert the following lines to the top of your beancount file:
```
option "insert_pythonpath" "True"
plugin "GIC"
```

And you're done!

## Example

`2022-11-29 custom "GIC" Assets:GIC:Flexible Assets:BANK:Chequing Income:GIC:Interest 5000 CAD 4.5 12`

turns into:

```
2022-11-29 open Assets:GIC:Flexible

2022-11-29 *
 Assets:GIC:Flexible 5000 CAD
 Assets:BANK:Chequing

2023-11-29 *
 Assets:BANK:Chequing 5225 CAD
 Assets:GIC:Flexible -5000 CAD
 Income:GIC:Interest

2023-11-29 close Assets:GIC:Flexible
 
```

