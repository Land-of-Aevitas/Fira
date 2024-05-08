'''
Errors for the FiraScript interpreter.
'''

class FSError(Exception):
    '''Parent for all FiraScript errors.'''
class FSSyntaxError(FSError):
    '''Raised when the syntax of the FiraScript is incorrect.'''
class FSRecursionError(FSError):
    '''Raised when the recursion depth is too high.'''
