## General Explanation  
This lexer works by reading an input file and tokenizing it into a list based off a **spec**.  
The spec is a list of tuples, where each tuple is a pair of a token name and a regular expression.  
The lexer reads the input file and tokenizes it into a list of tuples, where each tuple is a pair of a token name and the value of the token.  
the lexer is used by changing the spec and calling the `lex` function on the input file.  

