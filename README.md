# spreadsheetlang
A Psi-inspired and spreadsheet-like esoteric programming language.

## Table Of Contents

* [Introduction](https://github.com/wompking/spreadsheetlang/#introduction)
* [Execution Model](https://github.com/wompking/spreadsheetlang/#execution-model)
* [Syntax](https://github.com/wompking/spreadsheetlang/#syntax)
* [Expressions and Operators](https://github.com/wompking/spreadsheetlang/#expressions-and-operators)
* [Examples](https://github.com/wompking/spreadsheetlang/#examples)

## Introduction
SPREADSHEET is a Psi-inspired and spreadsheet-like esolang. Like [Hat Trick](https://github.com/wompking/tailorlang), it is evaluated using RPN. File extensions for SPREADSHEET programs are `.sprd`, and SPREADSHEET comments begin with `//`. SPREADSHEET, unlike [Tailor](https://github.com/wompking/tailorlang), is not forgiving, but it basically never throws errors anyways.

## Execution Model
The SPREADSHEET execution model consists of a grid of formulas, like a spreadsheet. The grid is unbounded in all four directions, and is updated once every **tick**.
The formulas have a *command* attached to them, which is either `V`, `S`, `F`, or `I`.
* The `V` command takes an expression and evaluates it. 
* The `F` command takes two expressions, and sets the cell denoted by the first expression to a string containing a valid line of SPREADSHEET code.
* The `S` command sets the cell denoted by the first expression to a `V` command containing the evaluated value of the second expression.
* The `I` command takes input from the user.

All changes to cells are applied at the end of the tick, in the order the `V` and `S` commands were evaluated.
The grid is updated every in this way:

* Evaluate all cells with the `F` or `S` command first, with the distance from the center serving as the order, and counterclockwise angle as a tiebreaker.
  * If these cells depend on other cells that have not yet been evaluated this tick, evaluate those cells first.
* Apply the changes made by the `F` and `S` commands to the grid.
* If the cell `(0,0)` contains a value, output it to the user, and clear the cell.
* If the grid has not changed since the last tick, halt the program.

To reiterate, every cell in a SPREADSHEET program is only evaluated **once per tick**; thus, if two cells depend on one `I` command, the user will only be prompted for input once.
## Syntax
Every line of a SPREADSHEET program is of a specific format:

```
V<coordinate>: <expression>
S<coordinate>: <expression> <= <expression>
F<coordinate>: <expression> <= <expression>
I<coordinate>
```
The coordinate specifies where on the grid the command is.
SPREADSHEET has **four data types**, being the number, the string, the tuple (or complex number), and None:
```
Number: 10
Number: -10
Number: 10.5
NOT a Number: .5

String: "beans are cool!"
String: 'hello world'
NOT a string: "oops'
NOT a string: 'oops', i did it again'
String: 'yay,\' fixed now'

Tuple: (10,10)
Tuple: (1.3,-4)
Tuple: (1.963,100.37252)

None: None
```

## Expressions and Operators

The following is a table of operators in SPREADSHEET. If some behaviour is not specified for this table, it returns None.

| Operator | Arity | Function |
|----------|-------|----------|
| `+` | 2 | Performs addition between numbers/tuples, and concatenation between strings. |
| `-` | 2 | Performs subtraction between numbers/tuples. |
| `*` | 2 | Performs scalar/complex multiplication between numbers/tuples, and scalar vector multiplication between a number and a tuple. Additionally, `string number *` returns `string` repeated `number` times, like in Python. |
| `/` | 2 | Performs divison between numbers/tuples, and scalar vector division between a number and a tuple. |
| `#` | 1 | Absolute value of numbers, component-wise absolute value of tuples, length of strings. |
| `£` | 1 | Sign of numbers, component-wise sign of tuples. |
| `%` | 2 | Modulus between numbers, component-wise modulus between tuples. |
| `^` | 2 | Exponentiation between numbers; complex-type exponentiation between numbers and tuples is encouraged in your implementation, but I was too lazy to implement it here. |
| `?` | 3 | `A if C else B`. For this statement, use Python truthiness rules. C is evaluated first, and then only the required argument is evaluated. This is needed for proper control flow. |
| `=` | 2 | Python `==`. Returns 0 or 1. |
| `<`, `>`, `≤`, `≥`, `=` | 2 | Performs magnitude comparison. Takes in numbers, returns 0 or 1. |
| `~` | 1 | Shorthand for `1 x -` on only numbers. |
| `$` | 1 | Returns the value of the cell at the input tuple; evaluates it if needed. |
| `x`, `y` | 1 | Gets x-coordinate or y-coordinate of the input tuple. |
| `$` | 1 | Returns the value of the cell at the input tuple; evaluates it if needed. If the cell has no value, it returns `None`. |
| `C` | 2 | Coerces the type of `A` to the type of `B`; see table below. |
| `T` | 2 | Builds a tuple from two numbers. |
| `X` | 3 | Python `C[A:B]` for strings. |
| `@` | 0 | Gets the coordinates of this cell. |

Here is a table of values for the `C` operator:

| From | To | Value |
|----------|-------|----------|
| Number | Number | Self-explanatory. |
| Number | String | `"<number>"` |
| Number | Tuple | `(<number>,<number>)` |
| Number | None | `None` |
| String | Number | Parses string into a number, base 10. |
| String | String | Self-explanatory. |
| String | Tuple | Parses string into a tuple. |
| String | None | `None` |
| Tuple | Number | Gets the magnitude of the tuple. |
| Tuple | String | `"<tuple>"` |
| Tuple | Tuple | Self-explanatory. |
| Tuple | None | `None` |
| None | Number | `0` |
| None | String | `"None"` |
| None | Tuple | `(0,0)` |
| None | None | `None` |

## Examples

Here is a sample cat program:

```
I(0,1) //no equation
S(0,2): (0,0) <= (0,1) $
```

First, the `S` command evaluates. The first part of the `S` command is the position expression, which here is a single value and thus evaluates immediately. The second part of the command is the value expression, which here is a `$` operator called on a tuple. This gets the value at `(0,1)`, which has not been evaluated yet. Since this coordinate has an `I` command attached to it, it gets input from the user. When the user gives input, the command at `(0,1)` evaluates with a string. Then, since the value at `(0,1)` has evaluated, the `S` command at `(0,2)` evaluates. This sets the value at `(0,0)` to be whatever the user gave in. The program outputs what the user gave in, and then halts because no equations (apart from the one at `(0,0)`, which is ignored) have changed.
