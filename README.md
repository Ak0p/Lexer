## General Explanation  
This lexer works by reading an input file and tokenizing it into a list based off a **spec**.  The spec is a list of tuples, where each tuple is a pair of a token name and a regular expression.  
After reading the file, the lexer tokenizes it into a list of tuples, where each tuple is a pair of a token name and the value of the token.
## How to use  

Instantiate a `Lexer` object with the desired spec and call the `lex` method on the input file.  

